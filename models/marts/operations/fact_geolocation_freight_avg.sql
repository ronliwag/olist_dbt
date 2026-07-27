-- One row per customer geolocation (ZIP code prefix), calculating average 
-- freight values and shipping costs incurred across orders in that zone.

with geolocations_deduped as (
    -- Deduplicate geolocation to 1 row per zip_code_prefix
    select
        geolocation_zip_code_prefix,
        max(geolocation_city) as geolocation_city,
        max(geolocation_state) as geolocation_state,
        avg(geolocation_lat) as avg_lat,
        avg(geolocation_lng) as avg_lng
    from {{ ref('stg_geolocation') }}
    group by 1
),

customers as (
    select customer_id, customer_zip_code_prefix 
    from {{ ref('stg_customers') }}
),

orders as (
    select order_id, customer_id 
    from {{ ref('stg_orders') }}
),

order_items as (
    select order_id, price, freight_value 
    from {{ ref('stg_order_items') }}
)

select
    -- Primary Key (Grain: 1 row per ZIP code prefix)
    g.geolocation_zip_code_prefix,

    -- Geographic Attributes
    g.geolocation_city,
    g.geolocation_state,
    g.avg_lat,
    g.avg_lng,

    -- Key Freight & Geographic Measures
    count(distinct c.customer_id) as total_customers,
    count(distinct o.order_id) as total_orders,
    coalesce(sum(oi.freight_value), 0) as total_freight_value,
    coalesce(round(cast(avg(oi.freight_value) as numeric), 2), 0) as avg_freight_value,
    coalesce(sum(oi.price), 0) as total_items_value,
    
    -- Freight-to-Item Ratio (%)
    case 
        when sum(oi.price) > 0 
        then round(cast((sum(oi.freight_value) / sum(oi.price)) * 100 as numeric), 2)
        else 0 
    end as freight_cost_ratio_pct

from geolocations_deduped g
left join customers c
    on g.geolocation_zip_code_prefix = c.customer_zip_code_prefix
left join orders o
    on c.customer_id = o.customer_id
left join order_items oi
    on o.order_id = oi.order_id

group by 1, 2, 3, 4, 5