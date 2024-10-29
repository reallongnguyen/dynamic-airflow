from airflow.decorators import dag
from pendulum import datetime
from datetime import timedelta

from dynamic.user_interface.adapter.tasks.test_and_build import test_and_build
from dynamic.user_interface.adapter.tasks.extract import extract
from dynamic.user_interface.adapter.tasks.transform import transform
from dynamic.user_interface.adapter.tasks.check_quality import check_quality
from dynamic.user_interface.adapter.tasks.load import delta_load
from dynamic.user_interface.adapter.tasks.trigger import trigger


def create_dag(source):
    dag_id = source["dag"]["id"]
    schedule = source["dag"]["schedule"]
    dag_disp_name = (
        source["dag"]["disp_name"] if "disp_name" in source["dag"] else dag_id
    )

    default_args = {
        "owner": "airflow",
        "start_date": datetime(2024, 10, 24, tz="UTC"),
        "retries": source["dag"]["retries"],
        "retry_delay": timedelta(minutes=3),
    }

    @dag(
        dag_id=dag_id,
        schedule=schedule,
        default_args=default_args,
        catchup=False,
        dag_display_name=dag_disp_name,
        params={"source": source},
    )
    def extract_dag():
        (
            test_and_build()
            >> extract()
            >> transform()
            >> check_quality()
            >> delta_load()
            >> trigger()
        )

    generated_dag = extract_dag()

    return generated_dag
