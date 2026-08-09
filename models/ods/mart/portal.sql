select
    portal_id,
    title,
    operator,
    site_url,
    api_base,
    catalog_type,
    organization_count,
    lg_organization_count,
    non_lg_organizations,
    status,
    measured_on
from {{ ref('stg_portal') }}
