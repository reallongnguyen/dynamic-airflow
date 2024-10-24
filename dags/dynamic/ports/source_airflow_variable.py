from airflow.models import Variable

key = "source"

def list():
  return Variable.get(key=key, default_var={}, deserialize_json=True)

def get(id: str):
  all_dags = Variable.get(key=key, default_var={}, deserialize_json=True)

  return all_dags[id] if id in all_dags else None
