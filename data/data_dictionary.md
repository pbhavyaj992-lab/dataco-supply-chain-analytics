# Data dictionary — DataCo (raw file, `data/raw/DataCoSupplyChainDataset.csv`)

180,519 rows x 53 columns, one row per order line. Money is in USD.

| Column | Notes |
|---|---|
| Type | DEBIT / TRANSFER / CASH / PAYMENT |
| Days_for_shipping_(real) | Actual days taken — known only AFTER delivery; leakage if used as a predictor |
| Days_for_shipment_(scheduled) | Promised days — known at order time; safe to use |
| Benefit_per_order, Sales_per_customer | Per-order economics |
| Delivery_Status | Advance shipping / Late delivery / Shipping canceled / Shipping on time — almost exactly encodes Late_delivery_risk; NEVER a predictor |
| Late_delivery_risk | 0 / 1 label; overall rate 54.83% |
| Category_Name (50), Department_Name (11), Market (5) | Product and geography dimensions |
| Customer_Email, Customer_Password, Customer_Street, Customer_Fname, Customer_Lname | PII — dropped from the clean file |
| Product_Description | 100% missing — dropped |
| Order_Zipcode | 86.24% missing — dropped |
| shipping_date_(DateOrders) | Actual ship date — known only after the fact; leakage if used as a predictor |
| Shipping_Mode | Standard Class / Second Class / First Class / Same Day |

Clean file: `data/clean/dataco_clean.csv` (180,519 rows x 50 columns).
