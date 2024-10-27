from airflow.decorators import task


@task()
def delta_load(**kwargs):
    print("Delta load")
