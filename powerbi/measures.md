# DAX Measures

All measures live in a single `fact Measures` table (created via Enter Data, not a query
against Postgres). A measure's home table is organizational only — it can reference any
table/column in the model regardless of where it's defined.

Table names in the model carry a literal `public ` prefix (e.g. `public fact_order_sales`),
inherited from the Postgres schema name at import time.

Threshold values below (`267.67`, `8778.43`, `36.34`) are the 90th percentile of the
relevant column, pulled from the live warehouse at the time these measures were written.

## fact_order_sales

```dax
Total Orders = COUNTROWS('public fact_order_sales')
```

```dax
Total Revenue = SUM('public fact_order_sales'[Total Order Cost])
```

```dax
Average Item Price = 
DIVIDE(
    SUM('public fact_order_sales'[Items Value]),
    SUM('public fact_order_sales'[Item Count])
)
```

```dax
Pct Revenue By State = 
DIVIDE(
    [Total Revenue],
    CALCULATE([Total Revenue], ALL('public dim_customers'[State]))
)
```

```dax
High Value Orders = 
COUNTROWS(FILTER('public fact_order_sales', 'public fact_order_sales'[Total Order Cost] > 267.67))
```

```dax
Average Order Value = DIVIDE([Total Revenue], [Total Orders])
```

```dax
Revenue MoM Growth % = 
VAR PriorMonthRevenue = CALCULATE([Total Revenue], DATEADD('public dim_date'[Date], -1, MONTH))
RETURN DIVIDE([Total Revenue] - PriorMonthRevenue, PriorMonthRevenue)
```

## fact_seller_sales

```dax
Total Sellers = COUNTROWS('public fact_seller_sales')
```

```dax
Total Seller Revenue = SUM('public fact_seller_sales'[Total Sales])
```

```dax
Average Items Sold Per Seller = AVERAGE('public fact_seller_sales'[Items Sold])
```

```dax
Pct Seller Revenue By State = 
DIVIDE(
    [Total Seller Revenue],
    CALCULATE([Total Seller Revenue], ALL('public dim_sellers'[State]))
)
```

```dax
Top Performing Sellers = 
COUNTROWS(FILTER('public fact_seller_sales', 'public fact_seller_sales'[Total Sales] > 8778.43))
```

```dax
Seller Revenue Rank = 
RANKX(ALL('public fact_seller_sales'), [Total Seller Revenue], , DESC)
```

```dax
Cumulative Seller Revenue % = 
VAR CurrentRank = [Seller Revenue Rank]
VAR CumulativeRevenue =
    CALCULATE(
        [Total Seller Revenue],
        FILTER(ALL('public fact_seller_sales'), [Seller Revenue Rank] <= CurrentRank)
    )
RETURN
    DIVIDE(CumulativeRevenue, CALCULATE([Total Seller Revenue], ALL('public fact_seller_sales')))
```

```dax
Pareto 80 Pct Line = 0.8
```

Used together on the Sellers page's Pareto chart (seller revenue, ranked descending, with a
cumulative-% line against a flat 80% reference) — see [`narrative_report.md`](narrative_report.md) Act 2.

## fact_order_delivery_distance

```dax
Total Deliveries = COUNTROWS('public fact_order_delivery_distance')
```

```dax
Average Delivery Delay = AVERAGE('public fact_order_delivery_distance'[Delivery Delay (Days)])
```

```dax
Average Distance = AVERAGE('public fact_order_delivery_distance'[Distance (km)])
```

```dax
Pct Late Deliveries = 
DIVIDE(
    COUNTROWS(FILTER('public fact_order_delivery_distance', 'public fact_order_delivery_distance'[Delivery Delay (Days)] > 0)),
    [Total Deliveries]
)
```

**Data quality note:** `Average Distance` (and any chart built on `Distance (km)`) can be pulled
upward by a small number of corrupted ZIP geolocation centroids — `dim_locations` averages every
raw lat/lng point sharing a ZIP prefix with no outlier filtering first, and Olist's public
geolocation dataset has some points geocoded well outside Brazil. Visuals built on distance
currently work around this with a visual-level filter (`Distance (km) < 4500`, Brazil's real
max extent); the permanent fix belongs in `dim_locations` itself (bound raw lat/lng to Brazil's
range before the `avg()`), not repeated per-visual. Not yet applied as of this writing.

## fact_geolocation_freight_avg

```dax
Total Zip Zones = COUNTROWS('public fact_geolocation_freight_avg')
```

```dax
Average Freight Ratio = AVERAGE('public fact_geolocation_freight_avg'[Freight Cost Ratio %])
```

```dax
High Freight Zones = 
COUNTROWS(FILTER('public fact_geolocation_freight_avg', 'public fact_geolocation_freight_avg'[Freight Cost Ratio %] > 36.34))
```

## Calculated columns

Unlike the measures above, these live directly on `fact_order_delivery_distance` as row-level
columns (Table tools → **New column**, not New measure) — they tag each delivery row with a
category, so they need row context rather than an aggregation.

```dax
Customer State = 
LOOKUPVALUE(
    'public dim_customers'[State],
    'public dim_customers'[Customer ID], 'public fact_order_delivery_distance'[Customer ID]
)
```

Added because `fact_order_delivery_distance` has no usable relationship to `dim_customers` for
this purpose: the direct relationship exists but is inactive (activating it creates an ambiguous
path back to `dim_date` through `fact_order_sales`), and `USERELATIONSHIP` didn't propagate the
filter correctly either (likely a cross-filter direction issue on that relationship). This column
sidesteps the relationship entirely with a direct row-by-row lookup. Used as the `State` field on
the Delivery page's state-performance table in place of `dim_customers[State]`.

```dax
Delivery Status = IF('public fact_order_delivery_distance'[Delivery Delay (Days)] > 0, "Late", "On-Time or Early")
```

```dax
Delay Bucket = 
SWITCH(
    TRUE(),
    'public fact_order_delivery_distance'[Delivery Delay (Days)] = 0, "On Time",
    'public fact_order_delivery_distance'[Delivery Delay (Days)] <= 3, "1-3 Days Late",
    'public fact_order_delivery_distance'[Delivery Delay (Days)] <= 7, "4-7 Days Late",
    'public fact_order_delivery_distance'[Delivery Delay (Days)] <= 14, "8-14 Days Late",
    "15+ Days Late"
)
```

```dax
Delay Bucket Sort = 
SWITCH(
    TRUE(),
    'public fact_order_delivery_distance'[Delivery Delay (Days)] = 0, 1,
    'public fact_order_delivery_distance'[Delivery Delay (Days)] <= 3, 2,
    'public fact_order_delivery_distance'[Delivery Delay (Days)] <= 7, 3,
    'public fact_order_delivery_distance'[Delivery Delay (Days)] <= 14, 4,
    5
)
```

`Delay Bucket`'s **Sort by column** (Column tools ribbon) is set to `Delay Bucket Sort`, since the
text labels would otherwise sort alphabetically ("1-3 Days Late" before "15+ Days Late" before
"4-7 Days Late") instead of in the intended severity order.

## Formatting applied

| Format | Measures |
|---|---|
| Currency | `Total Revenue`, `Average Item Price`, `Total Seller Revenue`, `Average Order Value` |
| Whole Number | `Total Orders`, `High Value Orders`, `Total Sellers`, `Top Performing Sellers`, `Total Deliveries`, `Total Zip Zones`, `High Freight Zones`, `Seller Revenue Rank` |
| Decimal Number | `Average Items Sold Per Seller`, `Average Delivery Delay`, `Average Distance`, `Average Freight Ratio` |
| Percentage | `Pct Revenue By State`, `Pct Seller Revenue By State`, `Pct Late Deliveries`, `Revenue MoM Growth %`, `Cumulative Seller Revenue %`, `Pareto 80 Pct Line` |

Note: `Average Freight Ratio` is Decimal Number, not Percentage — the underlying
`Freight Cost Ratio %` column already stores a plain percentage value (e.g. `18.53`
meaning 18.53%), so applying Percentage format would double-apply and show `1853%`.

Note: `Pareto 80 Pct Line` must be formatted as Percentage even though it's a hardcoded constant
(`0.8`) — it needs to render on the same 0–100% scale as `Cumulative Seller Revenue %` to work as
a reference line on that chart.
