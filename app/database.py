# database.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "amazon.db")


def get_connection():
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    # ================= USERS TABLE =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,   -- s.no
        name TEXT,                              -- username
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    # ================= PRODUCTS TABLE =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,                 -- s.no
        title TEXT,
        price INTEGER,
        category TEXT,
        image TEXT,
        description TEXT,
        features TEXT
    )
    """)

    # ================= USER HISTORY TABLE =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,   -- s.no
        user_id INTEGER,
        username TEXT,                          -- ✅ NEW
        product_id INTEGER,
        viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ================= INSERT PRODUCTS =================
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    if count == 0:

        products = [

# -------- DEALS --------

(1,"Noise Smart Watch",1999,"deals","https://www.hindustantimes.com/ht-img/img/2023/10/07/400x225/amazon_sale_2023_smartwatches_1696688913776_1696688937601.JPG",
"Premium smartwatch with modern design",
"Bluetooth Calling,Heart Rate Monitor,Long Battery Life,Water Resistant,Touch Display"),

(2,"JEE ADVANCED physics pyq",700,"deals","https://gkpublications.com/cdn/shop/files/JEEAdvancedPhysicsPYQ2026Front.jpg?v=1772688201&width=690",
"Best book for JEE Advanced preparation",
"Previous Year Questions,Detailed Solutions,Latest Pattern,Concept Clarity,High Quality Print"),

(3,"Boat Power Bank",899,"deals","https://rukminim2.flixcart.com/image/720/720/xif0q/power-bank/c/h/9/-original-imahdthbvgdtjzuy.jpeg?q=90",
"Fast charging power bank",
"10000mAh Capacity,Fast Charging,Compact Design,LED Indicator,Durable Build"),

(4,"LG Air Conditioner",34290,"deals","https://rukminim2.flixcart.com/image/720/720/xif0q/air-conditioner-new/z/g/t/-original-imahh8b86cyhevqj.jpeg?q=90",
"Energy efficient AC",
"Inverter Technology,Low Noise,Fast Cooling,Energy Saving,Remote Control"),

(5,"Logitech Keyboard",1499,"deals","https://m.media-amazon.com/images/I/61pUul1oDlL._SL1500_.jpg",
"Wireless keyboard for daily use",
"Ergonomic Design,Wireless,Long Battery,Silent Keys,Compact Size"),

(6,"Classic Black shirt",2199,"deals","https://www.jiomart.com/images/product/original/rvdtynnjc7/baleshwar-man-s-solid-slim-fit-casual-shirt-for-men-shirts-bk-xxxl-product-images-rvdtynnjc7-0-202304221429.jpg?im=Resize=(500,630)",
"Stylish black shirt",
"Cotton Fabric,Slim Fit,Comfort Wear,Easy Wash,Durable"),

(7,"Nike Shoes",1199,"deals","https://di2ponv0v5otw.cloudfront.net/posts/2023/03/23/641cd791a0aeb7aabe388eb0/m_641cd8ff253a8cb00b7684e3.jpg",
"Comfortable sports shoes",
"Lightweight,Running Support,Stylish,Durable Sole,Breathable"),

(8,"SG Cricket Kit",5000,"deals","https://rukminim2.flixcart.com/image/720/720/k2jbyq80/kit/x/w/d/academy-set-of-6-no-ideal-for-11-14-years-complete-sg-89219898-original-imafhvhb8gathd2y.jpeg?q=90",
"Complete cricket kit",
"Bat,Ball,Pads,Gloves,Helmet"),

(9,"Travel Bag",3999,"deals","https://rukminim2.flixcart.com/image/720/720/xif0q/rucksack/y/y/y/water-resistance-trekking-hiking-travel-bag-with-shoe-original-imaha2zkyze5ydyp.jpeg?q=90",
"Large travel backpack",
"Water Resistant,Multiple Compartments,Strong Zip,Comfort Straps,Lightweight"),

(10,"Voltas Refrigerator",14899,"deals","https://swapnainfotech.com/cdn/shop/files/W0FWE0M0B00GO.jpg?v=1737456159&width=600",
"Compact fridge",
"Energy Efficient,Silent Cooling,Durable,Fast Freeze,Low Power"),

# -------- RECOMMENDED --------

(11,"Apple iPhone 14",69999,"recommended","https://m.media-amazon.com/images/I/61cwywLZR-L._SL1500_.jpg",
"Latest Apple smartphone",
"A15 Chip,Great Camera,Face ID,Premium Build,iOS"),

(12,"Samsung Galaxy S23",74999,"recommended","https://m.media-amazon.com/images/I/71CXhVhpM0L._SL1500_.jpg",
"Flagship Samsung phone",
"Snapdragon Processor,AMOLED Display,Fast Charging,Camera Pro Mode,5G"),

(13,"Whirlpool Washing Machine",31990,"recommended","https://rukminim2.flixcart.com/image/720/720/xif0q/washing-machine-new/t/h/t/-original-imahk3tzbpaxtc62.jpeg?q=90",
"Automatic washing machine",
"9kg Capacity,Auto Wash,Quick Dry,Energy Efficient,Silent"),

(14,"Dell Laptop",55999,"recommended","https://m.media-amazon.com/images/I/61Dw5Z8LzJL._SL1500_.jpg",
"Powerful laptop",
"Intel Processor,SSD Storage,Lightweight,Long Battery,HD Display"),

(15,"Sony Bravia TV",59999,"recommended","https://m.media-amazon.com/images/I/81wxS8abrgL._SL1500_.jpg",
"Smart LED TV",
"4K Display,Android TV,Dolby Audio,WiFi,Voice Control"),

(16,"CSK Jersey",450,"recommended","https://www.chennaisuperkings.com/shop/_next/image?url=https%3A%2F%2Fstore.chennaisuperkings.com%2F%2Fmedia%2Fcatalog%2Fproduct%2F%2F1%2F_%2F1_2_9.png&w=750&q=75",
"Cricket jersey",
"Team Logo,Comfort Fit,Lightweight,Durable,Stylish"),

(17,"Panasonic Mixer",4999,"recommended","https://jamesandco.in/wp-content/uploads/2024/09/panasonic-mx-ac460-original-imafux93zzvxhefu_Copy_702ac507-1895-4c34-a4f3-0d064bf21e20.jpg",
"Kitchen mixer",
"High Power,Multiple Jars,Durable Motor,Easy Clean,Compact"),

(18,"Arduino Uno",500,"recommended","https://cdn.sparkfun.com/assets/9/1/e/4/8/515b4656ce395f8a38000000.png",
"Microcontroller board",
"ATmega328,USB Powered,Beginner Friendly,Open Source,Low Cost"),

(19,"Havells Cooler",19999,"recommended","https://havells.com/media/catalog/product/cache/844a913d283fe95e56e39582c5f2767b/g/h/ghracdwe3451_1_.jpg",
"Air cooler",
"Large Tank,Powerful Fan,Energy Efficient,Low Noise,Remote"),

(20,"India Jersey",499,"recommended","https://www.nextprint.in/cdn/shop/files/51wY94bfDRL._SX569_800x.jpg?v=1765976163",
"Team India jersey",
"Breathable Fabric,Stylish,Comfort Fit,Lightweight,Durable")

        ]

        cursor.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?)",
            products
        )

    conn.commit()
    conn.close()
