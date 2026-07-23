with source as (
    select * from {{ source('raw_olist', 'raw_order_payments') }}
),

renamed_and_casted as (
    select
        order_id,
        payment_sequential,
        payment_type,
        payment_value
    from source
)

select * from renamed_and_casted