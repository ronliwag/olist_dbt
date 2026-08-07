-- One row per order item delivery, focusing strictly on geographic distance 
-- and delivery timeframe performance between seller and customer.

with order_items as (
    select
        order_id,
        order_item_id,
        seller_id,
        product_id
    from {{ ref('stg_order_items') }}
),

orders as (
    select 
        order_id, 
        customer_id, 
        purchased_at, 
        customer_delivered_at, 
        estimated_delivery_at 
    from {{ ref('stg_orders') }}
),

customers as (
    select 
        customer_id, 
        customer_zip_code_prefix 
    from {{ ref('dim_customers') }}
),

sellers as (
    select 
        seller_id, 
        seller_zip_code_prefix 
    from {{ ref('dim_sellers') }}
),

geo_locations as (
    select
        geolocation_zip_code_prefix as zip_code_prefix,
        geolocation_lat as lat,
        geolocation_lng as lng
    from {{ ref('dim_locations') }}
)

select
    -- Primary Surrogate Key
    row_number() over (
        order by oi.order_id, oi.order_item_id
    ) as delivery_distance_key,

    -- Degenerate Keys
    oi.order_id,
    oi.order_item_id,

    -- Foreign Keys to Dimensions
    o.customer_id,
    oi.seller_id,
    oi.product_id,
    date(o.purchased_at) as purchase_date_key,

    -- Location Identifiers
    c.customer_zip_code_prefix,
    s.seller_zip_code_prefix,

    -- Coordinates
    cust_geo.lat as customer_lat,
    cust_geo.lng as customer_lng,
    seller_geo.lat as seller_lat,
    seller_geo.lng as seller_lng,

    -- Calculated Spatial Measure (Haversine Formula in KM)
    round(
        cast(
            6371 * acos(
                least(1.0, greatest(-1.0,
                    cos(radians(cust_geo.lat)) * cos(radians(seller_geo.lat)) *
                    cos(radians(seller_geo.lng) - radians(cust_geo.lng)) +
                    sin(radians(cust_geo.lat)) * sin(radians(seller_geo.lat))
                ))
            ) as numeric
        ), 2
    ) as distance_km,

    -- Delivery Timeframe Measures (Days)
    date_part('day', o.customer_delivered_at - o.purchased_at) as actual_delivery_days,
    date_part('day', o.estimated_delivery_at - o.purchased_at) as estimated_delivery_days,
    
    -- Delay calculation (0 if delivered early or on-time)
    case 
        when o.customer_delivered_at > o.estimated_delivery_at 
        then date_part('day', o.customer_delivered_at - o.estimated_delivery_at)
        else 0 
    end as delivery_delay_days

from order_items oi
inner join orders o 
    on oi.order_id = o.order_id
inner join customers c 
    on o.customer_id = c.customer_id
inner join sellers s 
    on oi.seller_id = s.seller_id
left join geo_locations cust_geo 
    on c.customer_zip_code_prefix = cust_geo.zip_code_prefix
left join geo_locations seller_geo 
    on s.seller_zip_code_prefix = seller_geo.zip_code_prefix