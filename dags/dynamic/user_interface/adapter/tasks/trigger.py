from airflow.decorators import task


@task()
def trigger(**kwargs):
    print("Trigger")
