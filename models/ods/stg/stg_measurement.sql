{# 型付け。lg_code は 6 桁のまま保持し、5 桁（検査数字なし）も併記する。 #}

select
    portal_id,
    lg_code,
    left(lg_code, 5) as lg_code_5,
    left(lg_code, 2) as prefecture_code,
    cast(item_no as integer) as item_no,
    item_key,
    cast(is_published as boolean) as is_published,
    cast(dataset_count as integer) as dataset_count,
    try_cast(measured_on as date) as measured_on
from {{ ref('raw_measurement') }}
