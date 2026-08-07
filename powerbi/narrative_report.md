# Olist Marketplace — Business Narrative Report

*Companion to [`measures.md`](measures.md). This is the story the dashboard should tell — each act below maps to a specific page and set of measures, so the visuals aren't just charts, they're evidence for a claim. Revised to match the final four-page build: Executive Overview, Sellers, Logistics, Delivery. Every page now carries its own date-range and multi-state slicer, so every act below can be re-cut by time period and region independently — this wasn't true of earlier drafts, where only the Overview page had a slicer.*

## Executive summary

Olist's marketplace is growing, but three deeper risks sit just underneath that headline number — all visible from the Executive Overview page alone. A small share of sellers carry a disproportionate share of revenue, and those same top sellers cluster geographically rather than spreading evenly across cities. Shipping cost and delivery reliability both vary sharply by region rather than being a uniform operating cost — and, newly proven in this build, freight cost rises with distance the same way delivery delay does, closing a gap this report used to have to leave as an assumption. The recommended actions are seller diversification, regional logistics investment targeted at the worst-performing zones and cities, and closing the one data gap that remains: connecting delivery performance to customer satisfaction.

---

## Act 1 — Executive Overview: a single-glance health check

**Business question:** Is the business healthy overall — not just growing, but cost-efficient, reliable, and not overly dependent on a handful of sellers?

This page's job changed from earlier drafts. It used to ask one question — "is revenue growing?" — with a KPI row built entirely from growth measures. In the final build, it asks a broader question by pulling one headline signal from *each* of the other three pages: `Total Revenue` and `Total Orders` (growth), `Total Seller Revenue` and `Total Sellers` (a preview of the seller-concentration story), `Average Freight Ratio %` (a preview of the cost story), and `Pct Late Deliveries` (a preview of the delivery-reliability story). The Overview page is no longer just Act 1 — it's a compressed preview of Acts 2 through 4, all in one KPI row.

**Evidence:** `Total Revenue`, `Total Orders`, `Total Seller Revenue`, `Total Sellers`, `Average Freight Ratio`, `Pct Late Deliveries`.

**Dashboard page:** Executive Overview — the six-KPI row above; a dual-axis Total Revenue and Orders trend by date (Y1 = revenue, Y2 = orders); a Freight Cost Ratio by State horizontal bar chart; and an Order Status breakdown donut. Two build notes worth knowing:
- **The freight-by-state chart lives here, not on Logistics.** It was originally built on Logistics, then moved here deliberately, so a regional cost signal is visible without requiring a click into a deeper page. Logistics keeps a *city*-level cut of the same underlying cost story instead (Act 3), so the two pages don't duplicate each other.
- **The Order Status donut reverses an earlier design decision.** Earlier drafts of this report explicitly dropped an order-status breakdown from this page as "too operational for a glance-level page." The final build reinstates it — worth knowing if anyone asks why it's back, since it's a deliberate reversal, not an oversight.

**The claim this supports:** *"At a glance, the marketplace looks healthy across four different dimensions — growth, seller base, cost, and delivery reliability — and each of those four signals gets its own deep-dive page next."* This is the baseline the rest of the story complicates.

---

## Act 2 — Sellers: growth concentrated in a few hands, and in a few cities

**Business question:** Is growth broad-based, or does it depend on a small number of sellers — and are those top sellers themselves clustered in just a handful of cities?

The original version of this page only asked about revenue concentration. The final build adds a second lens: geographic concentration of the *top* sellers specifically, not just seller revenue in general.

**Evidence:** `Total Seller Revenue`, `Total Sellers`, `Top Performing Sellers`, `Average Items Sold Per Seller`, plus `Seller Revenue Rank` and `Cumulative Seller Revenue %` against the flat `Pareto 80 Pct Line` reference.

**Dashboard page:** Sellers — a KPI row; a Total Seller Revenue by State horizontal bar chart; the seller-revenue Pareto/concentration chart (unchanged from earlier drafts — still the core evidence for "few sellers carry most of the revenue"); and a **Top 10 City by Top Seller Concentration** treemap. That treemap replaced an earlier state-level treemap — the state cut is now covered by the new bar chart instead, so the treemap was freed up to answer a sharper question: *of our highest-performing sellers specifically, which cities are they clustered in?*

**The claim this supports:** *"Growth is real, but it's fragile on two fronts at once — a small number of sellers carry most of the revenue, and those same sellers aren't even spread across the country. Losing one city's worth of top sellers could hurt as much as losing any individual account."* Retention and diversification are now both a seller-level and a geography-level risk, not just the former.

---

## Act 3 — Logistics: the geography of cost, now tied to distance

**Business question:** Where does the marketplace lose margin to logistics — and does distance actually drive that cost the same way it drives delivery delay?

This is the biggest change in this build. Earlier drafts of this report treated freight cost (Act 3) and delivery delay (Act 4) as two separate, unconnected stories — the freight table only ever knew a customer's ZIP zone, and the distance table never carried freight cost at all. That gap was explicitly named as unproven. It's now closed: a new measure, **`Delivery Freight Ratio %`**, pulls order-level freight value and item value onto the same table that already computes seller-to-customer distance, via two calculated columns (`Order Freight Value`, `Order Item Value`) using the same `LOOKUPVALUE` technique already in use elsewhere in this model. That makes it possible, for the first time, to plot freight cost against distance the same way delay is already plotted against distance.

**Evidence:** `Total Zip Zones`, `Average Freight Ratio`, `High Freight Zones`, and the new `Delivery Freight Ratio %`.

**Dashboard page:** Logistics — a KPI row (unchanged); a **Top High Freight Zones by City** vertical bar chart, which replaces both the state-level chart (moved to Overview, Act 1) and the zip-level detail table from earlier drafts (this build has no table visuals anywhere — see cross-cutting notes below); a **Delivery Freight Ratio by Distance** line-and-clustered-column chart with a fitted trend line, built the same way as the Delivery page's distance/delay chart so it can carry a real statistical trend line rather than just a reference line; and a **Freight Cost vs. Order Volume by State** scatter plot (average freight value on X, total order count on Y, bubble size = freight ratio, colored by state) — this asks a question neither of the other two charts can: *are the states doing the most volume also the ones paying the highest freight cost, or is high freight cost concentrated in low-volume states instead?*

**Two caveats worth naming here specifically:**
1. The `Delivery Freight Ratio %` chart inherits the same corrupted-ZIP-centroid data quality issue already flagged on the Delivery page (Act 4) — since it uses the same `Distance (km)` column, any distance-based visual on either page is exposed unless it carries the `<4500km` filter.
2. `Order Freight Value` is pulled at **order grain** and repeated across every item in a multi-item order — so an order with three items counts three times toward the freight-by-distance average, while a single-item order counts once. This is a reasonable approximation for a directional trend chart, but it's not a precise per-item allocation, and shouldn't be quoted as an exact freight-per-item figure.

**The claim this supports:** *"Logistics cost isn't just regional (the bar chart) — it's distance-driven (the new trend chart), the same underlying variable that drives delivery delay. That means the same regional logistics investment that would fix delay in Act 4 plausibly reduces freight cost too — these aren't two separate problems needing two separate fixes, they're two symptoms of the same root cause."*

---

## Act 4 — Delivery: distance, delay, and monitoring over time

**Business question:** Does shipping distance predict unreliable delivery — and is delivery performance improving or getting worse over time?

The core distance-vs-delay evidence is unchanged from earlier drafts. What changed is the page's second chart: earlier drafts used a delay-severity bucket chart (On Time / 1–3 / 4–7 / 8–14 / 15+ days late) to distinguish "mostly mild delays" from "a severe long tail." The final build replaces that with a **Delivery Performance by Month** chart instead, trading the severity breakdown for a temporal one.

**Evidence:** `Total Deliveries`, `Average Delivery Delay`, `Average Distance`, `Pct Late Deliveries`.

**Dashboard page:** Delivery — a KPI row; an On-Time vs. Late donut (unchanged); a **Delivery Performance by Month** line-and-clustered-column chart (average delay as columns, % late deliveries as a line, trended by month — note: this chart's month axis needs `Sort by Column` set to a numeric month field, since the raw month-name text field sorts alphabetically, not chronologically, by default); and the **Delivery Delay by Distance** binned trend chart (unchanged — the reason this chart type is a line-and-clustered-column rather than a scatter is the same as before: Power BI's Analytics-pane trend line only supports line/column/area/combo chart types).

**Worth flagging if asked:** the delay-bucket severity view from earlier drafts is no longer part of this page. That means the page no longer directly answers "is late mostly mild or mostly severe" — it now answers "is delivery reliability trending better or worse over time" instead. If the severity distinction still matters to a stakeholder, it would need to be added back as a fifth visual; it isn't currently duplicated anywhere else in the build.

**The claim this supports:** *"Delay is predictable via distance — a lever operations can act on proactively — and now trackable month over month, so the business can tell whether logistics investment is actually improving reliability over time, not just whether distance correlates with delay in the abstract."*

---

## Act 5 — The next chapter: closing the loop on cost and trust

The natural continuation of this story is still connecting delivery performance to customer sentiment — this hasn't changed with the new build. Does a delayed order actually correlate with a lower review score? If so, the freight-cost and delivery-delay findings in Acts 3–4 stop being purely an operations story and become a revenue-risk story — "delay costs us Y in future retention/reviews," which is the sentence that moves budget.

**Recommended next step:** build a model joining `stg_order_reviews` into the order-level fact table (or a small standalone `fact_order_reviews`), and add a measure like *average review score by delivery-delay bucket*. That single addition would let Act 4 end with a number instead of a caveat — and now that Act 3 has proven the freight-cost/distance link, a review-score join would let that same logic extend to freight cost as well: does a higher-freight order also correlate with lower satisfaction?

---

## So what — recommendations

1. **Seller diversification program.** The revenue concentration in Act 2 is a retention priority for top sellers and a growth priority for the long tail — and now that the treemap shows those top sellers cluster geographically too, this is also a city-level diversification question, not just an account-level one.
2. **Targeted regional logistics investment — now with a sharper target.** Act 3 previously supported only a regional (state/city) cut of where to invest. It now also supports a distance-based cut, since freight cost has been shown to rise with distance the same way delay does — meaning the same investment (a regional fulfillment point, a renegotiated carrier contract for long-haul routes) plausibly addresses both cost and delay at once.
3. **Proactive delay and freight management on high-distance corridors.** If both delay and freight cost predictably rise with distance, that's a lever for setting realistic estimated-delivery windows, pre-flagging high-risk shipments, *and* budgeting for freight cost on long-haul orders — one root cause, two operational fixes.
4. **Instrument the review-score linkage.** Closing the Act 5 gap turns four operational findings (growth, concentration, cost, delay) into financial ones, and is still the highest-leverage next addition to the data model for this narrative specifically.

---

## Appendix — narrative-to-dashboard map

| Act | Business question | Dashboard page | Key measures / visuals |
|---|---|---|---|
| 1 | Is the business healthy overall — growth, cost, seller base, delivery, all at once? | Executive Overview — dual-axis revenue/orders trend, freight-by-state bar, order-status donut | `Total Revenue`, `Total Orders`, `Total Seller Revenue`, `Total Sellers`, `Average Freight Ratio`, `Pct Late Deliveries` |
| 2 | Is growth broad-based, or concentrated in a few sellers and cities? | Sellers — revenue-by-state bar, Pareto chart, top-city treemap | `Total Seller Revenue`, `Seller Revenue Rank`, `Cumulative Seller Revenue %`, `Top Performing Sellers` |
| 3 | Where is logistics cost highest, and does distance drive it? | Logistics — high-freight-zones-by-city bar, freight-by-distance trend, freight-vs-volume scatter | `Average Freight Ratio`, `High Freight Zones`, `Delivery Freight Ratio %` |
| 4 | Does distance predict delay, and is reliability trending better or worse? | Delivery — on-time/late donut, performance-by-month chart, delay-by-distance trend | `Average Delivery Delay`, `Average Distance`, `Pct Late Deliveries` |
| 5 | Does delay (or freight cost) affect customer trust? | *(not yet built — needs review-score join)* | *(new)* average review score by delay bucket |

**Cross-cutting build notes** (not tied to one Act, but relevant to reading the dashboard correctly):
- **Every page now has its own date-range and multi-state slicer**, not just Executive Overview. This is a real upgrade over earlier drafts — any act can be re-cut by time and region independently. It also means there are now four times as many slicer fields to get right: if any page's slicer was copied from another page rather than built fresh against that page's own tables, it will silently filter nothing (see the original Logistics build note this replaces).
- **This build has no table visuals anywhere.** Every page that used to rely on a sortable detail table (Sellers, Logistics) now uses a ranked bar chart, treemap, or scatter plot instead, with drill-down detail moved into tooltips rather than rows.
- **Distance-based measures are subject to the ZIP-centroid data quality issue on two pages now, not one** — Delivery (`Average Distance`, delay-by-distance) and Logistics (`Delivery Freight Ratio %`) both read the same `Distance (km)` column and need the same `<4500km` treatment.
- The Executive Overview's date-range slicer default selection should still exclude the incomplete trailing months flagged in earlier drafts — this hasn't changed, and any new visual added later still needs that checked, not assumed.
- All cross-filtering between charts and KPI cards was deliberately disabled per visual (Format → Edit interactions) in earlier drafts — carry this forward and verify it's still applied on the new visuals added in this build (freight-by-distance chart, scatter plot, order-status donut, performance-by-month chart), since it wasn't automatically inherited when they were created.
