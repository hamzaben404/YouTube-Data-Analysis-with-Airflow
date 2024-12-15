from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import pandas as pd
import os

# YouTube API setup
API_KEY = 'AIzaSyAxs7uzwcGOqJftvR_p9gqZ2nT6KmwtKj4'
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Paths
OUTPUT_DIR = "/opt/airflow/data/scraping/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fetch channel stats
def fetch_channel_stats(channel_ids):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_ids)
    )
    response = request.execute()

    all_data = []
    for item in response['items']:
        data = {
            'channelName': item['snippet']['title'],
            'subscribers': item['statistics']['subscriberCount'],
            'views': item['statistics']['viewCount'],
            'totalVideos': item['statistics']['videoCount'],
            'playlistId': item['contentDetails']['relatedPlaylists']['uploads']
        }
        all_data.append(data)

    df = pd.DataFrame(all_data)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(f"{OUTPUT_DIR}channel_stats_{timestamp}.csv", index=False)
    return f"Channel stats saved at {OUTPUT_DIR}"

# Fetch video IDs from playlist
def fetch_video_ids(playlist_id, **kwargs):
    video_ids = []
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()

    for item in response['items']:
        video_ids.append(item['contentDetails']['videoId'])

    next_page_token = response.get('nextPageToken')
    while next_page_token is not None:
        request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = response.get('nextPageToken')
    
    # Push the video_ids to XCom
    kwargs['ti'].xcom_push(key='video_ids', value=video_ids)
    # Save video IDs locally
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pd.DataFrame(video_ids, columns=['video_id']).to_csv(
        f"{OUTPUT_DIR}video_ids_{timestamp}.csv", index=False
    )
    return f"{len(video_ids)} video IDs saved at {OUTPUT_DIR}"

# Fetch video details
def fetch_video_details(youtube, **kwargs):
    video_ids = kwargs['ti'].xcom_pull(task_ids='scrape_video_ids', key='video_ids')  # Pull video_ids from XCom

    all_video_info = []
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(video_ids[i:i+50])
        )
        response = request.execute()

        for video in response['items']:
            video_info = {
                'video_id': video['id'],
                'title': video['snippet']['title'],
                'description': video['snippet']['description'],
                'viewCount': video['statistics'].get('viewCount'),
                'likeCount': video['statistics'].get('likeCount'),
                'commentCount': video['statistics'].get('commentCount'),
                'duration': video['contentDetails']['duration']
            }
            all_video_info.append(video_info)

    # Save video details locally
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pd.DataFrame(all_video_info).to_csv(
        f"{OUTPUT_DIR}video_details_{timestamp}.csv", index=False
    )
    return f"Video details saved at {OUTPUT_DIR}"

# Define the DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
with DAG(
    'scraping_dag',
    default_args=default_args,
    description='Scrape YouTube Data',
    schedule_interval='@daily',
    start_date=datetime(2023, 12, 10),
    catchup=False,
) as dag:
    # Tasks
    scrape_channel_stats = PythonOperator(
        task_id='scrape_channel_stats',
        python_callable=fetch_channel_stats,
        op_args=[['UCoOae5nYA7VqaXzerajD0lg']],
    )
    scrape_video_ids = PythonOperator(
        task_id='scrape_video_ids',
        python_callable=fetch_video_ids,
        op_args=['UUoOae5nYA7VqaXzerajD0lg'],
        provide_context=True,  # Allow passing context to the function
    )
    scrape_video_details = PythonOperator(
        task_id='scrape_video_details',
        python_callable=fetch_video_details,
        op_args=[youtube],
        provide_context=True,  # Allow passing context to the function
    )

    # Task dependencies
    scrape_channel_stats >> scrape_video_ids >> scrape_video_details
