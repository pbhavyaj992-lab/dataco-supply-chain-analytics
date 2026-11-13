-- 1. LEAKAGE CHECK — never use Delivery_Status as a predictor
SELECT delivery_status,
       COUNT(*) AS rows,
       100.0 * AVG(late_delivery_risk) AS late_rate_pct
FROM dataco.order_lines GROUP BY 1 ORDER BY 1;
-- Result: 'Late delivery' = 100% late, everything else = 0%. It IS the label.

-- 2. Late rate by shipping mode (the real driver)
SELECT shipping_mode, COUNT(*) AS orders,
       100.0 * AVG(late_delivery_risk) AS late_rate_pct,
       SUM(sales) AS sales, SUM(order_profit_per_order) AS profit
FROM dataco.order_lines GROUP BY 1 ORDER BY late_rate_pct DESC;

-- 3. Late rate by market (flat — not a regional problem)
SELECT market, COUNT(*) AS orders,
       100.0 * AVG(late_delivery_risk) AS late_rate_pct
FROM dataco.order_lines GROUP BY 1 ORDER BY late_rate_pct DESC;

-- 4. Loss-making order lines by department
SELECT department_name, COUNT(*) AS loss_orders, SUM(benefit_per_order) AS total_benefit
FROM dataco.order_lines WHERE benefit_per_order < 0
GROUP BY 1 ORDER BY total_benefit;

-- 5. Monthly orders, late rate, sales, profit
SELECT date_trunc('month', order_date) AS month, COUNT(*) AS orders,
       100.0 * AVG(late_delivery_risk) AS late_rate_pct,
       SUM(sales) AS sales, SUM(order_profit_per_order) AS profit
FROM dataco.order_lines GROUP BY 1 ORDER BY 1;

-- 6. What is knowable BEFORE shipping: late rate by scheduled days
SELECT days_for_shipment_scheduled, COUNT(*) AS orders,
       100.0 * AVG(late_delivery_risk) AS late_rate_pct,
       AVG(days_for_shipping_real) AS avg_real_days
FROM dataco.order_lines GROUP BY 1 ORDER BY 1;
