from airflow.providers.google.cloud.hooks.gcs import GCSHook

from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import (
    GCSToBigQueryOperator,
)
import json
from pendulum import DateTime


def extract(kwargs):
    data_interval_start: DateTime = kwargs['data_interval_start']
    data_interval_end: DateTime = kwargs['data_interval_end']

    bucket_name = 'isling-data'
    prefix = 'vn/comments'
    match_glob = '**/*.csv'

    dataset = 'isling_data'
    unique_id = kwargs['ts_nodash']
    stg_table = f"comments_{unique_id}"
    data_table = 'comments'

    foot_print = json.dumps({
        'bucket_name': bucket_name,
        'prefix': prefix,
        'match_glob': match_glob,
        'timespan_start': data_interval_start.to_datetime_string(),
        'timespan_end': data_interval_end.to_datetime_string(),
    })

    print(f"extract files from {foot_print}")

    gcs_hook = GCSHook()

    files = gcs_hook.list_by_timespan(
        bucket_name=bucket_name,
        prefix=prefix,
        timespan_start=data_interval_start,
        timespan_end=data_interval_end,
        match_glob=match_glob,
    )

    print(f"list file: {files}")

    if len(files) == 0:
        return

    GCSToBigQueryOperator(
        task_id='gcs_to_bq',
        bucket=bucket_name,
        source_objects=files,
        destination_project_dataset_table=f"{dataset}.{stg_table}",
        schema_fields=[
            {'name': 'id', 'type': 'STRING', 'mode': 'REQUIRED'},
            {'name': 'user_id', 'type': 'STRING', 'mode': 'REQUIRED'},
            {'name': 'comment', 'type': 'STRING', 'mode': 'REQUIRED'},
            {
                'name': 'created_at',
                'type': 'TIMESTAMP',
                'mode': 'REQUIRED',
            },
        ],
        write_disposition='WRITE_TRUNCATE',
    ).execute(kwargs)

    bq_hook = BigQueryHook()

    sql = f"""
        MERGE
            `{dataset}.{data_table}` AS data
        USING
        (
            WITH no_dup AS (
                SELECT
                    *,
                    ROW_NUMBER() OVER(
                        PARTITION BY id
                        ORDER BY created_at DESC
                    ) AS rn
                FROM `{dataset}.{stg_table}`
            )
            SELECT
                * EXCEPT(rn)
            FROM no_dup
            WHERE
                rn = 1
        ) AS stg
        ON
            data.id = stg.id
        WHEN MATCHED THEN UPDATE SET
            user_id = stg.user_id,
            comment = stg.comment,
            created_at = stg.created_at
        WHEN NOT MATCHED BY TARGET
        THEN
        INSERT
            (
                id,
                user_id,
                comment,
                created_at
            )
        VALUES
            ( stg.id, stg.user_id, stg.comment, stg.created_at )
    """

    bq_hook.insert_job(
        configuration={'query': {
            'query': sql,
            'useLegacySql': False,
        }},
    )
