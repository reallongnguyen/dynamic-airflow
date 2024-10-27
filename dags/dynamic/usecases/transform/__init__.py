from airflow.decorators import task


@task()
def transform(**kwargs):
    print("Transform")
