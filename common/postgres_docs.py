"""
Builds one RAG document per product, per README.md section 4
("products + categories + inventory -> one document per product").
"""

import uuid

import psycopg2
import psycopg2.extras

from . import config

# Fixed namespace so point IDs are deterministic across runs (README section 5:
# "Point ID: deterministic, derived from (source_table, source_pk[, chunk_index])").
POINT_ID_NAMESPACE = uuid.UUID("7f3f9c2a-4d3e-4b7a-9b1a-6f7f2f9c2a4d")

SOURCE_TABLE = "products"

QUERY = """
    SELECT
        p.product_id,
        p.sku,
        p.product_name,
        p.price,
        p.description,
        p.is_deleted,
        p.updated_at,
        c.category_id,
        c.category_name,
        COALESCE(SUM(i.quantity_on_hand), 0) AS stock_on_hand
    FROM products p
    JOIN categories c ON c.category_id = p.category_id
    LEFT JOIN inventory i ON i.product_id = p.product_id
    WHERE p.is_deleted = FALSE
    GROUP BY p.product_id, p.sku, p.product_name, p.price, p.description,
             p.is_deleted, p.updated_at, c.category_id, c.category_name
    ORDER BY p.product_id
"""


def point_id_for(source_pk) -> str:
    return str(uuid.uuid5(POINT_ID_NAMESPACE, f"{SOURCE_TABLE}:{source_pk}"))


def connect():
    return psycopg2.connect(**config.POSTGRES)


def fetch_product_documents(conn):
    """Returns a list of {point_id, text, payload} dicts, one per in-stock-or-not product."""
    docs = []
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(QUERY)
        for row in cur.fetchall():
            stock_status = "in stock" if row["stock_on_hand"] > 0 else "out of stock"
            text = (
                f"{row['product_name']} (SKU {row['sku']}) is in the "
                f"'{row['category_name']}' category, priced at {row['price']}. "
                f"{row['description'] or ''} "
                f"Stock status: {stock_status} ({row['stock_on_hand']} units on hand)."
            ).strip()

            payload = {
                "source_table": SOURCE_TABLE,
                "source_pk": row["product_id"],
                "sku": row["sku"],
                "product_name": row["product_name"],
                "category_id": row["category_id"],
                "category_name": row["category_name"],
                "price": float(row["price"]),
                "status": stock_status,
                "stock_on_hand": row["stock_on_hand"],
                "updated_at": row["updated_at"].isoformat(),
                "is_deleted": row["is_deleted"],
                "text": text,
            }

            docs.append({
                "point_id": point_id_for(row["product_id"]),
                "text": text,
                "payload": payload,
            })
    return docs
