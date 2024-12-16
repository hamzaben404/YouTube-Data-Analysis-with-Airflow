# **YouTube Data Analysis with Airflow**

## **Overview**
This project demonstrates the use of Apache Airflow to build a scalable data pipeline for processing YouTube video data. The pipeline automates tasks such as scraping data, preprocessing it, performing sentiment analysis on video descriptions, and generating insightful visualizations.

### **Features**
- Automated scraping of YouTube video data.
- Data preprocessing to clean and standardize data.
- Sentiment analysis using the Hugging Face Transformers library.
- Visualizations of key metrics such as top videos by view count and word clouds of video titles.
- Full pipeline orchestration using Apache Airflow.

## **Project Structure**
```
project/
├── dags/
│   ├── analysis_dag.py          # DAG for sentiment analysis and visualizations
│   ├── preprocessing_dag.py     # DAG for data preprocessing
├── data/
│   ├── scraping/                # Raw scraped data
│   ├── processed/               # Processed data
│   ├── analysis/                # Analysis outputs (e.g., charts, sentiment results)
├── logs/                        # Airflow logs
├── config/                      # Configuration files (e.g., Airflow, environment variables)
├── report.pdf                   # Detailed project report
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## **Requirements**
- Python 3.8 or higher
- Apache Airflow 2.x
- Docker (optional, for containerized setup)
- Required Python packages (listed in `requirements.txt`)

## **Setup Instructions**

### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
```

### **2. Install Dependencies**
Install the necessary Python packages:
```bash
pip install -r requirements.txt
```

### **3. Set Up Airflow**
#### **Option A: Using Docker Compose**
1. Make sure Docker is installed on your machine.
2. Start Airflow using Docker Compose:
   ```bash
   docker-compose up
   ```
3. Access the Airflow web interface at [http://localhost:8080](http://localhost:8080).

#### **Option B: Local Installation**
1. Initialize Airflow:
   ```bash
   airflow db init
   ```
2. Start the Airflow webserver:
   ```bash
   airflow webserver -p 8080
   ```
3. Start the Airflow scheduler in another terminal:
   ```bash
   airflow scheduler
   ```

### **4. Configure Airflow Connections**
Ensure that all necessary Airflow connections (e.g., API keys, database connections) are configured in the Airflow UI under "Admin > Connections."

### **5. Run DAGs**
- Trigger the `preprocessing_dag` to process raw scraped YouTube data.
- Once preprocessing is complete, the `analysis_dag` will automatically execute (or can be manually triggered) to perform sentiment analysis and generate visualizations.

## **Outputs**
- **Processed Data**: Stored in the `data/processed/` directory.
- **Sentiment Analysis Results**: Stored as a CSV file in the `data/analysis/` directory.
- **Visualizations**: Charts and word clouds saved in the `data/analysis/` directory.

## **Challenges Overcome**
- **Handling Missing Data**: Used robust data cleaning techniques in the preprocessing step.
- **Sentiment Analysis**: Truncated video descriptions to avoid token length errors in Hugging Face models.
- **XCom Issues**: Ensured proper data passing between tasks in Airflow DAGs by explicitly managing file paths.

## **Future Enhancements**
- Extend analysis to include metrics like comment sentiment and engagement rates.
- Implement periodic scheduling to keep data and visualizations updated.
- Incorporate advanced NLP models for deeper insights.
- Optimize pipeline performance and reduce DAG complexity.

## **Contributing**
We welcome contributions to enhance the project! To contribute:
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your message here"
   ```
4. Push your branch and submit a pull request.