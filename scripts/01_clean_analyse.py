"""DataCo Supply Chain — clean + analyse (real data, Kaggle copy via Hugging Face).
Business question: where is profit leaking — late delivery by market, shipping
mode, department and category — and what actually predicts late delivery?
LEAKAGE WARNING: Delivery_Status almost encodes the label Late_delivery_risk,
and Days_for_shipping_(real) / shipping_date are only known AFTER delivery.
Neither may be used as a predictor. No ~97% accuracy claim is made anywhere.
Run:  python3 scripts/01_clean_analyse.py   (from the project folder)
Reads data/raw/DataCoSupplyChainDataset.csv, writes data/clean/ + output/*.csv
"""
import os
import pandas as pd
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
CLEAN = os.path.join(BASE, "data", "clean")
OUT = os.path.join(BASE, "output")
os.makedirs(CLEAN, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(os.path.join(RAW, "DataCoSupplyChainDataset.csv"), low_memory=False)
N_RAW_COLS = len(df.columns)
print("Raw rows:", len(df), "| columns:", N_RAW_COLS)
print("Columns:", list(df.columns))

null_share = df.isna().mean().sort_values(ascending=False)
print("Highest null shares:\n", null_share.head(8).to_string())
print("Duplicate rows (all columns):", int(df.duplicated().sum()))

df["order_date"] = pd.to_datetime(df["order_date_(DateOrders)"], errors="coerce")
df["shipping_date"] = pd.to_datetime(df["shipping_date_(DateOrders)"], errors="coerce")
df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
df["order_year"] = df["order_date"].dt.year

# PII / unusable columns dropped from the clean file (never published):
DROP = ["Customer_Email", "Customer_Password", "Customer_Street",
        "Customer_Fname", "Customer_Lname", "Product_Description", "Product_Image"]
clean = df.drop(columns=[c for c in DROP if c in df.columns]).copy()
clean.to_csv(os.path.join(CLEAN, "dataco_clean.csv"), index=False)
print("Clean file columns:", len(clean.columns), "| rows:", len(clean))

late_rate = float(df["Late_delivery_risk"].mean())
kpis = {
    "raw_rows": int(len(df)),
    "raw_columns": int(N_RAW_COLS),
    "clean_columns": int(len(clean.columns)),
    "duplicate_rows": int(df.duplicated().sum()),
    "orders_unique_order_id": int(df["Order_Id"].nunique()),
    "customers_unique": int(df["Customer_Id"].nunique()),
    "late_delivery_rate_pct": round(100 * late_rate, 2),
    "total_sales": round(float(df["Sales"].sum()), 2),
    "total_order_item_total": round(float(df["Order_Item_Total"].sum()), 2),
    "total_benefit_per_order": round(float(df["Benefit_per_order"].sum()), 2),
    "total_profit_per_order": round(float(df["Order_Profit_Per_Order"].sum()), 2),
    "avg_days_shipping_real": round(float(df["Days_for_shipping_(real)"].mean()), 2),
    "avg_days_shipment_scheduled": round(float(df["Days_for_shipment_(scheduled)"].mean()), 2),
    "date_min": str(df["order_date"].min().date()),
    "date_max": str(df["order_date"].max().date()),
    "markets": int(df["Market"].nunique()),
    "departments": int(df["Department_Name"].nunique()),
    "categories": int(df["Category_Name"].nunique()),
    "product_description_missing_pct": round(float(100 * df["Product_Description"].isna().mean()), 2),
    "order_zipcode_missing_pct": round(float(100 * df["Order_Zipcode"].isna().mean()), 2),
}
with open(os.path.join(OUT, "kpis.txt"), "w") as f:
    for k, v in kpis.items():
        f.write(f"{k}: {v}\n")
print(kpis)

def late_table(group_col, out_name):
    t = (df.groupby(group_col).agg(orders=("Order_Id", "count"),
                                   late_orders=("Late_delivery_risk", "sum"),
                                   late_rate_pct=("Late_delivery_risk", lambda s: 100 * s.mean()),
                                   sales=("Sales", "sum"),
                                   profit=("Order_Profit_Per_Order", "sum"),
                                   avg_benefit=("Benefit_per_order", "mean"))
         .reset_index().sort_values("late_rate_pct", ascending=False))
    t.to_csv(os.path.join(OUT, out_name), index=False)
    return t

late_table("Market", "late_by_market.csv")
late_table("Shipping_Mode", "late_by_shipping_mode.csv")
late_table("Department_Name", "late_by_department.csv")
late_table("Category_Name", "late_by_category.csv")
late_table("Customer_Segment", "late_by_segment.csv")
late_table("Order_Region", "late_by_region.csv")
late_table("Order_Status", "late_by_order_status.csv")

# ---- LEAKAGE CHECK (the honest centrepiece) --------------------------------
ct = pd.crosstab(df["Delivery_Status"], df["Late_delivery_risk"], margins=True)
ct.to_csv(os.path.join(OUT, "leakage_check_delivery_status_x_late_risk.csv"))
print("Delivery_Status x Late_delivery_risk:\n", ct.to_string())
late_given_status = df.groupby("Delivery_Status")["Late_delivery_risk"].agg(["count", "mean"])
late_given_status["late_rate_pct"] = (late_given_status["mean"] * 100).round(2)
late_given_status.to_csv(os.path.join(OUT, "leakage_check_late_rate_by_delivery_status.csv"))

# What is knowable BEFORE shipping? Scheduled days, mode, market, department.
pre = (df.groupby("Days_for_shipment_(scheduled)").agg(
    orders=("Order_Id", "count"),
    late_rate_pct=("Late_delivery_risk", lambda s: 100 * s.mean()),
    avg_real_days=("Days_for_shipping_(real)", "mean")).reset_index())
pre.to_csv(os.path.join(OUT, "late_by_scheduled_days.csv"), index=False)

monthly = (df.groupby("order_month").agg(orders=("Order_Id", "count"),
                                         late_rate_pct=("Late_delivery_risk", lambda s: 100 * s.mean()),
                                         sales=("Sales", "sum"),
                                         profit=("Order_Profit_Per_Order", "sum"))
           .reset_index())
monthly.to_csv(os.path.join(OUT, "monthly_orders.csv"), index=False)

# Orders that lost money: negative benefit, by department
neg = df[df["Benefit_per_order"] < 0]
neg_by_dept = (neg.groupby("Department_Name").agg(loss_orders=("Order_Id", "count"),
                                                  total_benefit=("Benefit_per_order", "sum"))
               .reset_index().sort_values("total_benefit"))
neg_by_dept.to_csv(os.path.join(OUT, "loss_making_orders_by_department.csv"), index=False)
print(f"Loss-making orders (Benefit_per_order < 0): {len(neg)} "
      f"({100*len(neg)/len(df):.1f}%), total benefit USD {neg['Benefit_per_order'].sum():,.2f}")

with open(os.path.join(OUT, "reconciliation.txt"), "w") as f:
    f.write("DATACO — RECONCILIATION (computed from the real file, 2026-11-13)\n")
    f.write(f"Raw rows: {len(df)} | columns: {N_RAW_COLS}\n")
    f.write(f"Unique Order_Id: {df['Order_Id'].nunique()} (rows are order-line level; "
            f"one row per Order_Item_Id)\n")
    f.write(f"Late delivery rate (mean of Late_delivery_risk): {100*late_rate:.2f}%\n")
    f.write(f"Total Sales: {df['Sales'].sum():,.2f} | Total Order_Item_Total: {df['Order_Item_Total'].sum():,.2f}\n")
    f.write(f"Total Order_Profit_Per_Order: {df['Order_Profit_Per_Order'].sum():,.2f}\n")
    f.write("LEAKAGE: see leakage_check_*.csv — Delivery_Status 'Late delivery' rows are "
            "almost all Late_delivery_risk=1, and 'Advance shipping'/'Shipping on time' rows "
            "are almost all 0. Any model using Delivery_Status, Days_for_shipping_(real) or "
            "shipping_date as inputs is leaking the answer. Honest late-delivery analysis "
            "uses only information known at order time (scheduled days, shipping mode, "
            "market, department, category).\n")
    f.write("Dropped from clean file (PII / unusable): " + ", ".join(DROP) + "\n")
print("DONE — outputs in", OUT)
