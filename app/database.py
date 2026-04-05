import sqlite3
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "amazon.db")


def get_connection():
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def to_ist(time_str):
    if not time_str:
        return None
    try:
        utc_time = datetime.fromisoformat(time_str)
        ist_time = utc_time + timedelta(hours=5, minutes=30)
        return ist_time.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return time_str


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ================= USERS =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user'
    )
    """)

    # ================= PRODUCTS =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        title TEXT,
        price INTEGER,
        category TEXT,
        image TEXT,
        description TEXT,
        features TEXT
    )
    """)

    # ================= USER HISTORY =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        product_id INTEGER,
        viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ================= ORDERS =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        product_id INTEGER,
        quantity INTEGER DEFAULT 1,
        status TEXT DEFAULT 'placed',
        invoice_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ================= ORDER TIMELINE =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ================= ADDRESS =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS addresses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        address TEXT,
        pincode TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ================= INVOICE =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        address TEXT,
        pincode TEXT,
        total_amount REAL,
        payment_mode TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ================= ADD MISSING COLUMNS =================
    # Check if 'invoice_id' exists in orders
    cursor.execute("PRAGMA table_info(orders)")
    columns = [col[1] for col in cursor.fetchall()]
    if "invoice_id" not in columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN invoice_id INTEGER")

    # ================= INSERT DEFAULT PRODUCTS =================
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    if count == 0:
        products = [
            (1,"Noise Smart Watch",1999,"deals","https://www.hindustantimes.com/ht-img/img/2023/10/07/400x225/amazon_sale_2023_smartwatches_1696688913776_1696688937601.JPG","Premium smartwatch","Bluetooth Calling,Heart Rate Monitor,Long Battery Life"),
            (2,"JEE Advanced Physics PYQ",700,"deals","https://gkpublications.com/cdn/shop/files/JEEAdvancedPhysicsPYQ2026Front.jpg?v=1772688201&width=690","Best book","PYQs,Concept Clarity"),
            (3,"Boat Power Bank",899,"deals","https://rukminim2.flixcart.com/image/720/720/xif0q/power-bank/c/h/9/-original-imahdthbvgdtjzuy.jpeg?q=90","Fast charging","10000mAh,Fast Charging"),
            (4,"LG Air Conditioner",34290,"deals","https://rukminim2.flixcart.com/image/720/720/xif0q/air-conditioner-new/z/g/t/-original-imahh8b86cyhevqj.jpeg?q=90","Energy efficient","Inverter,Fast Cooling"),
            (5,"Logitech Keyboard",1499,"deals","https://m.media-amazon.com/images/I/61pUul1oDlL._SL1500_.jpg","Wireless keyboard","Silent Keys"),
            (6,"Black Shirt",2199,"deals","https://www.jiomart.com/images/product/original/rvdtynnjc7/baleshwar-man-s-solid-slim-fit-casual-shirt-for-men-shirts-bk-xxxl-product-images-rvdtynnjc7-0-202304221429.jpg","Stylish","Cotton,Slim Fit"),
            (7,"Nike Shoes",1199,"deals","https://di2ponv0v5otw.cloudfront.net/posts/2023/03/23/641cd791a0aeb7aabe388eb0/m_641cd8ff253a8cb00b7684e3.jpg","Comfortable","Lightweight"),
            (8,"SG Cricket Kit",5000,"deals","https://rukminim2.flixcart.com/image/720/720/k2jbyq80/kit/x/w/d/academy-set-of-6-no-ideal-for-11-14-years-complete-sg-89219898-original-imafhvhb8gathd2y.jpeg?q=90","Complete kit","Bat,Ball,Pads"),
            (9,"Travel Bag",3999,"deals","https://rukminim2.flixcart.com/image/720/720/xif0q/rucksack/y/y/y/water-resistance-trekking-hiking-travel-bag-with-shoe-original-imaha2zkyze5ydyp.jpeg?q=90","Large bag","Water Resistant"),
            (10,"Voltas Refrigerator",14899,"deals","https://swapnainfotech.com/cdn/shop/files/W0FWE0M0B00GO.jpg?v=1737456159&width=600","Compact fridge","Energy Efficient"),
            (11,"Apple iPhone 14",69999,"recommended","https://m.media-amazon.com/images/I/61cwywLZR-L._SL1500_.jpg","Latest iPhone","A15 Chip"),
            (12,"Samsung Galaxy S23",74999,"recommended","https://m.media-amazon.com/images/I/71CXhVhpM0L._SL1500_.jpg","Flagship phone","AMOLED,5G"),
            (13,"Whirlpool Washing Machine",31990,"recommended","https://rukminim2.flixcart.com/image/720/720/xif0q/washing-machine-new/t/h/t/-original-imahk3tzbpaxtc62.jpeg?q=90","Automatic","9kg"),
            (14,"Dell Laptop",55999,"recommended","https://m.media-amazon.com/images/I/61Dw5Z8LzJL._SL1500_.jpg","Powerful laptop","SSD"),
            (15,"Sony Bravia TV",59999,"recommended","https://m.media-amazon.com/images/I/81wxS8abrgL._SL1500_.jpg","Smart TV","4K"),
            (16,"CSK Jersey",450,"recommended","https://www.nextprint.in/cdn/shop/files/51wY94bfDRL._SX569.jpg","Cricket jersey","Comfort Fit"),
            (17,"Panasonic Mixer",4999,"recommended","https://assets.nikshanonline.com/wp-content/uploads/2022/11/onam-saleonam-2023onam-mixi-offersonam-mixi-saleonam-discountonam-offers-at-nikshan.png","Kitchen mixer","Durable"),
            (18,"Arduino Uno",500,"recommended","https://cdn.sparkfun.com/assets/9/1/e/4/8/515b4656ce395f8a38000000.png","Microcontroller","Beginner Friendly"),
            (19,"Havells Cooler",19999,"recommended","https://havells.com/media/catalog/product/cache/844a913d283fe95e56e39582c5f2767b/g/h/ghracdwe3451_3_.jpg","Air cooler","Low Noise"),
            (20,"India Jersey",499,"recommended","https://www.nextprint.in/cdn/shop/files/51wY94bfDRL._SX569.jpg","Team jersey","Breathable")
        ]
        cursor.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?)",
            products
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully")
