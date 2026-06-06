"""
setup_db.py
Creates and populates the ecommerce SQLite database with mock data.
Tables: products, customers, orders, order_items, shipments
Run once: python setup_db.py
"""

import sqlite3
import json
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ecommerce.db")


# ──────────────────────────────────────────
# Schema
# ──────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    product_id          TEXT PRIMARY KEY,
    sku                 TEXT NOT NULL,
    name                TEXT NOT NULL,
    description         TEXT,
    category            TEXT,
    sub_category        TEXT,
    brand               TEXT,
    price               REAL,
    cost_price          REAL,
    weight_kg           REAL,
    dimensions_cm       TEXT,
    color               TEXT,
    material            TEXT,
    stock_quantity      INTEGER,
    warehouse_location  TEXT,
    supplier_id         TEXT,
    supplier_name       TEXT,
    reorder_level       INTEGER,
    is_active           INTEGER DEFAULT 1,
    average_rating      REAL,
    review_count        INTEGER,
    warranty_months     INTEGER,
    country_of_origin   TEXT,
    barcode             TEXT,
    tags                TEXT,
    created_at          TEXT,
    updated_at          TEXT
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id         TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    email               TEXT,
    phone               TEXT,
    shipping_address    TEXT,
    billing_address     TEXT,
    city                TEXT,
    state               TEXT,
    zip_code            TEXT,
    country             TEXT DEFAULT 'US',
    loyalty_tier        TEXT,
    loyalty_points      INTEGER DEFAULT 0,
    total_orders        INTEGER DEFAULT 0,
    total_spent         REAL DEFAULT 0.0,
    account_created_at  TEXT,
    last_login_at       TEXT,
    marketing_opt_in    INTEGER DEFAULT 1,
    internal_segment    TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    order_id            TEXT PRIMARY KEY,
    customer_id         TEXT,
    customer_name       TEXT,
    customer_email      TEXT,
    customer_phone      TEXT,
    shipping_address    TEXT,
    billing_address     TEXT,
    order_date          TEXT,
    order_status        TEXT,
    payment_method      TEXT,
    payment_status      TEXT,
    subtotal            REAL,
    tax_amount          REAL,
    shipping_fee        REAL,
    discount_amount     REAL DEFAULT 0.0,
    promo_code          TEXT,
    total_amount        REAL,
    shipping_method     TEXT,
    priority_flag       INTEGER DEFAULT 0,
    internal_ref        TEXT,
    warehouse_id        TEXT,
    notes               TEXT,
    created_at          TEXT,
    updated_at          TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    item_id             TEXT PRIMARY KEY,
    order_id            TEXT,
    product_id          TEXT,
    sku                 TEXT,
    product_name        TEXT,
    quantity            INTEGER,
    unit_price          REAL,
    total_price         REAL,
    weight_kg           REAL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS shipments (
    shipment_id         TEXT PRIMARY KEY,
    order_id            TEXT,
    carrier             TEXT,
    tracking_number     TEXT,
    shipping_method     TEXT,
    status              TEXT,
    origin_warehouse_id TEXT,
    origin_warehouse    TEXT,
    destination_address TEXT,
    estimated_dispatch  TEXT,
    actual_dispatch     TEXT,
    estimated_delivery  TEXT,
    actual_delivery     TEXT,
    last_known_location TEXT,
    last_update         TEXT,
    delay_reason        TEXT,
    delay_days          INTEGER DEFAULT 0,
    package_weight_kg   REAL,
    package_dimensions  TEXT,
    insurance_value     REAL,
    signature_required  INTEGER DEFAULT 0,
    delivery_attempts   INTEGER DEFAULT 0,
    carrier_notes       TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
"""


# ──────────────────────────────────────────
# Data
# ──────────────────────────────────────────

PRODUCTS = [
    ("PROD-001", "SKU-771", "Wireless Noise-Cancelling Headphones",
     "Premium over-ear headphones with active noise cancellation, 30-hour battery life, and foldable design.",
     "Electronics", "Audio", "SoundWave", 89.99, 34.50, 0.40, "18x16x8", "Matte Black",
     "ABS Plastic / Leather", 120, "WH-07-A3", "SUP-12", "AudioTech Supplies", 20,
     1, 4.6, 312, 24, "China", "0123456789012",
     "audio,wireless,noise-cancelling,headphones", "2023-06-01", "2024-01-15"),

    ("PROD-002", "SKU-203", "Silicone Phone Case — iPhone 15",
     "Slim-fit silicone case with microfibre lining. Drop-tested to 1.5m. Available in 6 colours.",
     "Accessories", "Phone Cases", "ShieldUp", 12.99, 3.20, 0.08, "15x7x1", "Midnight Blue",
     "Silicone", 450, "WH-03-B1", "SUP-07", "CaseCraft Ltd", 50,
     1, 4.4, 891, 12, "China", "0123456789013",
     "case,iphone,silicone,protection", "2023-08-10", "2024-02-01"),

    ("PROD-003", "SKU-409", "Mechanical Keyboard — TKL",
     "Tenkeyless mechanical keyboard with Cherry MX Brown switches, RGB backlight, and USB-C connection.",
     "Electronics", "Peripherals", "KeyForge", 129.99, 55.00, 0.95, "36x13x4", "Space Grey",
     "Aluminium / ABS", 75, "WH-07-C2", "SUP-15", "KeyMaster Wholesale", 15,
     1, 4.7, 204, 12, "Taiwan", "0123456789014",
     "keyboard,mechanical,RGB,gaming,office", "2023-05-20", "2024-01-28"),

    ("PROD-004", "SKU-512", "USB-C Charging Hub — 7 Port",
     "Compact 7-in-1 USB-C hub with 4K HDMI, 3x USB-A 3.0, SD card reader, and 100W PD pass-through.",
     "Electronics", "Connectivity", "HubMax", 49.99, 18.75, 0.22, "12x5x2", "Silver",
     "Aluminium", 200, "WH-07-A1", "SUP-09", "TechHub Imports", 30,
     1, 4.5, 567, 12, "China", "0123456789015",
     "usb-c,hub,adapter,connectivity", "2023-07-14", "2024-01-10"),

    ("PROD-005", "SKU-617", "Ergonomic Desk Chair",
     "Fully adjustable mesh office chair with lumbar support, 4D armrests, and breathable back panel.",
     "Furniture", "Seating", "PosturePro", 349.99, 145.00, 18.50, "67x65x120", "Charcoal Grey",
     "Mesh / Steel", 30, "WH-02-D4", "SUP-03", "OfficeFit Corp", 5,
     1, 4.3, 128, 36, "Vietnam", "0123456789016",
     "chair,ergonomic,office,furniture,seating", "2023-04-01", "2024-02-05"),

    ("PROD-006", "SKU-734", "Stainless Steel Water Bottle — 1L",
     "Double-wall vacuum insulated bottle. Keeps drinks cold 24hrs, hot 12hrs. BPA-free.",
     "Lifestyle", "Hydration", "HydroCore", 34.99, 10.50, 0.35, "28x8x8", "Forest Green",
     "18/8 Stainless Steel", 310, "WH-05-B2", "SUP-11", "EcoBottle Supply", 40,
     1, 4.8, 1204, 0, "South Korea", "0123456789017",
     "water bottle,insulated,eco,hydration", "2023-03-15", "2024-01-20"),

    ("PROD-007", "SKU-821", "Laptop Stand — Adjustable Aluminium",
     "Height-adjustable aluminium laptop stand. Foldable and portable. Fits laptops up to 17 inches.",
     "Electronics", "Accessories", "ElevateDesk", 39.99, 13.00, 0.48, "26x22x3", "Silver",
     "Aluminium", 180, "WH-07-B3", "SUP-09", "TechHub Imports", 25,
     1, 4.6, 447, 12, "China", "0123456789018",
     "laptop stand,ergonomic,portable,aluminium", "2023-09-01", "2024-02-10"),

    ("PROD-008", "SKU-935", "Wireless Charging Pad — 15W",
     "Qi-certified wireless charger compatible with iPhone 12+ and Android. LED indicator, non-slip base.",
     "Electronics", "Charging", "ChargeFlow", 24.99, 8.25, 0.15, "10x10x1", "White",
     "ABS Plastic", 260, "WH-07-A2", "SUP-12", "AudioTech Supplies", 35,
     1, 4.2, 339, 12, "China", "0123456789019",
     "wireless charging,qi,iphone,android", "2023-08-25", "2024-01-30"),

    ("PROD-009", "SKU-1041", "Merino Wool Crew Neck Sweater",
     "100% merino wool crew neck. Naturally temperature regulating and odour resistant. Machine washable.",
     "Clothing", "Tops", "WoolCraft", 79.99, 28.00, 0.45, "N/A", "Navy",
     "100% Merino Wool", 95, "WH-04-A1", "SUP-06", "WoolWorks NZ", 15,
     1, 4.7, 88, 0, "New Zealand", "0123456789020",
     "sweater,merino,wool,knitwear,clothing", "2023-10-01", "2024-02-01"),

    ("PROD-010", "SKU-1158", "LED Desk Lamp — Wireless Charging Base",
     "Touch-dimmable LED lamp with 5 colour temperatures. Built-in 10W wireless charging base. USB-A port.",
     "Lighting", "Desk Lamps", "LumiDesk", 59.99, 22.00, 0.80, "14x14x45", "White",
     "ABS Plastic / Steel", 140, "WH-07-C1", "SUP-14", "LightSource Trading", 20,
     1, 4.5, 276, 12, "China", "0123456789021",
     "lamp,LED,desk,wireless charging,lighting", "2023-07-20", "2024-01-25"),

    ("PROD-011", "SKU-1267", "Foam Yoga Mat — 6mm",
     "High-density non-slip foam yoga mat. Includes carrying strap. 183cm x 61cm.",
     "Sports", "Yoga", "FlexCore", 29.99, 9.50, 1.10, "183x61x0.6", "Purple",
     "NBR Foam", 200, "WH-05-C3", "SUP-08", "ActiveGear Supply", 30,
     1, 4.4, 512, 0, "China", "0123456789022",
     "yoga,mat,fitness,exercise,non-slip", "2023-06-10", "2024-01-15"),

    ("PROD-012", "SKU-1389", "Smart LED Strip Lights — 5m",
     "Wi-Fi enabled RGB LED strip. App and voice control (Alexa/Google). Music sync mode. Cuttable every 3 LEDs.",
     "Lighting", "Smart Lighting", "GlowTech", 44.99, 16.50, 0.30, "N/A", "Multicolour",
     "LED / Adhesive Backing", 165, "WH-07-C1", "SUP-14", "LightSource Trading", 25,
     1, 4.3, 398, 12, "China", "0123456789023",
     "LED,smart,RGB,strip lights,alexa,google", "2023-08-05", "2024-02-12"),
]

CUSTOMERS = [
    ("CUST-9921", "James Miller", "james.miller@email.com", "555-0192",
     "142 Birchwood Lane, Austin TX 78701", "142 Birchwood Lane, Austin TX 78701",
     "Austin", "TX", "78701", "US", "Silver", 240, 4, 289.94,
     "2022-11-03", "2024-01-28", 1, "mid_value"),

    ("CUST-4432", "Sarah Chen", "sarah.chen@email.com", "555-0847",
     "88 Maple Ave, Seattle WA 98101", "88 Maple Ave, Seattle WA 98101",
     "Seattle", "WA", "98101", "US", "Gold", 1450, 12, 1243.80,
     "2021-06-15", "2024-01-30", 1, "high_value"),

    ("CUST-7751", "Marcus Johnson", "marcus.j@email.com", "555-0334",
     "21 Oak Street, Chicago IL 60601", "21 Oak Street, Chicago IL 60601",
     "Chicago", "IL", "60601", "US", "Bronze", 90, 2, 114.98,
     "2023-09-20", "2024-01-15", 0, "low_value"),

    ("CUST-3318", "Priya Patel", "priya.patel@email.com", "555-0561",
     "505 Elm Road, New York NY 10001", "505 Elm Road, New York NY 10001",
     "New York", "NY", "10001", "US", "Platinum", 3200, 27, 3489.73,
     "2020-03-10", "2024-01-31", 1, "vip"),

    ("CUST-6609", "Tom Eriksen", "tom.eriksen@email.com", "555-0712",
     "9 Cedar Drive, Portland OR 97201", "9 Cedar Drive, Portland OR 97201",
     "Portland", "OR", "97201", "US", "Silver", 380, 6, 524.91,
     "2022-08-22", "2024-01-27", 1, "mid_value"),

    ("CUST-2247", "Lisa Nguyen", "lisa.nguyen@email.com", "555-0983",
     "330 Pine Blvd, Denver CO 80201", "330 Pine Blvd, Denver CO 80201",
     "Denver", "CO", "80201", "US", "Bronze", 60, 1, 79.99,
     "2023-12-01", "2024-01-22", 1, "new"),

    ("CUST-8834", "Daniel Ruiz", "d.ruiz@email.com", "555-0258",
     "17 Willow Court, Miami FL 33101", "17 Willow Court, Miami FL 33101",
     "Miami", "FL", "33101", "US", "Gold", 920, 9, 899.82,
     "2021-11-18", "2024-01-29", 0, "high_value"),
]

# order_id, customer_id, order_date, status, payment_method, payment_status,
# subtotal, tax, shipping_fee, discount, promo_code, total, shipping_method,
# priority, internal_ref, warehouse_id, notes
ORDERS_RAW = [
    ("ORD-48291", "CUST-9921", "James Miller", "james.miller@email.com", "555-0192",
     "142 Birchwood Lane, Austin TX 78701", "142 Birchwood Lane, Austin TX 78701",
     "2024-01-28T09:14:32Z", "delayed", "visa_ending_4421", "paid",
     115.97, 9.54, 5.99, 0.0, None, 131.50, "standard", 0,
     "INT-REF-48291", "WH-07", None),

    ("ORD-51042", "CUST-4432", "Sarah Chen", "sarah.chen@email.com", "555-0847",
     "88 Maple Ave, Seattle WA 98101", "88 Maple Ave, Seattle WA 98101",
     "2024-01-30T14:22:10Z", "in_transit", "mastercard_ending_7823", "paid",
     179.98, 14.76, 0.0, 0.0, None, 194.74, "express", 0,
     "INT-REF-51042", "WH-07", None),

    ("ORD-52887", "CUST-7751", "Marcus Johnson", "marcus.j@email.com", "555-0334",
     "21 Oak Street, Chicago IL 60601", "21 Oak Street, Chicago IL 60601",
     "2024-01-31T10:05:00Z", "delivered", "paypal", "paid",
     49.99, 4.12, 5.99, 0.0, None, 60.10, "standard", 0,
     "INT-REF-52887", "WH-07", None),

    ("ORD-53601", "CUST-3318", "Priya Patel", "priya.patel@email.com", "555-0561",
     "505 Elm Road, New York NY 10001", "505 Elm Road, New York NY 10001",
     "2024-02-01T08:30:00Z", "processing", "amex_ending_1122", "paid",
     429.98, 35.27, 0.0, 43.00, "LOYAL10", 422.25, "express", 1,
     "INT-REF-53601", "WH-02", "VIP customer — priority handling"),

    ("ORD-54112", "CUST-6609", "Tom Eriksen", "tom.eriksen@email.com", "555-0712",
     "9 Cedar Drive, Portland OR 97201", "9 Cedar Drive, Portland OR 97201",
     "2024-01-29T16:45:00Z", "delivered", "visa_ending_3309", "paid",
     64.98, 5.34, 5.99, 0.0, None, 76.31, "standard", 0,
     "INT-REF-54112", "WH-05", None),

    ("ORD-54899", "CUST-2247", "Lisa Nguyen", "lisa.nguyen@email.com", "555-0983",
     "330 Pine Blvd, Denver CO 80201", "330 Pine Blvd, Denver CO 80201",
     "2024-01-22T11:20:00Z", "delivered", "visa_ending_6677", "paid",
     79.99, 6.58, 5.99, 0.0, None, 92.56, "standard", 0,
     "INT-REF-54899", "WH-04", None),

    ("ORD-55234", "CUST-8834", "Daniel Ruiz", "d.ruiz@email.com", "555-0258",
     "17 Willow Court, Miami FL 33101", "17 Willow Court, Miami FL 33101",
     "2024-02-01T13:10:00Z", "in_transit", "mastercard_ending_4451", "paid",
     114.97, 9.45, 5.99, 11.50, "SAVE10", 118.91, "standard", 0,
     "INT-REF-55234", "WH-07", None),

    ("ORD-55891", "CUST-4432", "Sarah Chen", "sarah.chen@email.com", "555-0847",
     "88 Maple Ave, Seattle WA 98101", "88 Maple Ave, Seattle WA 98101",
     "2024-02-02T09:00:00Z", "processing", "mastercard_ending_7823", "paid",
     349.99, 28.74, 0.0, 0.0, None, 378.73, "express", 0,
     "INT-REF-55891", "WH-02", None),

    ("ORD-56010", "CUST-9921", "James Miller", "james.miller@email.com", "555-0192",
     "142 Birchwood Lane, Austin TX 78701", "142 Birchwood Lane, Austin TX 78701",
     "2024-01-10T10:00:00Z", "delivered", "visa_ending_4421", "paid",
     39.99, 3.28, 5.99, 0.0, None, 49.26, "standard", 0,
     "INT-REF-56010", "WH-07", None),

    ("ORD-56421", "CUST-3318", "Priya Patel", "priya.patel@email.com", "555-0561",
     "505 Elm Road, New York NY 10001", "505 Elm Road, New York NY 10001",
     "2024-01-15T14:00:00Z", "cancelled", "amex_ending_1122", "refunded",
     129.99, 0.0, 0.0, 0.0, None, 129.99, "standard", 0,
     "INT-REF-56421", "WH-07", "Customer requested cancellation before dispatch"),
]

# (item_id, order_id, product_id, sku, product_name, qty, unit_price, total_price, weight)
ORDER_ITEMS = [
    ("ITEM-001", "ORD-48291", "PROD-001", "SKU-771", "Wireless Noise-Cancelling Headphones", 1, 89.99, 89.99, 0.40),
    ("ITEM-002", "ORD-48291", "PROD-002", "SKU-203", "Silicone Phone Case — iPhone 15", 2, 12.99, 25.98, 0.16),
    ("ITEM-003", "ORD-51042", "PROD-007", "SKU-821", "Laptop Stand — Adjustable Aluminium", 1, 39.99, 39.99, 0.48),
    ("ITEM-004", "ORD-51042", "PROD-010", "SKU-1158", "LED Desk Lamp — Wireless Charging Base", 1, 59.99, 59.99, 0.80),
    ("ITEM-005", "ORD-51042", "PROD-008", "SKU-935", "Wireless Charging Pad — 15W", 1, 24.99, 24.99, 0.15),
    ("ITEM-006", "ORD-51042", "PROD-002", "SKU-203", "Silicone Phone Case — iPhone 15", 2, 12.99, 25.98, 0.16),
    ("ITEM-007", "ORD-52887", "PROD-004", "SKU-512", "USB-C Charging Hub — 7 Port", 1, 49.99, 49.99, 0.22),
    ("ITEM-008", "ORD-53601", "PROD-005", "SKU-617", "Ergonomic Desk Chair", 1, 349.99, 349.99, 18.50),
    ("ITEM-009", "ORD-53601", "PROD-011", "SKU-1267", "Foam Yoga Mat — 6mm", 1, 29.99, 29.99, 1.10),
    ("ITEM-010", "ORD-53601", "PROD-008", "SKU-935", "Wireless Charging Pad — 15W", 1, 24.99, 24.99, 0.15),
    ("ITEM-011", "ORD-54112", "PROD-006", "SKU-734", "Stainless Steel Water Bottle — 1L", 1, 34.99, 34.99, 0.35),
    ("ITEM-012", "ORD-54112", "PROD-011", "SKU-1267", "Foam Yoga Mat — 6mm", 1, 29.99, 29.99, 1.10),
    ("ITEM-013", "ORD-54899", "PROD-009", "SKU-1041", "Merino Wool Crew Neck Sweater", 1, 79.99, 79.99, 0.45),
    ("ITEM-014", "ORD-55234", "PROD-012", "SKU-1389", "Smart LED Strip Lights — 5m", 1, 44.99, 44.99, 0.30),
    ("ITEM-015", "ORD-55234", "PROD-008", "SKU-935", "Wireless Charging Pad — 15W", 1, 24.99, 24.99, 0.15),
    ("ITEM-016", "ORD-55234", "PROD-004", "SKU-512", "USB-C Charging Hub — 7 Port", 1, 49.99, 49.99, 0.22),
    ("ITEM-017", "ORD-55891", "PROD-005", "SKU-617", "Ergonomic Desk Chair", 1, 349.99, 349.99, 18.50),
    ("ITEM-018", "ORD-56010", "PROD-007", "SKU-821", "Laptop Stand — Adjustable Aluminium", 1, 39.99, 39.99, 0.48),
    ("ITEM-019", "ORD-56421", "PROD-003", "SKU-409", "Mechanical Keyboard — TKL", 1, 129.99, 129.99, 0.95),
]

# (shipment_id, order_id, carrier, tracking_number, shipping_method, status,
#  warehouse_id, warehouse_name, destination,
#  est_dispatch, actual_dispatch, est_delivery, actual_delivery,
#  last_location, last_update, delay_reason, delay_days,
#  weight, dimensions, insurance, signature, attempts, notes)
SHIPMENTS = [
    ("SHIP-7291", "ORD-48291", "FedEx", None, "standard", "delayed",
     "WH-07", "Austin Fulfillment Center", "142 Birchwood Lane, Austin TX 78701",
     "2024-01-29T00:00:00Z", None, "2024-02-03T00:00:00Z", None,
     "Austin Fulfillment Center", "2024-01-30T14:22:10Z",
     "warehouse_backlog", 3, 1.16, "28x22x12cm", 131.50, 0, 0,
     "Held at origin warehouse due to backlog. Expected dispatch 2024-02-03."),

    ("SHIP-7842", "ORD-51042", "UPS", "1Z999AA10123456784", "express", "in_transit",
     "WH-07", "Austin Fulfillment Center", "88 Maple Ave, Seattle WA 98101",
     "2024-01-30T00:00:00Z", "2024-01-30T18:00:00Z", "2024-02-01T00:00:00Z", None,
     "Salt Lake City, UT", "2024-01-31T20:15:00Z",
     None, 0, 1.59, "35x28x18cm", 194.74, 0, 0,
     "On schedule. Last scan: Salt Lake City sorting facility."),

    ("SHIP-7901", "ORD-52887", "USPS", "9400111899223397613", "standard", "delivered",
     "WH-07", "Austin Fulfillment Center", "21 Oak Street, Chicago IL 60601",
     "2024-02-01T00:00:00Z", "2024-02-01T09:00:00Z", "2024-02-05T00:00:00Z", "2024-02-04T14:30:00Z",
     "Chicago, IL — Delivered", "2024-02-04T14:30:00Z",
     None, 0, 0.47, "20x16x10cm", 60.10, 0, 0,
     "Delivered to front door."),

    ("SHIP-8012", "ORD-53601", "FedEx", None, "express", "processing",
     "WH-02", "New York Fulfillment Center", "505 Elm Road, New York NY 10001",
     "2024-02-02T00:00:00Z", None, "2024-02-04T00:00:00Z", None,
     "New York Fulfillment Center", "2024-02-02T08:30:00Z",
     None, 0, 19.75, "70x68x45cm", 422.25, 1, 0,
     "Priority order. Awaiting packing — large item (chair). Signature required on delivery."),

    ("SHIP-8103", "ORD-54112", "USPS", "9400111899223398827", "standard", "delivered",
     "WH-05", "Denver Fulfillment Center", "9 Cedar Drive, Portland OR 97201",
     "2024-01-30T00:00:00Z", "2024-01-30T11:00:00Z", "2024-02-03T00:00:00Z", "2024-02-02T13:45:00Z",
     "Portland, OR — Delivered", "2024-02-02T13:45:00Z",
     None, 0, 1.45, "32x25x12cm", 76.31, 0, 0, None),

    ("SHIP-8241", "ORD-54899", "UPS", "1Z999AA10123456801", "standard", "delivered",
     "WH-04", "Los Angeles Fulfillment Center", "330 Pine Blvd, Denver CO 80201",
     "2024-01-23T00:00:00Z", "2024-01-23T14:00:00Z", "2024-01-27T00:00:00Z", "2024-01-26T16:00:00Z",
     "Denver, CO — Delivered", "2024-01-26T16:00:00Z",
     None, 0, 0.45, "35x28x8cm", 92.56, 0, 0, None),

    ("SHIP-8390", "ORD-55234", "FedEx", "274899004297914", "standard", "in_transit",
     "WH-07", "Austin Fulfillment Center", "17 Willow Court, Miami FL 33101",
     "2024-02-02T00:00:00Z", "2024-02-02T10:30:00Z", "2024-02-06T00:00:00Z", None,
     "Orlando, FL", "2024-02-02T22:10:00Z",
     None, 0, 0.67, "25x20x15cm", 118.91, 0, 0,
     "In transit. Last scan: Orlando distribution hub."),

    ("SHIP-8451", "ORD-55891", "FedEx", None, "express", "processing",
     "WH-02", "New York Fulfillment Center", "88 Maple Ave, Seattle WA 98101",
     "2024-02-03T00:00:00Z", None, "2024-02-05T00:00:00Z", None,
     "New York Fulfillment Center", "2024-02-02T09:00:00Z",
     None, 0, 18.50, "70x68x45cm", 378.73, 0, 0, None),

    ("SHIP-8502", "ORD-56010", "USPS", "9400111899223397544", "standard", "delivered",
     "WH-07", "Austin Fulfillment Center", "142 Birchwood Lane, Austin TX 78701",
     "2024-01-11T00:00:00Z", "2024-01-11T10:00:00Z", "2024-01-15T00:00:00Z", "2024-01-14T15:20:00Z",
     "Austin, TX — Delivered", "2024-01-14T15:20:00Z",
     None, 0, 0.48, "28x24x5cm", 49.26, 0, 0, None),
]


# ──────────────────────────────────────────
# Build
# ──────────────────────────────────────────

def build_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(SCHEMA)

    cur.executemany("""
        INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, PRODUCTS)

    cur.executemany("""
        INSERT INTO customers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, CUSTOMERS)

    for row in ORDERS_RAW:
        cur.execute("""
            INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, row + ("2024-01-28T09:00:00Z", "2024-01-31T00:00:00Z"))

    cur.executemany("""
        INSERT INTO order_items VALUES (?,?,?,?,?,?,?,?,?)
    """, ORDER_ITEMS)

    cur.executemany("""
        INSERT INTO shipments VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, SHIPMENTS)

    conn.commit()
    conn.close()
    print(f"Database created at: {DB_PATH}")
    print(f"  products:    {len(PRODUCTS)} rows")
    print(f"  customers:   {len(CUSTOMERS)} rows")
    print(f"  orders:      {len(ORDERS_RAW)} rows")
    print(f"  order_items: {len(ORDER_ITEMS)} rows")
    print(f"  shipments:   {len(SHIPMENTS)} rows")


if __name__ == "__main__":
    build_db()
