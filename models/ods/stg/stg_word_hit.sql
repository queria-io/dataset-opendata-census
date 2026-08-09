select
    portal_id,
    cast(item_no as integer) as item_no,
    item_key,
    search_word,
    try_cast(dataset_count as integer) as dataset_count,
    status,
    try_cast(measured_on as date) as measured_on
from {{ ref('raw_word_hit') }}
