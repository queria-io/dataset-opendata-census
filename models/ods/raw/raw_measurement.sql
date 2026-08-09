{# 団体 × 項目の観測結果の生データ。census.py が data/measurement.ndjson に書く。 #}

{{ config(materialized='table') }}

select *
from read_json(
    'data/measurement.ndjson',
    format = 'newline_delimited',
    columns = {
        'portal_id': 'VARCHAR',
        'lg_code': 'VARCHAR',
        'item_no': 'VARCHAR',
        'item_key': 'VARCHAR',
        'is_published': 'VARCHAR',
        'dataset_count': 'VARCHAR',
        'measured_on': 'VARCHAR'
    }
)
