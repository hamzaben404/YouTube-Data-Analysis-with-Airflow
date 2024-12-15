# Use the official Airflow image as a base
FROM apache/airflow:2.10.3

# Switch to root user to have permissions to install packages
USER root

# Install required build tools and libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    libffi-dev \
    libpq-dev \
    libsasl2-dev \
    libldap2-dev \
    && apt-get clean

# Copy the requirements.txt to the container
ADD requirements.txt .

# Switch back to the airflow user before running pip install
USER ${AIRFLOW_UID:-50000}

# Install the necessary Python packages, including Airflow dependencies and additional packages
RUN pip install apache-airflow==2.10.3 -r requirements.txt
