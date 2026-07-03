# SalesApp

Универсальное приложение для учёта ежедневной выручки любого бизнеса.

## Архитектура проекта
```
SalesApp/
├── salesapp/              # Python-код приложения
│   ├── config.py          # пути и настройки
│   ├── database.py        # SQLite, init_db
│   ├── products.py        # загрузка каталога
│   ├── sales.py           # продажи, закрытие дня, отчёты
│   └── ui.py              # Streamlit-интерфейс
├── data/                  # пользовательские данные
│   ├── products.json      # каталог товаров/услуг
│   └── sales.db           # база (создаётся автоматически)
├── assets/                # иконки
├── scripts/               # сборка и ярлыки (Windows)
├── docs/                  # инструкции
├── .streamlit/            # настройки Streamlit
├── start.bat              # запуск для клиента
├── create_shortcut.bat    # ярлык на рабочий стол
└── build_client.bat       # сборка ZIP
```

## Быстрый старт

```powershell
cd SalesApp
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
py -3 -m streamlit run salesapp/ui.py
```
