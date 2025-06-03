import streamlit as st
import pandas as pd
#streamlit run tf_key_calculator.py

st.set_page_config(page_title="TF Key Profit Calculator", layout="wide")

# Настройки от пользователя
st.sidebar.header("Настройки базовых переменных")

# Пользователь вводит полные цены, комиссии применяются автоматически
lavka_price = st.sidebar.number_input('TF Key Price (Lavka)', value=1.69)
tm_price = st.sidebar.number_input('TF Key Price (TM)', value=1.85)
tm_autobuy_price = st.sidebar.number_input('TF Key Price (TM Autobuy)', value=1.8)
csdeals_price = st.sidebar.number_input('TF Key Price (CSDeals)', value=1.75)

real_tf_key_pices = {
    'Lavka': lavka_price,
    'TM': tm_price * 0.9,  # -10%
    'TM_Autobuy': tm_autobuy_price * 0.9,  # -10%
    'CSDeals': csdeals_price * 0.95  # -5%
}

sell_tf_key_pices = {
    'lootfarm': st.sidebar.number_input('Sell TF Key Price (lootfarm)', value=2.81),
    'tradeit': st.sidebar.number_input('Sell TF Key Price (tradeit)', value=3.20),
    'csmoney': st.sidebar.number_input('Sell TF Key Price (csmoney)', value=2.92),
}

transfer_fees = {
    'tradeit': st.sidebar.slider('Tradeit → Lootfarm Fee (%)', 0.0, 100.0, 11.5) / 100,
    'csmoney': st.sidebar.slider('CSMoney → Lootfarm Fee (%)', 0.0, 100.0, 4.5) / 100,
}

schemes = ['lootfarm', 'tradeit', 'csmoney', 'tradeit_self', 'csmoney_self']

scheme_start_profits = {
    scheme: st.sidebar.slider(f"Старт % прибыли для схемы {scheme.upper()}", 50, 200, 100)
    for scheme in schemes
}

def calculate(purchase_price, min_profit_filter):
    all_results = {}
    for scheme in schemes:
        data = []
        start_profit_pct = scheme_start_profits[scheme]
        for profit_pct in range(start_profit_pct, 49, -1):
            sell_value = purchase_price * (1 + profit_pct / 100)

            if scheme == "lootfarm":
                keys = sell_value / sell_tf_key_pices["lootfarm"]
            elif scheme == "tradeit":
                keys = (sell_value * (1 - transfer_fees["tradeit"])) / sell_tf_key_pices["lootfarm"]
            elif scheme == "csmoney":
                keys = (sell_value * (1 - transfer_fees["csmoney"])) / sell_tf_key_pices["lootfarm"]
            elif scheme == "tradeit_self":
                keys = sell_value / sell_tf_key_pices["tradeit"]
            elif scheme == "csmoney_self":
                keys = sell_value / sell_tf_key_pices["csmoney"]
            else:
                continue

            row = {"Profit %": f"{profit_pct:.0f}%"}
            for source, real_key_price in real_tf_key_pices.items():
                out = keys * real_key_price
                pct = ((out / purchase_price) - 1) * 100
                if pct >= min_profit_filter:
                    row[f"{source} (out)"] = round(out, 2)
                    row[f"{source} (%)"] = f"{pct:.2f}%"
            data.append(row)
        all_results[scheme] = pd.DataFrame(data)
    return all_results

st.title("TF Key Profit Calculator")

price = st.number_input("Цена покупки", min_value=1.0, value=10.0, step=0.1)
min_profit = st.slider("Минимальный % прибыли для отображения", 0, 100, 0)

results = calculate(price, min_profit)

tabs = st.tabs([s.upper() for s in schemes])
for tab, name in zip(tabs, schemes):
    with tab:
        df = results[name]
        st.dataframe(df.style.applymap(
            lambda v: "color: green" if isinstance(v, str) and '%' in v and float(v.strip('%')) > 0 else ("color: red" if isinstance(v, str) and '%' in v else ""),
            subset=[col for col in df.columns if '%' in col]
        ))
