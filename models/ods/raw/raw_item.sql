{# 自治体標準ODS 31項目の定義。census.py が items.py から data/item.ndjson に書く。 #}

{{ config(materialized='table') }}

select *
from read_json(
    'data/item.ndjson',
    format = 'newline_delimited',
    columns = {
        'item_no': 'VARCHAR',
        'item_key': 'VARCHAR',
        'item_label': 'VARCHAR',
        'definition_book': 'VARCHAR',
        'search_words': 'VARCHAR'
    }
)
