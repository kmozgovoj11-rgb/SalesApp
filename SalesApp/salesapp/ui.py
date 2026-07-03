from datetime import date

import pandas as pd
import streamlit as st

from salesapp.database import init_db
from salesapp.products import load_products
from salesapp.sales import (
    add_sale,
    auto_close_days,
    build_breakdown,
    close_day,
    fetch_daily_history,
    fetch_today_sales,
    notify_auto_close_results,
    undo_last,
)


def main() -> None:
    st.set_page_config(page_title="SalesApp — учёт выручки", layout="wide")
    st.title("SalesApp — ежедневный учёт выручки")

    init_db()
    notify_auto_close_results(auto_close_days())

    with st.sidebar:
        st.header("История")
        date_range = st.date_input(
            "Диапазон дат",
            value=(date.today(), date.today()),
        )

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range

        history_df = fetch_daily_history(start_date, end_date)
        if history_df.empty:
            st.info("В выбранном диапазоне нет данных.")
        else:
            history_chart = history_df.copy()
            history_chart["date"] = pd.to_datetime(history_chart["date"])
            history_chart = history_chart.set_index("date")
            st.line_chart(history_chart["total_revenue"])
            st.dataframe(
                history_df.rename(
                    columns={
                        "date": "Дата",
                        "total_revenue": "Выручка",
                        "total_qty": "Кол-во, шт",
                    }
                ),
                use_container_width=True,
            )

    products = load_products()
    product_map = {p["name"]: p["price"] for p in products}
    product_names = list(product_map.keys())

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        selected_product = st.selectbox(
            "Выберите товар",
            options=product_names,
            index=None,
            placeholder="Выберите товар из списка",
        )
    with col2:
        qty = st.number_input("Количество", min_value=1, step=1, value=1)
    with col3:
        st.write("")
        st.write("")
        add_disabled = selected_product is None
        if st.button("Добавить продажу", use_container_width=True, disabled=add_disabled):
            if not isinstance(qty, int) or qty <= 0:
                st.error("Количество должно быть целым числом больше 0.")
            elif selected_product is None:
                st.error("Пожалуйста, выберите товар.")
            else:
                add_sale(selected_product, qty, product_map[selected_product])
                st.success(f"Добавлено: {qty} x {selected_product}")

    action_col1, action_col2, action_col3 = st.columns([1, 1, 2])
    with action_col1:
        if st.button("Отменить последнюю запись", use_container_width=True):
            if undo_last():
                st.warning("Последняя запись удалена.")
            else:
                st.info("Нет продаж для отмены.")
    with action_col2:
        if st.button("Обновить товары", use_container_width=True):
            st.cache_data.clear()
            st.success("Кэш товаров очищен.")
            st.rerun()
    with action_col3:
        if st.button("Закрыть день", use_container_width=True):
            result = close_day()
            if result is None:
                st.info("Сегодня нет продаж для закрытия дня.")
            else:
                st.balloons()
                st.success(
                    f"День закрыт ({result['date']}) — "
                    f"за смену: {result['session_revenue']:.2f} ({result['session_qty']} шт), "
                    f"итого за день: {result['day_total_revenue']:.2f} ({result['day_total_qty']} шт), "
                    f"топ-товар: {result['top_product']}"
                )

    if not products:
        st.warning(
            "Товары не найдены. Добавьте корректный data/products.json с элементами вида "
            '[{"name": "Услуга", "price": 1500}].'
        )

    today_sales = fetch_today_sales()
    total_revenue = float(today_sales["revenue"].sum()) if not today_sales.empty else 0.0
    total_qty = int(today_sales["qty"].sum()) if not today_sales.empty else 0

    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric("Выручка за сегодня", f"{total_revenue:.2f}")
    metric_col2.metric("Продано позиций за сегодня", total_qty)

    st.subheader("Продажи за сегодня")
    st.dataframe(
        today_sales.rename(
            columns={
                "id": "ID",
                "product": "Товар",
                "qty": "Кол-во",
                "price": "Цена",
                "revenue": "Выручка",
                "timestamp": "Время",
            }
        ),
        use_container_width=True,
    )

    st.subheader("Разбивка по товарам за сегодня")
    breakdown_df = build_breakdown(today_sales)
    st.dataframe(breakdown_df, use_container_width=True)


if __name__ == "__main__":
    main()
