-- Continuous calendar spine spanning the full range of order activity,
-- required for DAX time-intelligence functions (SAMEPERIODLASTYEAR, TOTALYTD, ...)
-- which need every calendar day present, not just days that had an order.
with bounds as (
    select
        min(date(purchased_at)) as min_date,
        max(date(purchased_at)) as max_date
    from {{ ref('stg_orders') }}
    where purchased_at is not null
),

date_spine as (
    select generate_series(min_date, max_date, interval '1 day')::date as date_day
    from bounds
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