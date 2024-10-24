from pendulum import datetime
from dynamic.core import create_dag

for i in range(8):
  dag_id = f"hello_{i}"
  default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 10, 24, tz="UTC"),
    "retries": 3,
  }

  globals()[dag_id] = create_dag(dag_id=dag_id, schedule='*/5 * * * *', dag_number=i, default_args=default_args)
