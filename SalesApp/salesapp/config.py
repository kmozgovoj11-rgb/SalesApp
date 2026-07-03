from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"

DB_PATH = DATA_DIR / "sales.db"
PRODUCTS_PATH = DATA_DIR / "products.json"

AUTO_CLOSE_HOUR = 23
AUTO_CLOSE_MINUTE = 59
