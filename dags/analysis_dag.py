from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from transformers import pipeline
import os
from transformers import pipeline

PROCESSED_DIR = "/opt/airflow/data/processed/"
ANALYSIS_DIR = "/opt/airflow/data/analysis/"
os.makedirs(ANALYSIS_DIR, exist_ok=True)

# Define the sentiment analysis pipeline with truncation enabled
sentiment_analyzer = pipeline("sentiment-analysis", truncation=True)


# Visualization function
def generate_visualizations(**kwargs):
    files = [f for f in os.listdir(PROCESSED_DIR) if f.startswith('video_data_processed')]
    if not files:
        raise FileNotFoundError("No processed data file found.")
    
    latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(PROCESSED_DIR, f)))
    video_df = pd.read_csv(os.path.join(PROCESSED_DIR, latest_file))

    # Best-performing videos
    plt.figure(figsize=(10, 6))
    top_videos = video_df.sort_values('viewCount', ascending=False).head(10)
    sns.barplot(x='title', y='viewCount', data=top_videos)
    plt.xticks(rotation=90)
    plt.title("Top 10 Videos by View Count")
    plt.tight_layout()
    plt.savefig(os.path.join(ANALYSIS_DIR, "top_videos.png"))

    # Word cloud for titles
    titles = ' '.join(video_df['title'].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(titles)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title("Word Cloud for Video Titles")
    plt.tight_layout()
    plt.savefig(os.path.join(ANALYSIS_DIR, "word_cloud.png"))

    return "Visualizations generated and saved."

# NLP Analysis function
def analyze_sentiments(ti, **kwargs):
    # Pull the file path from XCom
    processed_file_path = ti.xcom_pull(
        key='processed_file_path',
        task_ids='preprocess_video_data',
        dag_id='preprocessing_dag'  # Ensure the DAG ID matches exactly
    )

    if not processed_file_path:
        raise FileNotFoundError("No processed file path found in XCom.")

    # Load processed data
    video_df = pd.read_csv(processed_file_path)

    # Perform sentiment analysis
    sentiment_analyzer = pipeline("sentiment-analysis", truncation=True)
    video_df['descriptionSentiment'] = video_df['description'].apply(
        lambda desc: sentiment_analyzer(desc[:512])[0]['label'] if pd.notnull(desc) else 'NEUTRAL'
    )

    # Save results
    sentiment_output_path = os.path.join(ANALYSIS_DIR, "sentiment_analysis.csv")
    video_df.to_csv(sentiment_output_path, index=False)
    return sentiment_output_path


# Define DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'analysis_dag',
    default_args=default_args,
    description='Analyze processed YouTube data',
    schedule_interval=None,
    start_date=datetime(2023, 12, 10),
    catchup=False,
) as dag:

    visualization_task = PythonOperator(
        task_id='generate_visualizations',
        python_callable=generate_visualizations,
        provide_context=True,
    )

    sentiment_analysis_task = PythonOperator(
        task_id='analyze_sentiments',
        python_callable=analyze_sentiments,
        provide_context=True,  # This allows passing `ti` (task instance)
    )

    visualization_task >> sentiment_analysis_task
