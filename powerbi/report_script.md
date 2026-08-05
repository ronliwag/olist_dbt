# Olist Marketplace Dashboard — Presentation Script

*Speaking script for an 8–10 minute walkthrough at ~115 wpm (~1,050 words total), written in plain, simple language. Bracketed cues tell you when to click to the next page. Companion to [`narrative_report.md`](narrative_report.md) and [`measures.md`](measures.md) — say the claim, then point at the visual that proves it.*

---

### Cold open (0:00–0:45)

Olist's marketplace is growing — the numbers show that clearly. But growth can be healthy, or it can be shaky underneath. A revenue chart by itself can't tell you which one you're looking at. Today I'll walk through four dashboard pages. Each one answers a different question about this business. By the end, we'll land on three things worth acting on, and one gap in our data that we should close next.

**[Click to Overview page]**

---

### Act 1 — A growing marketplace (0:45–2:30)

First question: is the business actually growing, and how fast?

This page starts with three numbers — Total Revenue, Total Orders, and Average Order Value — sitting above a chart that tracks revenue and orders over time. Our date table is a full, continuous calendar, so we can look at this by year, quarter, or month. The Revenue MoM Growth number at the top gives us the month-over-month change at a glance.

One quick flag before we read too much into this chart: the last month or two of data drop off sharply. That's not a real drop in sales — it's just where the dataset happens to end. There's a date filter on this page that hides that incomplete tail, so what you're looking at is the real trend, not a false alarm.

Below that, we break revenue down by state. That shows us growth isn't spread evenly — it's concentrated in certain regions. That sets up everything that follows.

So the claim here is simple: the marketplace is healthy and growing. That's our starting point. Now let's dig a layer deeper.

**[Click to Sellers page]**

---

### Act 2 — Growth concentrated in a few hands (2:30–4:15)

Here's the problem with a rising revenue line: it looks exactly the same whether it comes from thousands of small sellers, or from just a handful of big ones. Those two situations carry very different risk. If a big seller leaves, and revenue is spread out, we barely feel it. If revenue is concentrated, losing one or two accounts could really hurt.

This chart is called a Pareto chart. It ranks sellers by revenue, from highest to lowest, with a line tracking the running total as a percentage. There's also a flat reference line at 80%. Wherever our running-total line crosses that 80% mark tells us how many sellers are carrying most of our revenue.

Next to that chart, there's a detail table you can filter by state — showing revenue, items sold, and rank for each seller. And there's a treemap, which shows seller revenue by state using different-sized boxes instead of bars. We picked a treemap on purpose here, because revenue is a "part of a whole" kind of number, and boxes show that better than a bar chart would.

The claim: growth is real, but it's concentrated in a small group of sellers. That makes keeping our top sellers a business-continuity issue, not just a relationship-management task. And growing the smaller sellers is how we reduce that risk over time.

**[Click to Logistics page]**

---

### Act 3 — The geography of cost (4:15–5:45)

Now let's shift from revenue to cost. Shipping isn't the same flat cost on every order — it changes a lot depending on where the customer is. This page shows exactly how much it changes.

At the top, we see Total Zip Zones, Average Freight Ratio, and High Freight Zones. That last number counts the zip zones where freight cost, compared to the value of the items being shipped, is unusually high — above the top ten percent, or roughly a 36% ratio. The chart below breaks this ratio down by state, and the table lets us drill all the way down to individual zip codes.

Why does this matter? Because it turns "shipping is expensive" from a vague complaint into a specific, fixable problem. Some regions genuinely cost more to serve than others. That means the fix is targeted — renegotiate a carrier contract, or open a fulfillment point, in the worst-performing regions — not a blanket policy applied everywhere.

**[Click to Delivery page]**

---

### Act 4 — Distance, delay, and trust (5:45–8:00)

This page connects cost to the customer's actual experience. The question here: does shipping distance predict whether a delivery will be late?

The main chart groups deliveries into 50-kilometer distance bands, and adds a trend line fitted through them. We built this as a line-and-column chart instead of a scatter plot, because Power BI can only draw a proper trend line on that chart type. And what the trend line shows is clear: delay goes up as distance goes up. In other words, distance is an early warning sign for delay — something the operations team can plan for, instead of just reacting to late orders after they happen.

Next to that chart, there's a simple donut showing on-time versus late deliveries, and a bar chart showing delay buckets — on time, 1 to 3 days late, 4 to 7, 8 to 14, and 15-plus days late — sorted from least to most severe. This bucket view matters because an average alone can hide the real story. Is "late" mostly small delays that a bit more buffer time would fix? Or is a small number of very late orders dragging the average up, while most deliveries are actually fine? Those are two very different problems, and this chart tells them apart.

One honest data quality note here, since it affects this page directly: our first version of this chart showed some deliveries over 20,000 kilometers — which is basically impossible, since Brazil's own width, top to bottom, is only about 4,400 kilometers. That came from a handful of bad zip-code coordinates in our source data. We've filtered those out of this specific chart, but that's a temporary fix, not a permanent one. So if you ever see the Average Distance number somewhere else on this dashboard, keep that same caveat in mind.

And here's the honest gap in the story: we don't yet have customer review scores connected to this data. So the idea that "late delivery hurts customer trust" is a reasonable assumption — but right now, it's an assumption, not a number we can actually prove with this dashboard.

**[No click — close]**

---

### Recommendations and close (8:00–9:15)

So, four things worth acting on.

First — a seller diversification effort. Protect and retain our top sellers, but also actively grow the smaller ones.

Second — targeted logistics investment. Use the freight-ratio view to decide exactly which regions need a new carrier deal or a local fulfillment point, instead of treating shipping cost as one uniform problem.

Third — proactive delay management on the longest shipping routes. If delay predictably increases with distance, we can set more realistic delivery estimates, and flag high-risk shipments in advance, instead of just reacting after they're late.

And fourth — the biggest opportunity for our data itself: connect review scores to delivery performance. Adding one simple measure — average review score by delay bucket — would let this last page end with a real number, instead of an assumption. That one addition turns three operational findings into a financial one — which is the kind of sentence that actually moves a budget.

That's the walkthrough. I'm happy to take questions, or go back into any page in more detail.

---

**Delivery notes:**
- Target runtime: ~9–10 minutes at 115 wpm; trim a sentence or two from Act 4 if you're running long.
- Cross-filtering between charts is turned off on every page — clicking a bar won't change the KPI numbers, and that's intentional.
- If someone asks why Average Distance looks off anywhere, the answer is the zip-code data note in Act 4.
