with order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

payments as (
    select
        order_id,
        sum(payment_value) as total_payment_value
    from {{ ref('stg_order_payments') }}
    group by 1
),

dim_customers as (
    select customer_id from {{ ref('dim_customers') }}
),

dim_products as (
    select product_id from {{ ref('dim_products') }}
),

dim_sellers as (
    select seller_id from {{ ref('dim_sellers') }}
)

select
    -- Primary Surrogate / Compound Key
    {{ dbt_utils.generate_surrogate_key(['oi.order_id', 'oi.order_item_id']) }} as sales_item_key,
    
    -- Foreign Keys to Dimensions
    oi.order_id,
    oi.order_item_id,
    o.customer_id,
    oi.product_id,
    oi.seller_id,
    date(o.purchased_at) as order_date_key,

    -- Order Timestamps & Status (UPDATED HERE)
    o.order_status,
    o.purchased_at,
    o.customer_delivered_at,

    -- Key Measures
    oi.price,
    oi.freight_value,
    (oi.price + oi.freight_value) as total_item_value,
    p.total_payment_value

from order_items oi
left join orders o 
    on oi.order_id = o.order_id
left join payments p 
    on oi.order_id = p.order_id
inner join dim_customers c 
    on o.customer_id = c.customer_id
inner join dim_products pr 
    on oi.product_id = pr.product_id
inner join dim_sellers s 
    on oi.seller_id = s.seller_id