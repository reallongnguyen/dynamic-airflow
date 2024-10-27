MERGE
            `{{ dataset }}.{{ data_table }}` AS data
        USING
        (
            WITH no_dup AS (
                SELECT
                    *,
                    ROW_NUMBER() OVER(
                        PARTITION BY id
                        ORDER BY created_at DESC
                    ) AS rn
                FROM `{{ dataset }}.{{ stg_table }}`
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
