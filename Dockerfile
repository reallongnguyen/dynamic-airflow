FROM apache/airflow:2.9.3

USER airflow

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
