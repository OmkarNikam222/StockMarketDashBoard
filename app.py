import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go   # for Sankey

# =========================
# APP CONFIG
# =========================
st.set_page_config(page_title="Stock Market Dashboard", layout="wide")
st.title("📈 Stock Market Dashboard")
st.caption("Data source: stock_market.csv | Cleaned & Aggregated with Pandas | Visualized in Streamlit")

# =========================
# THEME TOGGLE (LIGHT / DARK)
# =========================
st.sidebar.header("Appearance")
theme = st.sidebar.radio("Theme", ["Light", "Dark"], index=0)
is_dark = theme == "Dark"

def apply_theme(dark: bool):
    if dark:
        st.markdown(
            """
            <style>
            body {
                background-color: #0e1117;
                color: #fafafa;
            }
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            body {
                background-color: #ffffff;
                color: #000000;
            }
            .stApp {
                background-color: #ffffff;
                color: #000000;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

apply_theme(is_dark)

# Helper for plotly theme
PLOTLY_TEMPLATE = "plotly_dark" if is_dark else "plotly_white"

# =========================
# LOAD DATA
# =========================
agg1 = pd.read_parquet("data/agg1.parquet")   # Daily avg close by ticker
agg2 = pd.read_parquet("data/agg2.parquet")   # Avg volume by sector
agg3 = pd.read_parquet("data/agg3.parquet")   # Daily returns

# Make sure dates are datetime
agg1["trade_date"] = pd.to_datetime(agg1["trade_date"])
agg3["trade_date"] = pd.to_datetime(agg3["trade_date"])

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("🔎 Filters")

# Ticker for detailed view
tickers = sorted(agg1["ticker"].dropna().unique())
ticker = st.sidebar.selectbox("Select Ticker", tickers)

# Tickers for comparison chart + summary
compare_tickers = st.sidebar.multiselect(
    "Tickers to compare",
    tickers,
    default=tickers[: min(5, len(tickers))]
)

# Date filters
min_date = agg1["trade_date"].min().date()
max_date = agg1["trade_date"].max().date()

start_date = st.sidebar.date_input("Start Date", min_date)
end_date = st.sidebar.date_input("End Date", max_date)

if end_date < start_date:
    st.sidebar.error("End Date must be on or after Start Date.")

start_ts = pd.to_datetime(start_date)
end_ts = pd.to_datetime(end_date)

# Filter data for selected ticker and dates
filtered = agg1[
    (agg1["ticker"] == ticker)
    & (agg1["trade_date"].between(start_ts, end_ts))
].copy()

returns = agg3[
    (agg3["ticker"] == ticker)
    & (agg3["trade_date"].between(start_ts, end_ts))
].copy()

# =========================
# MAIN LAYOUT
# =========================
col1, col2 = st.columns(2)

# Chart 1: Average Close Price Over Time (Altair)
with col1:
    st.subheader(f"Average Close Price for {ticker}")
    if filtered.empty:
        st.warning("No data for this ticker and date range.")
    else:
        chart1 = (
            alt.Chart(filtered)
            .mark_line(point=True)
            .encode(
                x=alt.X("trade_date:T", title="Date"),
                y=alt.Y("close_price:Q", title="Average Close Price"),
                tooltip=["trade_date:T", "close_price:Q"]
            )
            .properties(height=350)
        )
        # Simple tweak so it looks OK in dark mode too
        if is_dark:
            chart1 = chart1.configure_axis(
                labelColor="white",
                titleColor="white"
            ).configure_view(
                strokeOpacity=0
            ).properties(background="#0e1117")

        st.altair_chart(chart1, use_container_width=True)

# Chart 2: Average Volume by Sector (Bar + Pie)
with col2:
    st.subheader("Sector Volume Overview")
    if agg2.empty:
        st.warning("No sector data available.")
    else:
        # Bar chart
        fig_bar = px.bar(
            agg2,
            x="sector",
            y="volume",
            title="Average Volume by Sector (Bar)",
        )
        fig_bar.update_layout(template=PLOTLY_TEMPLATE)
        st.plotly_chart(fig_bar, use_container_width=True)

        # Pie chart
        fig_pie = px.pie(
            agg2,
            names="sector",
            values="volume",
            title="Sector Volume Share (Pie)",
        )
        fig_pie.update_layout(template=PLOTLY_TEMPLATE)
        st.plotly_chart(fig_pie, use_container_width=True)

# Chart 3: Daily Returns Line Chart
st.subheader(f"Daily Returns for {ticker}")
if returns.empty:
    st.info("No return data for this ticker and date range.")
else:
    fig_ret = px.line(
        returns.sort_values("trade_date"),
        x="trade_date",
        y="daily_return",
        title=f"Daily Returns – {ticker}",
    )
    fig_ret.update_xaxes(rangeslider_visible=True)
    fig_ret.update_layout(template=PLOTLY_TEMPLATE)
    st.plotly_chart(fig_ret, use_container_width=True)

# Chart 4: Distribution of Daily Returns (Histogram)
st.subheader(f"Distribution of Daily Returns – {ticker}")
if not returns.empty:
    fig_hist = px.histogram(
        returns,
        x="daily_return",
        nbins=40,
        title=f"Histogram of Daily Returns – {ticker}",
    )
    fig_hist.update_layout(template=PLOTLY_TEMPLATE)
    st.plotly_chart(fig_hist, use_container_width=True)

# =========================
# COMPARISON SECTION
# =========================
st.markdown("---")
st.subheader("📊 Multi-Ticker Comparison (Prices, Stats & Risk)")

# Filter data for selected comparison tickers
compare_df = agg1[
    agg1["ticker"].isin(compare_tickers)
    & agg1["trade_date"].between(start_ts, end_ts)
].copy()

if compare_df.empty:
    st.info("No data for selected tickers in this date range.")
else:
    # Line chart: daily average close price
    fig_multi = px.line(
        compare_df.sort_values("trade_date"),
        x="trade_date",
        y="close_price",
        color="ticker",
        title="Daily Average Close Price by Ticker",
    )
    fig_multi.update_xaxes(rangeslider_visible=True)
    fig_multi.update_layout(template=PLOTLY_TEMPLATE)
    st.plotly_chart(fig_multi, use_container_width=True)

    # Build numeric comparison summary
    returns_multi = agg3[
        agg3["ticker"].isin(compare_tickers)
        & agg3["trade_date"].between(start_ts, end_ts)
    ].copy()

    summary_rows = []
    for t in compare_tickers:
        price_slice = compare_df[compare_df["ticker"] == t]
        ret_slice = returns_multi[returns_multi["ticker"] == t]

        if price_slice.empty:
            continue

        avg_close = price_slice["close_price"].mean()

        if not ret_slice.empty:
            avg_ret = ret_slice["daily_return"].mean()
            vol = ret_slice["daily_return"].std()
            n_days = ret_slice.shape[0]
        else:
            avg_ret = float("nan")
            vol = float("nan")
            n_days = price_slice.shape[0]

        summary_rows.append({
            "Ticker": t,
            "Avg Close": round(avg_close, 2),
            "Avg Daily Return": round(avg_ret, 4) if pd.notna(avg_ret) else None,
            "Volatility (Std of Return)": round(vol, 4) if pd.notna(vol) else None,
            "Trading Days": int(n_days),
        })

    if summary_rows:
        st.markdown("**Comparison Summary (selected tickers & date range)**")
        summary_df = pd.DataFrame(summary_rows)
        st.dataframe(summary_df, use_container_width=True)
    else:
        st.info("No valid data to summarize for selected tickers.")

    # Box plot: returns distribution by ticker (risk)
    st.markdown("**Return Distribution by Ticker (Box Plot)**")
    if not returns_multi.empty:
        fig_box = px.box(
            returns_multi,
            x="ticker",
            y="daily_return",
            title="Daily Returns Distribution by Ticker",
        )
        fig_box.update_layout(template=PLOTLY_TEMPLATE)
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("No return data available for box plot.")

    