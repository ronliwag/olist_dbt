-- One row per seller, summarizing their historical lifetime performance.

with sellers as (
    select seller_id from {{ ref('stg_sellers') }}
),

order_items as (
    select 
        seller_id,
        order_id,
        order_item_id,
        price
    from {{ ref('stg_order_items') }}
)

select
    s.seller_id,
    
    -- Metrics required by grain spec
    coalesce(count(oi.order_item_id), 0) as total_items_sold,
    coalesce(sum(oi.price), 0.0) as total_sales_amount,
    
    -- Additional seller metrics
    count(distinct oi.order_id) as total_orders_handled,
    case 
        when count(oi.order_item_id) > 0 
        then round((sum(oi.price) / count(oi.order_item_id))::numeric, 2)
        else 0.0 
    end as avg_item_price

from sellers s
left join order_items oi 
    on s.seller_id = oi.seller_id
group by 1