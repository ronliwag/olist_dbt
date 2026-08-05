# Olist Marketplace — Business Narrative Report

*Companion to [`measures.md`](measures.md). This is the story the dashboard should tell — each act below maps to a specific panel and set of measures, so the visuals aren't just charts, they're evidence for a claim.*

## Executive summary

Olist's marketplace is growing, but that growth rests on uneven foundations: a small share of sellers carry a disproportionate share of revenue, and shipping cost and delivery reliability vary sharply by region rather than being a uniform operating cost. Distance appears to drive delivery delay, which — though not yet proven with review-score data — is a plausible channel through which regional logistics weakness becomes a customer-trust problem. The recommended actions are seller diversification, regional logistics investment targeted at the worst-performing zones, and closing the current data gap between delivery performance and customer satisfaction.

---

## Act 1 — A growing marketplace

**Business question:** Is the business growing, and how fast?

Total revenue and order volume trended over time is the opening beat — it establishes the frame that this is a live, scaling business, not a static dataset. Because `dim_date` is now a continuous calendar spine joined to `fact_order_sales` via `purchase_date_key`, this trend can be sliced by year/quarter/month and supports period-over-period comparisons (YTD, same-period-last-year).

**Evidence:** `Total Revenue`, `Total Orders` trended monthly, plus `Average Order Value` and `Revenue MoM Growth %` for headline context.

**Dashboard page:** Overview — KPI card row, the Revenue/Orders trend chart, a Revenue-by-State bar chart, and a `Revenue MoM Growth %` KPI visual (with sparkline) sitting where a raw order-status breakdown was originally considered and dropped as too operational for a glance-level page. A date-range slicer lets this page (and everything downstream of it) exclude the dataset's incomplete trailing months — Olist's extract tapers off sharply in its last month or two, which otherwise reads as a fake revenue collapse rather than a data artifact.

**The claim this supports:** *"The marketplace is healthy and expanding."* This is the baseline the rest of the story complicates.

---

## Act 2 — Growth concentrated in few hands

**Business question:** Is this growth broad-based, or does it depend on a small number of sellers?

A rising revenue line looks the same whether it comes from thousands of small sellers or a handful of large ones — but those two situations carry very different risk. If a small percentage of sellers generate most of the revenue, the marketplace has a concentration/dependency risk: losing a handful of accounts would materially hurt the topline.

**Evidence:** `Total Seller Revenue`, `Seller Revenue Rank`, and `Cumulative Seller Revenue %` plotted against a flat `Pareto 80 Pct Line` reference — a true Pareto chart, not just a leaderboard, since the leaderboard version turned out to be redundant with the detail table (below) and was dropped in favor of a treemap.

**Dashboard page:** Sellers — a KPI row, the Pareto/concentration chart, a sortable/filterable seller detail table (revenue, items sold, orders handled, avg item price, rank — filterable by state), and a Seller Revenue by State treemap. The treemap deliberately isn't a bar chart like the other "by state" views elsewhere on the dashboard — a treemap suits revenue (a part-of-whole quantity) better than it would suit a ratio metric, and it keeps the page visually distinct from Overview and Logistics rather than repeating the same chart shape a third time.

**The claim this supports:** *"Growth is real, but it's fragile — retention and diversification of top sellers is a business-continuity issue, not just an account-management one."*

---

## Act 3 — The geography of cost

**Business question:** Where does the marketplace lose margin to logistics?

Freight cost isn't a flat tax on every order — `fact_geolocation_freight_avg` shows it varies by customer region, some zones running a much higher freight-to-item-value ratio than others. This reframes "shipping is expensive" from a general operating fact into a specific, addressable problem: certain regions are structurally more expensive to serve.

**Evidence:** `Average Freight Ratio`, `High Freight Zones`, broken out by state.

**Dashboard page:** Logistics — a KPI row (`Total Zip Zones`, `Average Freight Ratio`, `High Freight Zones`), a Freight Cost Ratio by State bar chart, and a zip-level detail table filterable by a state slicer. (Build note: if this page is ever copied to create another one, rebuild any slicer's field from scratch against the new page's actual tables — a slicer copied along with the page kept filtering on the *old* page's dimension table, silently filtering nothing on the new one, since Power BI slicers only affect visuals on an actual relationship path from their own field.)

**The claim this supports:** *"Logistics cost is a geography problem, which means it has a geography-shaped solution — regional fulfillment or carrier renegotiation in the worst zones, not a blanket policy."*

---

## Act 4 — Distance, delay, and trust

**Business question:** Does shipping distance predict unreliable delivery, and what does that cost the business?

`fact_order_delivery_distance` lets us test whether the same regions that are expensive to ship to are also the ones where delivery is late. Plotting average delivery delay against distance (binned, since this table is order-item grain at ~112K rows) should show delay rising with distance — turning "some orders arrive late" into "distance is a leading indicator of delay," which is something operations can act on proactively rather than after the fact.

**Evidence:** `Average Delivery Delay`, `Average Distance`, `Pct Late Deliveries`, delay-vs-distance trend chart (binned).

**Dashboard page:** Delivery — a KPI row, the distance/delay chart (binned into 50km groups, built as a Line and clustered column chart rather than a true scatter — Power BI's Analytics-pane trend line isn't available on scatter charts, only line/column/area/combo types, so this chart type was chosen specifically to support a real fitted trend line rather than just a reference line), an On-Time vs. Late donut, a Delay Bucket distribution bar chart (severity-sorted: On Time / 1-3 / 4-7 / 8-14 / 15+ days late), and a state-level delivery-performance detail table.

**The claim this supports:** *"Delay is predictable, not random — and predictable problems can be resourced against."* The delay-bucket distribution adds a layer the averages alone hide: whether "late" mostly means mildly late (a small buffer would fix it) or whether a long tail of severely late orders is dragging the average up while most deliveries are actually fine — those are two different operational problems with two different fixes.

**Data quality finding, since it affects this Act specifically:** the first build of the distance chart showed bins running out to ~20,000km — close to Earth's theoretical maximum possible distance, and obviously impossible for two points inside Brazil (max real extent ~4,400km). Root cause: `dim_locations` computes each ZIP prefix's coordinate as `avg()` of every raw geolocation point sharing that prefix, with no outlier filtering — and Olist's public geolocation dataset has a known handful of points geocoded well outside Brazil. A single bad raw point is enough to drag an otherwise-normal ZIP's centroid off target. **Current state:** worked around with a visual-level filter (`Distance (km) < 4500`) on the distance chart only — this is a per-visual patch, not a fix, and any other visual or measure touching `distance_km` (including the `Average Distance` KPI card) is still exposed to the same corrupted centroids unless it carries the same filter. The permanent fix belongs in `dim_locations` (bound raw lat/lng to Brazil's real range before the `avg()`) and hasn't been applied yet — see [`measures.md`](measures.md) for the DAX-level note.

**Honest caveat — the chapter this story can't finish yet:** the pipeline stages a customer review dataset (`stg_order_reviews`) but it isn't joined into any mart yet. That means "late delivery hurts customer trust" is currently an assumption borrowed from general marketplace intuition, not a number this warehouse can prove. The report is more persuasive with that gap named than with the claim quietly asserted as fact.

---

## Act 5 — The next chapter: closing the loop on cost and trust

The natural continuation of this story is connecting delivery performance to customer sentiment: does a delayed order actually correlate with a lower review score? If so, the freight-cost and delivery-delay findings in Acts 3–4 stop being purely an operations story and become a revenue-risk story — "delay costs us Y in future retention/reviews," which is the sentence that moves budget.

**Recommended next step:** build a model joining `stg_order_reviews` into the order-level fact table (or a small standalone `fact_order_reviews`), and add a measure like *average review score by delivery-delay bucket*. That single addition would let Act 4 end with a number instead of a caveat.

---

## So what — recommendations

1. **Seller diversification program.** The revenue concentration in Act 2 is a retention priority for top sellers and a growth priority for the long tail, not just a leaderboard curiosity.
2. **Targeted regional logistics investment.** Use the freight-ratio-by-region view (Act 3) to prioritize *which* regions get a renegotiated carrier contract or a regional fulfillment point, instead of treating logistics cost as a uniform problem.
3. **Proactive delay management on high-distance corridors.** If delay predictably rises with distance (Act 4), that's a lever for setting realistic estimated-delivery windows or pre-flagging high-risk shipments, rather than reacting to lateness after the fact.
4. **Instrument the review-score linkage.** Closing the Act 5 gap turns three operational findings into one financial one, and is the highest-leverage next addition to the data model for this narrative specifically.

---

## Appendix — narrative-to-dashboard map

| Act | Business question | Dashboard page | Key measures |
|---|---|---|---|
| 1 | Is the business growing? | Overview — trend, revenue-by-state, growth KPI | `Total Revenue`, `Total Orders`, `Average Order Value`, `Revenue MoM Growth %` |
| 2 | Is growth broad-based or concentrated? | Sellers — Pareto chart, detail table, treemap | `Total Seller Revenue`, `Seller Revenue Rank`, `Cumulative Seller Revenue %` |
| 3 | Where is logistics cost highest? | Logistics — freight-by-state, detail table | `Average Freight Ratio`, `High Freight Zones` |
| 4 | Does distance predict delay? | Delivery — delay/distance trend, delay buckets, detail table | `Average Delivery Delay`, `Average Distance`, `Pct Late Deliveries`, `Delay Bucket` |
| 5 | Does delay affect customer trust? | *(not yet built — needs review-score join)* | *(new)* average review score by delay bucket |

**Cross-cutting build notes** (not tied to one Act, but relevant to reading the dashboard correctly):
- Every trend/KPI visual is subject to the incomplete-trailing-data issue flagged in Act 1 — the date-range slicer's default selection should exclude it, but any *new* visual added later needs that checked, not assumed.
- Distance-based measures (Act 4) are subject to the ZIP-centroid data quality issue until the `dim_locations` fix lands — treat `Average Distance` anywhere it appears with that caveat in mind.
- All cross-filtering between charts and KPI cards was deliberately disabled per visual (Format → Edit interactions) — clicking a bar/point/slice is not expected to filter the KPI row on any page.
