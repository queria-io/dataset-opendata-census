{# 検索語ごとのヒット数。判定の根拠を利用者が検証できるように残す。 #}

{{ config(materialized='table') }}

select *
from read_json(
    'data/word_hit.ndjson',
    format = 'newline_delimited',
    columns = {
        'portal_id': 'VARCHAR',
        'item_no': 'VARCHAR',
        'item_key': 'VARCHAR',
        'search_word': 'VARCHAR',
        'dataset_count': 'VARCHAR',
        'status': 'VARCHAR',
        'measured_on': 'VARCHAR'
    }
)
