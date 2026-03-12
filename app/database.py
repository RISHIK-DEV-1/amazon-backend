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

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # Products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        price INTEGER NOT NULL,
        category TEXT NOT NULL,
        image TEXT NOT NULL
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    if count == 0:

        products = [
            (1,"Noise Smart Watch",1999,"deals","https://m.media-amazon.com/images/I/61TapeOXotL._SL1500_.jpg"),
            (2,"boAt Rockerz 255",1299,"deals","https://m.media-amazon.com/images/I/61u1VALn6JL._SL1500_.jpg"),
            (3,"Redmi Power Bank",899,"deals","https://m.media-amazon.com/images/I/71lVwl3q-kL._SL1500_.jpg"),
            (4,"HP Wireless Mouse",599,"deals","https://m.media-amazon.com/images/I/61mkcnh0xVL._SL1500_.jpg"),
            (5,"Logitech Keyboard",1499,"deals","https://m.media-amazon.com/images/I/61pUul1oDlL._SL1500_.jpg"),
            (6,"Samsung 25W Charger",1199,"deals","https://m.media-amazon.com/images/I/51S6JXKc-9L._SL1500_.jpg"),
            (7,"Mi USB Cable",299,"deals","https://m.media-amazon.com/images/I/51Lk7h4rDEL._SL1500_.jpg"),
            (8,"boAt Stone Speaker",1799,"deals","https://m.media-amazon.com/images/I/71nL5GZ9R-L._SL1500_.jpg"),
            (9,"Sony Wired Headphones",999,"deals","https://m.media-amazon.com/images/I/61kFL7ywsZS._SL1500_.jpg"),
            (10,"AmazonBasics Tripod",899,"deals","https://m.media-amazon.com/images/I/61pVtPaTk-L._SL1500_.jpg"),

            (11,"Apple iPhone 14",69999,"recommended","https://m.media-amazon.com/images/I/61bK6PMOC3L._SL1500_.jpg"),
            (12,"Samsung Galaxy S23",74999,"recommended","https://m.media-amazon.com/images/I/71CXhVhpM0L._SL1500_.jpg"),
            (13,"MacBook Air M1",89999,"recommended","https://m.media-amazon.com/images/I/71TPda7cwUL._SL1500_.jpg"),
            (14,"Dell Inspiron Laptop",55999,"recommended","https://m.media-amazon.com/images/I/61Dw5Z8LzJL._SL1500_.jpg"),
            (15,"Sony Bravia 55 TV",59999,"recommended","https://m.media-amazon.com/images/I/81wxS8abrgL._SL1500_.jpg"),
            (16,"Canon DSLR Camera",42999,"recommended","https://m.media-amazon.com/images/I/81dO3h6pGGL._SL1500_.jpg"),
            (17,"Apple AirPods",11999,"recommended","https://m.media-amazon.com/images/I/71bhWgQK-cL._SL1500_.jpg"),
            (18,"Samsung Galaxy Watch",18999,"recommended","https://m.media-amazon.com/images/I/61ZjlBOp+rL._SL1500_.jpg"),
            (19,"iPad 10th Gen",38999,"recommended","https://m.media-amazon.com/images/I/61NGnpjoRDL._SL1500_.jpg"),
            (20,"Amazon Echo Dot",4499,"recommended","https://m.media-amazon.com/images/I/71xoR4A6q-L._SL1500_.jpg"),
        ]

        cursor.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?)", products
        )

    conn.commit()
    conn.close()
