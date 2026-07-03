import json

import streamlit as st

from salesapp.config import PRODUCTS_PATH


@st.cache_data(ttl=None)
def load_products() -> list[dict]:
    if not PRODUCTS_PATH.exists():
        return []

    with PRODUCTS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    valid_products = []
    for item in data:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        price = item.get("price")
        if isinstance(name, str) and name.strip() and isinstance(price, (int, float)):
            valid_products.append({"name": name.strip(), "price": float(price)})
    return valid_products
