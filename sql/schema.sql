-- DataCo — PostgreSQL schema. One row = one order line (Order_Item_Id).
-- PII columns (email, password, street, names) are NOT loaded; see clean file.
CREATE SCHEMA IF NOT EXISTS dataco;

CREATE TABLE dataco.order_lines (
    order_id INT, order_item_id INT PRIMARY KEY, order_date DATE,
    customer_id INT, customer_segment TEXT, customer_city TEXT,
    customer_state TEXT, customer_country TEXT,
    market TEXT, order_region TEXT, order_state TEXT, order_country TEXT,
    department_id INT, department_name TEXT, category_id INT, category_name TEXT,
    product_name TEXT, product_price NUMERIC(10,2),
    order_item_quantity INT, order_item_product_price NUMERIC(10,2),
    order_item_discount NUMERIC(10,2), order_item_discount_rate NUMERIC(5,4),
    order_item_total NUMERIC(12,2), sales NUMERIC(12,2),
    order_profit_per_order NUMERIC(12,2), benefit_per_order NUMERIC(12,2),
    order_item_profit_ratio NUMERIC(6,4),
    shipping_mode TEXT, days_for_shipment_scheduled INT, days_for_shipping_real INT,
    delivery_status TEXT, late_delivery_risk INT CHECK (late_delivery_risk IN (0,1)),
    order_status TEXT, shipping_date DATE);

CREATE INDEX idx_dataco_order ON dataco.order_lines (order_id);
CREATE INDEX idx_dataco_date ON dataco.order_lines (order_date);
CREATE INDEX idx_dataco_market ON dataco.order_lines (market);
