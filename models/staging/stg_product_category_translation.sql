with source as (
    select * from {{ source('clnd_olist', 'clnd_product_category_translation') }}
),

renamed as (
    select
        product_category_name,
        product_category_name_english
    from source
)

select * from renamed