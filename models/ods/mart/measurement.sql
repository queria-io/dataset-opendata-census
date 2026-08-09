{# 1行 = 団体 × 項目 × 観測。項目名を持たせて 1 テーブルで読めるようにする。 #}

select
    m.lg_code,
    m.lg_code_5,
    m.prefecture_code,
    m.item_no,
    m.item_key,
    i.item_label,
    i.definition_book,
    m.is_published,
    m.dataset_count,
    m.portal_id,
    m.measured_on
from {{ ref('stg_measurement') }} as m
inner join {{ ref('stg_item') }} as i
    on m.item_no = i.item_no
