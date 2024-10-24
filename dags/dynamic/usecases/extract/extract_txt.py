from dynamic.ports.source_airflow_variable import get

def extract(source_id: str):
  source = get(source_id)

  print("Extract txt with config", source["extract"]["config"])
