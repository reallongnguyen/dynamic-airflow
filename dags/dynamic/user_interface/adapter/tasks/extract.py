from airflow.decorators import task
import importlib

@task()
def extract(**kwargs):
    src = kwargs["params"]["source"]

    print("Extract", src)
    usecase_pkg = "dynamic.domain.usecases"
    extract_mod_name = f"{usecase_pkg}.{src["extract"]["module_name"]}"

    extract_mod = importlib.import_module(name=extract_mod_name)
    extract_mod.extract(kwargs)
