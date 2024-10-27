from airflow.decorators import task


@task()
def check_quality(**kwargs):
    print("Check quality")
