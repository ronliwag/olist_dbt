with source as (
    select * from {{ source('clnd_olist', 'clnd_order_payments') }}
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