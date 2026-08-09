{# 観測対象カタログの記録。観測に失敗したカタログも status 付きで残る。 #}

{{ config(materialized='table') }}

select *
from read_json(
    'data/portal.ndjson',
    format = 'newline_delimited',
    columns = {
        'portal_id': 'VARCHAR',
        'title': 'VARCHAR',
        'operator': 'VARCHAR',
        'site_url': 'VARCHAR',
        'api_base': 'VARCHAR',
        'type': 'VARCHAR',
        'organization_count': 'VARCHAR',
        'lg_organization_count': 'VARCHAR',
        'non_lg_organizations': 'VARCHAR',
        'status': 'VARCHAR',
        'measured_on': 'VARCHAR'
    }
)
