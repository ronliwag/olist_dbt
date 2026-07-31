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

## fact_order_delivery_distance

```dax
Total Deliveries = COUNTROWS('public fact_order_delivery_distance')
```

```dax
Average Delivery Delay = AVERAGE('public fact_order_delivery_distance'[Delivery Delay (days)])
```

```dax
Average Distance = AVERAGE('public fact_order_delivery_distance'[Distance (km)])
```

```dax
Pct Late Deliveries = 
DIVIDE(
    COUNTROWS(FILTER('public fact_order_delivery_distance', 'public fact_order_delivery_distance'[Delivery Delay (days)] > 0)),
    [Total Deliveries]
)
```

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

## Formatting applied

| Format | Measures |
|---|---|
| Currency | `Total Revenue`, `Average Item Price`, `Total Seller Revenue` |
| Whole Number | `Total Orders`, `High Value Orders`, `Total Sellers`, `Top Performing Sellers`, `Total Deliveries`, `Total Zip Zones`, `High Freight Zones` |
| Decimal Number | `Average Items Sold Per Seller`, `Average Delivery Delay`, `Average Distance`, `Average Freight Ratio` |
| Percentage | `Pct Revenue By State`, `Pct Seller Revenue By State`, `Pct Late Deliveries` |

Note: `Average Freight Ratio` is Decimal Number, not Percentage — the underlying
`Freight Cost Ratio %` column already stores a plain percentage value (e.g. `18.53`
meaning 18.53%), so applying Percentage format would double-apply and show `1853%`.
