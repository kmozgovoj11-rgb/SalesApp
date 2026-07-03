from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PNG = ASSETS / "app_icon.png"
ICO = ASSETS / "app_icon.ico"

img = Image.open(PNG).convert("RGBA")
sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
icons = [img.resize(size, Image.Resampling.LANCZOS) for size in sizes]
icons[0].save(ICO, format="ICO", sizes=[icon.size for icon in icons])
print(f"Created: {ICO}")
