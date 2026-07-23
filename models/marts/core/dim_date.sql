with date_spine as (
    select distinct
        date(purchased_at) as date_day
    from {{ ref('stg_orders') }}
    where purchased_at is not null
)

select
    date_day as date_key,
    extract(year from date_day) as year,
    extract(quarter from date_day) as quarter,
    extract(month from date_day) as month,
    to_char(date_day, 'Month') as month_name,
    extract(day from date_day) as day_of_month,
    extract(isodow from date_day) as day_of_week,
    to_char(date_day, 'Day') as day_name
from date_spine