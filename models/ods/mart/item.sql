select
    item_no,
    item_key,
    item_label,
    definition_book,
    search_words
from {{ ref('stg_item') }}
