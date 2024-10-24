from dynamic.core import create_dag
from dynamic.ports.source_airflow_variable import list as source_list

sources = source_list()

for source in sources.values():
  dag_id = source["dag"]["id"]

  globals()[dag_id] = create_dag(source=source)
