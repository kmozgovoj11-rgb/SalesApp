from datetime import date, datetime

import pandas as pd
import streamlit as st

from salesapp.config import AUTO_CLOSE_HOUR, AUTO_CLOSE_MINUTE
from salesapp.database import get_connection


def add_sale(product_name: str, qty: int, price: float) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    revenue = qty * price
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sales (product, qty, price, revenue, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (product_name, qty, price, revenue, now),
        )
        conn.commit()


def undo_last() -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM sales ORDER BY timestamp DESC, id DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return False
        conn.execute("DELETE FROM sales WHERE id = ?", (row["id"],))
        conn.commit()
        return True


def fetch_today_sales() -> pd.DataFrame:
    today = date.today().isoformat()
    query = """
        SELECT id, product, qty, price, revenue, timestamp
        FROM sales
        WHERE date(timestamp) = ?
        ORDER BY timestamp DESC, id DESC
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=(today,))


def fetch_daily_history(start_date: date | None = None, end_date: date | None = None) -> pd.DataFrame:
    base_query = """
        SELECT date, total_revenue, total_qty
        FROM daily_history
    """
    params: list[str] = []
    conditions = []

    if start_date is not None:
        conditions.append("date >= ?")
        params.append(start_date.isoformat())
    if end_date is not None:
        conditions.append("date <= ?")
        params.append(end_date.isoformat())

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    base_query += " ORDER BY date ASC"

    with get_connection() as conn:
        return pd.read_sql_query(base_query, conn, params=params)


def fetch_open_sale_dates() -> list[date]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT date(timestamp) AS sale_date FROM sales ORDER BY sale_date"
        ).fetchall()
    return [date.fromisoformat(row["sale_date"]) for row in rows]


def should_auto_close_today(now: datetime) -> bool:
    return (now.hour, now.minute) >= (AUTO_CLOSE_HOUR, AUTO_CLOSE_MINUTE)


def close_day_for_date(target_date: date, auto: bool = False) -> dict | None:
    date_str = target_date.isoformat()
    with get_connection() as conn:
        day_rows = pd.read_sql_query(
            """
            SELECT product, qty, revenue
            FROM sales
            WHERE date(timestamp) = ?
            """,
            conn,
            params=(date_str,),
        )

        if day_rows.empty:
            return None

        session_revenue = float(day_rows["revenue"].sum())
        session_qty = int(day_rows["qty"].sum())

        product_group = (
            day_rows.groupby("product", as_index=False)["revenue"]
            .sum()
            .sort_values(["revenue", "product"], ascending=[False, True])
        )
        top_product = str(product_group.iloc[0]["product"]) if not product_group.empty else "-"

        conn.execute(
            """
            INSERT INTO daily_history (date, total_revenue, total_qty)
            VALUES (?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                total_revenue = daily_history.total_revenue + excluded.total_revenue,
                total_qty = daily_history.total_qty + excluded.total_qty
            """,
            (date_str, session_revenue, session_qty),
        )
        conn.execute("DELETE FROM sales WHERE date(timestamp) = ?", (date_str,))

        row = conn.execute(
            "SELECT total_revenue, total_qty FROM daily_history WHERE date = ?",
            (date_str,),
        ).fetchone()
        conn.commit()

    return {
        "date": date_str,
        "session_revenue": session_revenue,
        "session_qty": session_qty,
        "day_total_revenue": float(row["total_revenue"]),
        "day_total_qty": int(row["total_qty"]),
        "top_product": top_product,
        "auto": auto,
    }


def close_day() -> dict | None:
    return close_day_for_date(date.today())


def auto_close_days() -> list[dict]:
    results: list[dict] = []
    today = date.today()
    now = datetime.now()

    for sale_date in fetch_open_sale_dates():
        if sale_date < today:
            result = close_day_for_date(sale_date, auto=True)
        elif sale_date == today and should_auto_close_today(now):
            result = close_day_for_date(sale_date, auto=True)
        else:
            result = None

        if result is not None:
            results.append(result)

    return results


def notify_auto_close_results(results: list[dict]) -> None:
    notified = st.session_state.setdefault("auto_close_notified", set())
    for result in results:
        key = (result["date"], result["session_revenue"], result["session_qty"])
        if key in notified:
            continue
        notified.add(key)
        st.info(
            f"Автоматически закрыт день {result['date']}: "
            f"+{result['session_revenue']:.2f} ({result['session_qty']} шт), "
            f"итого за день: {result['day_total_revenue']:.2f} ({result['day_total_qty']} шт)."
        )


def build_breakdown(today_sales: pd.DataFrame) -> pd.DataFrame:
    if today_sales.empty:
        return pd.DataFrame(columns=["Товар", "Продано, шт", "Выручка"])

    breakdown = (
        today_sales.groupby("product", as_index=False)
        .agg(units_sold=("qty", "sum"), revenue=("revenue", "sum"))
        .sort_values(["revenue", "units_sold", "product"], ascending=[False, False, True])
    )
    return breakdown.rename(
        columns={
            "product": "Товар",
            "units_sold": "Продано, шт",
            "revenue": "Выручка",
        }
    )
