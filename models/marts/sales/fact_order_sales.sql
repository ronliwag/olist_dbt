-- One row per order, summarizing the logistics lifecycle, 
-- total items/freight, and aggregated payment amounts.

with orders as (
    select * from {{ ref('stg_orders') }}
),

-- Aggregate items & shipping up to the order level
order_items_aggregated as (
    select
        order_id,
        count(order_item_id) as total_items_count,
        count(distinct seller_id) as total_unique_sellers,
        sum(price) as total_items_value,
        sum(freight_value) as total_freight_value
    from {{ ref('stg_order_items') }}
    group by 1
),

-- Aggregate payments up to the order level
payments_aggregated as (
    select
        order_id,
        count(distinct payment_type) as payment_methods_count,
        sum(payment_sequential) as total_payment_installments,
        sum(payment_value) as total_payment_value
    from {{ ref('stg_order_payments') }}
    group by 1
)

select
    -- Primary Key (Grain: 1 row per order)
    o.order_id,

    -- Foreign Keys & Status
    o.customer_id,
    o.order_status,

    -- Logistics Lifecycle Timestamps
    o.purchased_at,
    o.approved_at,
    o.carrier_delivered_at,
    o.customer_delivered_at,
    o.estimated_delivery_at,

    -- Aggregated Order Item / Logistics Measures
    coalesce(oi.total_items_count, 0) as total_items_count,
    coalesce(oi.total_unique_sellers, 0) as total_unique_sellers,
    coalesce(oi.total_items_value, 0) as total_items_value,
    coalesce(oi.total_freight_value, 0) as total_freight_value,
    (coalesce(oi.total_items_value, 0) + coalesce(oi.total_freight_value, 0)) as total_order_cost,

    -- Aggregated Payment Measures
    coalesce(p.total_payment_value, 0) as total_payment_value,
    coalesce(p.total_payment_installments, 0) as total_payment_installments,
    coalesce(p.payment_methods_count, 0) as payment_methods_count

from orders o
left join order_items_aggregated oi
    on o.order_id = oi.order_id
left join payments_aggregated p
    on o.order_id = p.order_id