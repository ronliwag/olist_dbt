with source as (
    select * from {{ source('raw_olist', 'raw_order_items') }}
),

renamed_and_casted as (
    select
        order_id,
        order_item_id,
        product_id,
        seller_id,
        cast(shipping_limit_date as timestamp) as shipping_limit_date,
        price,
        freight_value
    from source
)

select * from renamed_and_casted