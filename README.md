# YouTube Data Analysis with Airflow

## Overview
This project uses Airflow to process YouTube video data, perform sentiment analysis on video descriptions, and generate visualizations based on the collected data.

## Project Structure
- `dags/`: Contains Airflow DAGs to preprocess data and perform analysis.
- `data/`: Directory for storing scraped data, processed data, and analysis results.
- `logs/`: Airflow logs.
- `config/`: Configuration files (e.g., Airflow settings, etc.).
  
## Requirements
- Python 3.x
- Apache Airflow 2.x
- Required Python packages (listed in `requirements.txt`)

## Setup Instructions

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Start Airflow**:
    - If using Docker:
      ```bash
      docker-compose up
      ```
    - If using local installation, start the Airflow webserver and scheduler:
      ```bash
      airflow webserver -p 8080
      airflow scheduler
      ```

4. **Run DAGs**: Trigger the DAGs either manually or on a schedule using Airflow’s UI.

## Contributing
Feel free to fork this repository, submit issues, and create pull requests. Make sure to add tests and documentation for any changes you make.

