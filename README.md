# Olist ELT Pipeline

An end-to-end ELT pipeline for the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), orchestrated by Airflow (Astronomer/Cosmos) and modeled with dbt on Postgres.

## Business model

This project builds a **marketplace analytics warehouse** for Olist, a Brazilian e-commerce marketplace connecting sellers to customers. The dbt marts (`include/dbt/models/marts/`) are organized around two subject areas:

- **Sales & revenue performance** (`marts/sales/`)
  - `fact_order_sales` — one row per order: item/freight/payment totals, payment method mix, and the full logistics timestamp lifecycle (purchased → approved → handed to carrier → delivered).
  - `fact_seller_sales` — one row per seller: lifetime items sold, total revenue, orders handled, and average item price.
- **Logistics & delivery performance** (`marts/operations/`)
  - `fact_order_delivery_distance` — one row per order item: great-circle distance between customer and seller, actual vs. estimated delivery days, and delivery delay.
  - `fact_geolocation_freight_avg` — one row per customer ZIP code prefix: average freight cost and freight-to-item-value ratio for that region.

These facts are conformed against shared dimensions in `marts/core/`: `dim_customers`, `dim_sellers`, `dim_products`, `dim_locations`, and `dim_date`.

**Business statement:** *this warehouse answers how much revenue Olist's marketplace is generating and from which sellers, and how efficiently and reliably orders are being delivered, broken down geographically.* Concretely, it supports questions like:
- What's the total/average order value, and how do customers prefer to pay (method, installments)?
- Which sellers drive the most revenue and volume?
- Which regions (ZIP prefixes) have disproportionately high freight costs relative to item value?
- How does shipping distance relate to delivery delay, and how often are orders delivered late?

## Architecture

```
Kaggle CSVs
   │  download.sh (Kaggle API)
   ▼
include/data/raw/*.csv
   │  pyspark_loader.py (PySpark + JDBC)
   ▼
Postgres schema: raw            (raw_customers, raw_orders, ...)
   │  clean_olist.py + cleaners/*.py (pandas)
   ▼
Postgres schema: cleaned        (clnd_customers, clnd_orders, ...)
   │  dbt staging models (views)
   ▼
Postgres schema: public — staging views (stg_*)
   │  dbt mart models (tables)
   ▼
Postgres schema: public — marts (dim_*, fact_*)
```

Everything after the CSV download happens inside the Postgres warehouse. Airflow (via an Astronomer Cosmos `DbtTaskGroup`) orchestrates the whole chain as a single DAG, `olist_end_to_end_pipeline` (`dags/olist_etl_dag.py`).

## Prerequisites

- Docker (Docker Desktop or equivalent)
- [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli) — this project has no standalone `docker-compose.yml`; Astro CLI generates the Airflow webserver/scheduler/triggerer stack from the `Dockerfile` and merges in `docker-compose.override.yml`, which adds the project's own `olist-db` Postgres warehouse container.
- A [Kaggle account and API key](https://www.kaggle.com/docs/api) (needed to download the dataset).

## Setup

Replication starts and ends with `.env` — fill it out and the rest of the pipeline runs itself.

1. Copy the template and fill in your own values:
   ```bash
   cp .env.example .env
   ```
   - `KAGGLE_USERNAME` / `KAGGLE_KEY` — from your Kaggle account's API token.
   - `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` / `DB_NAME` — the warehouse Postgres connection (defaults match `docker-compose.override.yml`'s `olist-db` service).
   - `AIRFLOW_CONN_POSTGRES_DEFAULT` — how Airflow auto-registers the `postgres_default` connection; keep it consistent with the `DB_*` values above.
   - `SPARK_JARS_PATH` / `RAW_DATA_DIR` — paths as seen *inside* the Airflow containers; the defaults in `.env.example` are correct for the standard Astro CLI mount and shouldn't need to change.

2. Start the stack:
   ```bash
   astro dev start
   ```
   This builds the image, launches Airflow, and starts `olist-db` (reachable from your host at `localhost:5433` for a SQL client).

3. Open the Airflow UI at [localhost:8080](http://localhost:8080), unpause and trigger `olist_end_to_end_pipeline`.

4. The DAG runs the full chain automatically: download the CSVs → load into `raw` (PySpark) → verify `raw` schema → clean into `cleaned` (pandas) → verify `cleaned` schema → run the dbt staging + mart models (Cosmos task group).

## Verifying the result

- Query the warehouse directly (`localhost:5433`, database `olist`) — check `cleaned.clnd_*` tables, then `public.stg_*` and `public.dim_*`/`fact_*`.
- Or, from inside the `include/dbt` project: `dbt test` (runs the staging-layer tests) and `dbt docs generate && dbt docs serve`.

## Repo layout

```
dags/olist_etl_dag.py        # main Airflow DAG
docker-compose.override.yml  # adds the olist-db Postgres warehouse service
Dockerfile                   # Astro runtime image + Java (for PySpark)
include/
  download.sh                # Kaggle CSV download
  scripts/
    pyspark_loader.py        # raw CSVs -> Postgres `raw` schema
    clean_olist.py           # `raw` -> `cleaned` schema (pandas)
    cleaners/                # per-table cleaning logic
  dbt/                       # dbt project (staging + marts, see Business model above)
```

## Known gaps / recommendations

Not fixed in this pass, but worth addressing next:

- **No mart-level dbt documentation or tests.** Only `models/staging/_staging_models.yml` has `description:`s and `unique`/`not_null`/`relationships` tests. Add the same for `dim_*`/`fact_*` models.
- **`dim_locations` isn't deduplicated** by ZIP prefix (it's a raw pass-through of `stg_geolocation`), so downstream facts each re-aggregate (`avg(lat)/avg(lng)` per zip) themselves. Dedupe once in `dim_locations` instead.
- **`dim_date` only covers dates that appear in `stg_orders.purchased_at`**, not a full continuous calendar spine. Consider `dbt_date`'s date-spine macros (already a project dependency).
- **`dim_products.product_category_name` stays in Portuguese** even though `stg_product_category_translation` exists — join it in for an English name column.
- **No CI.** Even a minimal `dbt build`/`dbt test` + `astro dev parse` GitHub Actions workflow would catch breakage before merge.
- **No intermediate (`int_`) layer.** Fine at the current scale, but worth introducing if mart logic grows more complex.
