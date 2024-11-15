from airflow.decorators import task
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook


@task()
def test_and_build(**kwargs):
    source = kwargs["params"]["source"]
    tables = source["tables"]
    schema_fields = source["schema_fields"]

    bq_hook = BigQueryHook()

    print(f"create tables if not exists {tables}")

    for table in tables:
        dataset = table["dataset"]
        table_name = table["name"]
        table_type = table["type"]
        time_partitioning = ({"field": table["partition_field"], "type": "DAY"}
                             if "partition_field" in table else None)

        print(f"create dataset if not exist {dataset}")

        bq_hook.create_empty_dataset(
            dataset_id=dataset,
            exists_ok=True,
        )

        table_schema_fields = list(schema_fields.values())

        if table_type == "load":
            table_schema_fields.append({
                "name": "ingestion_ts",
                "type": "TIMESTAMP",
                "mode": "REQUIRED",
            })

        print(
            f"""
                create table if not exist {table_name}
                with schema
                {table_schema_fields}
            """
        )

        bq_hook.create_empty_table(
            dataset_id=dataset,
            table_id=table_name,
            schema_fields=table_schema_fields,
            exists_ok=True,
            time_partitioning=time_partitioning,
        )
