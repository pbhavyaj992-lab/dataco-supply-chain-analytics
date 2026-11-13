# Power BI model — DataCo Supply Chain Analytics

No .pbix is in this repo (no Power BI Desktop here). Build it from this document:
load `data/clean/dataco_clean.csv`, or connect Power BI to the PostgreSQL schema
in `sql/schema.sql`.

## Star schema
- **FactOrderLines** (grain: one order line) — `data/clean/dataco_clean.csv`.
  Sales, Order_Item_Total, Order_Profit_Per_Order, Benefit_per_order,
  Days_for_shipping_(real), Days_for_shipment_(scheduled), Late_delivery_risk.
- **DimCustomer** — Customer_Id, Customer_Segment, Customer_City/State/Country.
- **DimProduct** — Category_Name, Department_Name, Product_Name.
- **DimMarket** — Market, Order_Region, Order_Country.
- **DimDate** — order_date, month, year.
- Relationships: FactOrderLines → DimCustomer, → DimProduct, → DimMarket, → DimDate.

## DAX measures
```dax
Orders = COUNTROWS(FactOrderLines)
Late Delivery Rate % = 100 * AVERAGE(FactOrderLines[Late_delivery_risk])
Total Sales = SUM(FactOrderLines[Sales])
Total Profit = SUM(FactOrderLines[Order_Profit_Per_Order])
Total Benefit = SUM(FactOrderLines[Benefit_per_order])
Loss-Making Lines = CALCULATE(COUNTROWS(FactOrderLines), FactOrderLines[Benefit_per_order] < 0)
Loss-Making Share % = 100 * DIVIDE([Loss-Making Lines], [Orders])
Avg Real Shipping Days = AVERAGE(FactOrderLines[Days_for_shipping_(real)])
Avg Scheduled Days = AVERAGE(FactOrderLines[Days_for_shipment_(scheduled)])
-- DO NOT create a measure or model that uses Delivery_Status,
-- Days_for_shipping_(real) or shipping_date to "predict" Late_delivery_risk.
-- Those are known only after delivery. See output/leakage_check_*.csv.
```

## Pages
1. **Overview** — orders, late rate 54.83%, sales, profit; monthly late-rate trend.
2. **Leakage warning** — Delivery_Status x Late_delivery_risk crosstab; what may and may not be used as a predictor.
3. **Shipping modes** — late rate by mode (First Class 95.3% vs Standard 38.1%); scheduled vs real days.
4. **Profit leaks** — loss-making lines by department; profit by market and category.
