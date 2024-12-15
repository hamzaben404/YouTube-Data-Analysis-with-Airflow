from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import os
import isodate
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

# Paths
SCRAPED_DIR = "/opt/airflow/data/scraping/"
PROCESSED_DIR = "/opt/airflow/data/processed/"
os.makedirs(PROCESSED_DIR, exist_ok=True)


# Preprocess scraped data
def preprocess_video_data(**kwargs):
    # Load the most recent scraped video details file
    files = [f for f in os.listdir(SCRAPED_DIR) if f.startswith("video_details")]
    if not files:
        raise FileNotFoundError("No video details file found in the scraped directory.")

    latest_file = max(
        files, key=lambda f: os.path.getctime(os.path.join(SCRAPED_DIR, f))
    )
    video_df = pd.read_csv(os.path.join(SCRAPED_DIR, latest_file))

    # Handle missing values
    video_df.fillna({"viewCount": 0, "likeCount": 0, "commentCount": 0}, inplace=True)

    # Handle 'tags' column gracefully
    if "tags" in video_df.columns:
        video_df["tags"] = video_df["tags"].fillna("")
        video_df["tagCount"] = video_df["tags"].apply(
            lambda x: len(x.split(",")) if isinstance(x, str) else 0
        )
    else:
        video_df["tagCount"] = 0  # Default to 0 if 'tags' column is missing

    # Handle 'publishedAt' column gracefully
    if "publishedAt" in video_df.columns:
        video_df["publishedAt"] = pd.to_datetime(
            video_df["publishedAt"], errors="coerce"
        )
        video_df["publishDayName"] = video_df["publishedAt"].dt.day_name()
    else:
        video_df["publishedAt"] = pd.NaT
        video_df["publishDayName"] = "Unknown"

    # Convert 'duration' to seconds
    video_df["durationSecs"] = video_df["duration"].apply(
        lambda x: isodate.parse_duration(x).total_seconds() if pd.notnull(x) else 0
    )

    # Save processed data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    processed_file_path = os.path.join(PROCESSED_DIR, f"video_data_processed_{timestamp}.csv")
    video_df.to_csv(processed_file_path, index=False)

    # Push file path to XCom
    ti = kwargs['ti']
    ti.xcom_push(key='processed_file_path', value=processed_file_path)
    return processed_file_path  # Optional for debug purposes



# Define the DAG
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "preprocessing_dag",
    default_args=default_args,
    description="Preprocess Scraped YouTube Data",
    schedule_interval=None,
    start_date=datetime(2023, 12, 10),
    catchup=False,
) as dag:
    preprocess_video_task = PythonOperator(
        task_id='preprocess_video_data',
        python_callable=preprocess_video_data,
        provide_context=True,
    )

    trigger_analysis_task = TriggerDagRunOperator(
        task_id='trigger_analysis_dag',
        trigger_dag_id='analysis_dag',
    )

    preprocess_video_task >> trigger_analysis_task

