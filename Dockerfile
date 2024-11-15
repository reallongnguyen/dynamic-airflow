FROM apache/airflow:2.9.3

USER airflow

COPY setup.py setup.py
RUN pip install -e .
