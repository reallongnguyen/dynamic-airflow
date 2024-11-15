from airflow.providers.google.cloud.hooks.gcs import GCSHook

from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import (
    GCSToBigQueryOperator,
)
import json
from pendulum import DateTime


def extract(kwargs):
    source = kwargs["params"]["source"]
    extract_config = source["extract"]["config"]
    schema_fields = source["schema_fields"]
    tables = source["tables"]

    data_interval_start: DateTime = kwargs["data_interval_start"]
    data_interval_end: DateTime = kwargs["data_interval_end"]

    match_glob_map = {"csv": "**/*.csv"}

    bucket_name = extract_config["bucket"]
    prefix = extract_config["prefix"]
    match_glob = (
        match_glob_map[extract_config["file_format"]]
        if extract_config["file_format"] in match_glob_map else None
    )
    load_table = extract_config["dst_table"]
    dataset: str | None = None
    load_table_type: str
    unique_id = kwargs["ts_nodash"]
    stg_table = f"{load_table}_{unique_id}"
    stg_table_scheme_fields = []

    for column_name in extract_config["column_order"]:
        if column_name in schema_fields:
            stg_table_scheme_fields.append(schema_fields[column_name])
        else:
            print(
                f"""column {column_name} was defined in column_order
                but not found in schema_fields"""
            )

    for table in tables:
        if table["name"] == load_table:
            dataset = table["dataset"]
            load_table_type = table["type"]

    if dataset is None:
        print(f"not found load table {load_table} in table config")
        return

    if load_table_type != "load":
        print(f"unexpected table type {load_table_type}. Required load table")
        return

    foot_print = json.dumps({
        "bucket_name": bucket_name,
        "prefix": prefix,
        "match_glob": match_glob,
        "timespan_start": data_interval_start.to_datetime_string(),
        "timespan_end": data_interval_end.to_datetime_string(),
    })

    print(f"[GCS] extract files with config {foot_print}")

    gcs_hook = GCSHook()

    files = gcs_hook.list_by_timespan(
        bucket_name=bucket_name,
        prefix=prefix,
        timespan_start=data_interval_start,
        timespan_end=data_interval_end,
        match_glob=match_glob,
    )

    print(f"[GCS] list file: {files}")

    if len(files) == 0:
        return

    print(
        "[BQ] load gcs to bq with config",
        json.dumps({
            "files": json.dumps(files),
            "dataset_table": f"{dataset}.{stg_table}",
            "stg_table_scheme_fields": json.dumps(stg_table_scheme_fields),
        }),
    )

    # load gcs file to staging
    GCSToBigQueryOperator(
        task_id="load_gcs_to_bq",
        bucket=bucket_name,
        source_objects=files,
        destination_project_dataset_table=f"{dataset}.{stg_table}",
        schema_fields=stg_table_scheme_fields,
        write_disposition="WRITE_TRUNCATE",
    ).execute(kwargs)

    bq_hook = BigQueryHook()

    ts = kwargs["ts"]

    delete_sql = f"""
        DELETE FROM
            `{dataset}.{load_table}`
        WHERE ingestion_ts = TIMESTAMP('{ts}')
    """

    print(f"[BQ] delete records have same ingestion_ts: {delete_sql}")

    bq_hook.insert_job(
        configuration={"query": {
            "query": delete_sql,
            "useLegacySql": False,
        }},
    )

    # merge staging to load
    load_columns = []
    staging_columns = []

    for column in schema_fields.values():
        load_columns.append(column["name"])
        staging_columns.append(column["name"])

    load_columns.append("ingestion_ts")
    staging_columns.append(f"TIMESTAMP('{ts}') AS ingestion_ts")

    load_columns_str = ", ".join(load_columns)
    staging_columns_str = ", ".join(staging_columns)

    insert_sql = f"""
        INSERT INTO
            `{dataset}.{load_table}`
        (
            {load_columns_str}
        )
        SELECT
            {staging_columns_str}
        FROM
            `{dataset}.{stg_table}`
    """

    print(f"[BQ] insert data to load table: {insert_sql}")

    bq_hook.insert_job(
        configuration={"query": {
            "query": insert_sql,
            "useLegacySql": False,
        }},
    )
