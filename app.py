import os
from flask import Flask, render_template, request
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_PASSWORD"),
        database="bite_the_bill"
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/platforms")
def platforms():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM platforms ORDER BY name")
        platform_list = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template("platforms.html", platforms=platform_list)


@app.route("/categories")
def categories():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT DISTINCT category
            FROM platforms
            ORDER BY category
        """)
        category_list = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template("categories.html", categories=category_list)


@app.route("/compare", methods=["GET", "POST"])
def compare():
    food = ""
    results = []
    cheapest = None
    savings = 0

    if request.method == "POST":
        food = request.form.get("food", "").strip()

    if food:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    p.name AS platform_name,
                    p.category,
                    f.item_name,
                    f.price,
                    f.available
                FROM food_items f
                JOIN platforms p ON p.id = f.platform_id
                WHERE LOWER(f.item_name) LIKE LOWER(%s)
                  AND f.available = TRUE
                  AND f.price IS NOT NULL
                ORDER BY f.price ASC
            """, (f"%{food}%",))

            results = cursor.fetchall()

            if results:
                cheapest = results[0]
                prices = [float(item["price"]) for item in results]
                savings = round(max(prices) - min(prices), 2)
        finally:
            cursor.close()
            connection.close()

    return render_template(
        "compare.html",
        food=food,
        results=results,
        cheapest=cheapest,
        savings=savings
    )


if __name__ == "__main__":
    app.run(debug=True)