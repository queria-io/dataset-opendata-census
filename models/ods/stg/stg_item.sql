select
    cast(item_no as integer) as item_no,
    item_key,
    item_label,
    definition_book,
    search_words
from {{ ref('raw_item') }}
