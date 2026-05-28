import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# ページ設定
# -----------------------------
st.set_page_config(
    page_title="Entry Signal",
    page_icon="📈",
    layout="centered"
)

# -----------------------------
# RSI計算関数
# -----------------------------
def calculate_rsi(series, period=14):
    delta = series.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi

# -----------------------------
# タイトル
# -----------------------------
st.title("📈 Entry Signal")

st.caption("中長期投資向け エントリー判定アプリ")

# -----------------------------
# 入力
# -----------------------------
ticker = st.text_input(
    "ティッカーを入力してください",
    "AAPL"
)

# -----------------------------
# 判定ボタン
# -----------------------------
if st.button("判定する"):

    try:

        # -----------------------------
        # データ取得
        # -----------------------------
        stock = yf.Ticker(ticker)

        df = stock.history(period="1y")

        if df.empty:
            st.error("データ取得に失敗しました")
            st.stop()

        # -----------------------------
        # 指標計算
        # -----------------------------
        df["MA50"] = df["Close"].rolling(50).mean()
        df["MA200"] = df["Close"].rolling(200).mean()
        df["RSI"] = calculate_rsi(df["Close"])

        latest = df.iloc[-1]

        price = latest["Close"]
        ma50 = latest["MA50"]
        ma200 = latest["MA200"]
        rsi = latest["RSI"]

        # 3か月前価格（約63営業日前）
        price_3m_ago = df.iloc[-63]["Close"]

        # -----------------------------
        # 条件判定
        # -----------------------------

        # ① Price > MA200
        cond1 = price > ma200

        # ② MA50 > MA200
        cond2 = ma50 > ma200

        # ③ 3か月上昇率 < 20%
        growth_3m = ((price - price_3m_ago) / price_3m_ago) * 100
        cond3 = growth_3m < 20

        # ④ MA50乖離 ±10%
        ma50_gap = ((price - ma50) / ma50) * 100
        cond4 = abs(ma50_gap) < 10

        # ⑤ RSI < 55
        cond5 = rsi < 55

        # -----------------------------
        # BUY / WAIT 判定
        # -----------------------------
        support_count = sum([cond3, cond4, cond5])

        if cond1 and cond2 and support_count >= 2:
            final_result = "BUY"
        else:
            final_result = "WAIT"

        # -----------------------------
        # 銘柄名
        # -----------------------------
        company_name = stock.info.get("shortName", ticker)

        # -----------------------------
        # 上部表示
        # -----------------------------
        st.subheader(f"{company_name}")

        # BUY / WAIT を上に表示
        if final_result == "BUY":
            st.success("🟢 BUY")
        else:
            st.warning("🟡 WAIT")

        st.write(f"現在株価: ${price:.2f}")

        st.write("---")

        # -----------------------------
        # 条件一覧
        # -----------------------------
        st.subheader("Conditions")

        st.write(f"① 【Must】Price > MA200 : {'✅' if cond1 else '❌'}")

        st.write(f"② 【Must】MA50 > MA200 : {'✅' if cond2 else '❌'}")

        st.write(f"③ 3-Month Growth < 20% : {'✅' if cond3 else '❌'}")

        st.write(f"④ MA50 Gap ±10% : {'✅' if cond4 else '❌'}")

        st.write(f"⑤ RSI < 55 : {'✅' if cond5 else '❌'}")

        st.write("---")

        # -----------------------------
        # 数値詳細
        # -----------------------------
        st.subheader("Metrics")

        st.write(f"3-Month Growth: {growth_3m:.2f}%")

        st.write(f"MA50 Gap: {ma50_gap:.2f}%")

        st.write(f"RSI: {rsi:.2f}")

        st.write("---")

        # -----------------------------
        # チャート
        # -----------------------------
        st.subheader("1 Year Chart")

        fig, ax = plt.subplots(figsize=(10, 4))

        ax.plot(
            df.index,
            df["Close"],
            label="Close"
        )

        ax.plot(
            df.index,
            df["MA50"],
            label="MA50"
        )

        ax.plot(
            df.index,
            df["MA200"],
            label="MA200"
        )

        ax.set_xlabel("Date")
        ax.set_ylabel("Price")

        ax.legend()

        st.pyplot(fig)

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
```
