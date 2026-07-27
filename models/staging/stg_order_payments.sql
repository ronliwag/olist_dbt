with source as (
    select * from {{ source('clnd_olist', 'clnd_order_payments') }}
),

renamed_and_casted as (
    select
        order_id,
        cast(payment_sequential as integer) as payment_sequential,
        payment_type,
        cast(payment_value as numeric) as payment_value
    from source
)

select * from renamed_and_casted