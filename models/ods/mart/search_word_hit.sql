{# 判定の根拠。どの語が何件に当たったかを残す。 #}

select
    w.portal_id,
    w.item_no,
    w.item_key,
    i.item_label,
    w.search_word,
    w.dataset_count,
    w.status,
    w.measured_on
from {{ ref('stg_word_hit') }} as w
inner join {{ ref('stg_item') }} as i
    on w.item_no = i.item_no
