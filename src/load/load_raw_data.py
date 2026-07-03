"""
Loads raw Olist e-commerce CSVs into the 'raw' schema in Postgres.
Idempotent: safe to re-run, drops and recreates each table.
"""

import os 
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

DATA_DIR = "data/raw"

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

#Maps CSV filename -> destination table name in the 'raw' schema

FILE_TO_TABLE = {
    "olist_customers_dataset.csv": "customers",
    "olist_geolocation_dataset.csv": "geolocation",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_orders_dataset.csv": "orders",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "product_category_name_translation.csv": "product_category_translation",
}

def get_engine():
    conn_str = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(conn_str)


def main():
    engine = get_engine()

    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
        conn.commit()
    logger.info("Ensured 'raw' schema exists.")

    for filename, table_name in FILE_TO_TABLE.items():
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            logger.warning(f"Skipping {filename} - file not found at {filepath}")
            continue
        
        df = pd.read_csv(filepath)
        df["loaded_at"] = pd.Timestamp.now("UTC")

        df.to_sql(
            table_name,
            engine,
            schema="raw",
            if_exists="replace", #idempotent: drop + recreate each run
            index=False,
        )
        logger.info(f"Loaded {filename} -> raw.{table_name} ({len(df):,} rows)")

    logger.info("Ingestion complete.")


if __name__ == "__main__":
    main()
