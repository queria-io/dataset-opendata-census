select
    portal_id,
    title,
    operator,
    site_url,
    api_base,
    type as catalog_type,
    try_cast(organization_count as integer) as organization_count,
    try_cast(lg_organization_count as integer) as lg_organization_count,
    non_lg_organizations,
    status,
    try_cast(measured_on as date) as measured_on
from {{ ref('raw_portal') }}
