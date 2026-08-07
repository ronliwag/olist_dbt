with staging as (
    select * from {{ ref('stg_geolocation') }}
)

-- Deduplicate to 1 row per ZIP code prefix so this can be used as the "one"
-- side of a relationship (multiple lat/lng points share the same prefix upstream)
select
    geolocation_zip_code_prefix,
    avg(geolocation_lat) as geolocation_lat,
    avg(geolocation_lng) as geolocation_lng,
    max(geolocation_city) as geolocation_city,
    max(geolocation_state) as geolocation_state
from staging
group by 1