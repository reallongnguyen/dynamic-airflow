from airflow.decorators import dag, task
import importlib
from pendulum import datetime
from datetime import timedelta

def create_dag(source):
    dag_id = source["dag"]["id"]
    schedule = source["dag"]["schedule"]
    dag_disp_name = source["dag"]["disp_name"] if "disp_name" in source["dag"] else dag_id
    default_args = {
      "owner": "airflow",
      "start_date": datetime(2024, 10, 24, tz="UTC"),
      "retries": source["dag"]["retries"],
      "retry_delay": timedelta(minutes=3)
    }

    @dag(dag_id=dag_id, schedule=schedule, default_args=default_args, catchup=False, dag_display_name=dag_disp_name, params={ "source": source })
    def extract_dag():
        @task()
        def test_and_build(**kwargs):
            print("Test and build")

        @task()
        def extract(**kwargs):
          src = kwargs["params"]["source"]

          print("Extract", src)
          usecase_pkg = "dynamic.usecases"
          extract_mod_name = f"{usecase_pkg}.{src["extract"]["module_name"]}"

          extract_mod = importlib.import_module(name=extract_mod_name)
          extract_mod.extract(src["id"])

        @task()
        def normalize(**kwargs):
          print("Normalize")

        @task()
        def transform(**kwargs):
          print("Transform")

        @task()
        def check_quality(**kwargs):
          print("Check quality")

        @task()
        def delta_load(**kwargs):
          print("Delta load")

        @task()
        def trigger(**kwargs):
          print("Trigger")

        test_and_build() >> extract() >> normalize() >> transform() >> check_quality() >> delta_load() >> trigger()

    generated_dag = extract_dag()

    return generated_dag
