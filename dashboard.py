import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Trader Behavior Dashboard", layout="wide")

st.title("Trader Performance vs Market Sentiment Dashboard")
st.markdown("A lightweight interactive dashboard to explore how Bitcoin sentiment impacts trader behavior and performance on Hyperliquid.")

# Provide an option to clear cache if needed
@st.cache_data
def load_and_preprocess_data():
    # Load raw data
    df_fg = pd.read_csv('data/fear_greed_index.csv')
    df_hd = pd.read_csv('data/historical_data.csv')
    
    # 1. Process Fear/Greed
    df_fg['Date'] = pd.to_datetime(df_fg['date']).dt.date
    df_fg = df_fg.drop_duplicates(subset=['Date'])
    
    def categorize_regime(x):
        val = str(x).lower()
        if 'fear' in val: return 'Fear'
        if 'greed' in val: return 'Greed'
        return 'Neutral'
    
    df_fg['Regime'] = df_fg['classification'].apply(categorize_regime)
    
    # 2. Process Traders
    df_hd['Timestamp_IST_DT'] = pd.to_datetime(df_hd['Timestamp IST'], format='%d-%m-%Y %H:%M')
    df_hd['Timestamp_UTC'] = df_hd['Timestamp_IST_DT'].dt.tz_localize('Asia/Kolkata').dt.tz_convert('UTC')
    df_hd['Date'] = df_hd['Timestamp_UTC'].dt.date
    df_hd['Net_PnL'] = df_hd['Closed PnL'] - df_hd['Fee']
    df_hd['Is_Win'] = df_hd['Net_PnL'] > 0
    df_hd['Is_Loss'] = df_hd['Net_PnL'] < 0
    df_hd['Is_Taker'] = df_hd['Crossed'] == True
    
    # 3. Aggregate Daily Stats
    daily_stats = df_hd.groupby('Date').agg(
        Daily_Total_Net_PnL=('Net_PnL', 'sum'),
        Avg_Trade_Size=('Size USD', 'mean'),
        Total_Trades=('Account', 'count'),
        Unique_Accounts=('Account', 'nunique'),
        Winning_Trades=('Is_Win', 'sum'),
        Losing_Trades=('Is_Loss', 'sum'),
        Taker_Trades=('Is_Taker', 'sum')
    ).reset_index()
    
    daily_stats['Win_Rate'] = daily_stats['Winning_Trades'] / (daily_stats['Winning_Trades'] + daily_stats['Losing_Trades']).replace(0, 1)
    daily_stats['Taker_Ratio'] = daily_stats['Taker_Trades'] / daily_stats['Total_Trades'].replace(0, 1)
    
    # Merge
    merged = pd.merge(daily_stats, df_fg[['Date', 'value', 'classification', 'Regime']], on='Date', how='inner')
    merged = merged.sort_values('Date')
    
    return merged, df_hd

with st.spinner('Crunching large dataset and enforcing UTC timezone alignment...'):
    try:
        df_merged, df_hd = load_and_preprocess_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

# ----- SIDEBAR -----
st.sidebar.header("Filter & Controls")
regime_filter = st.sidebar.multiselect("Select Market Sentiment Regime", options=['Fear', 'Neutral', 'Greed'], default=['Fear', 'Neutral', 'Greed'])

if not regime_filter:
    st.warning("Please select at least one regime from the sidebar.")
    st.stop()

filtered_df = df_merged[df_merged['Regime'].isin(regime_filter)]

# ----- KPI METRICS -----
st.markdown("### Market Aggregate KPIs (Filtered by Regime)")
c1, c2, c3, c4 = st.columns(4)

c1.metric("Selected Days", f"{len(filtered_df)} days")
c2.metric("Total Net PnL", f"${filtered_df['Daily_Total_Net_PnL'].sum():,.2f}")
c3.metric("Avg Win Rate", f"{filtered_df['Win_Rate'].mean():.2%}")
c4.metric("Avg Taker Ratio (Urgency)", f"{filtered_df['Taker_Ratio'].mean():.2%}")

st.markdown("---")

# ----- VISUALIZATIONS -----
st.markdown("### 1. Market Sentiment Timeline vs Daily Aggregates")

metric_choice = st.selectbox("Select metric to overlay with Sentiment Index Score:", 
                             ['Daily_Total_Net_PnL', 'Win_Rate', 'Avg_Trade_Size', 'Taker_Ratio', 'Total_Trades'], 
                             index=0)

fig_time = go.Figure()
fig_time.add_trace(go.Bar(x=filtered_df['Date'], y=filtered_df[metric_choice], name=metric_choice, marker_color='rgb(55, 83, 109)', opacity=0.7, yaxis='y1'))
fig_time.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['value'], mode='lines+markers', name='F&G Index Score', line=dict(color='orange', width=2), yaxis='y2'))

fig_time.update_layout(
    xaxis=dict(title="Date"),
    yaxis=dict(title="Value", title_font=dict(color='rgb(55, 83, 109)'), tickfont=dict(color='rgb(55, 83, 109)')),
    yaxis2=dict(title="Fear & Greed Value (0-100)", title_font=dict(color='orange'), tickfont=dict(color='orange'), overlaying='y', side='right', range=[0, 100]),
    hovermode='x unified',
    template='plotly_white'
)
st.plotly_chart(fig_time, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 2. Behavioral Divergence by Sentiment")
    
    # Boxplot of Win Rate across regimes
    fig_box = px.box(df_merged, x='Regime', y='Win_Rate', color='Regime',
                     title="Win Rate Distribution Across Sentiment Phase",
                     color_discrete_map={'Fear':'red', 'Neutral':'gray', 'Greed':'green'})
    st.plotly_chart(fig_box, use_container_width=True)

with col2:
    st.markdown("### 3. Taker Ratios (Panic/Urgency Indicator)")
    fig_scatter = px.scatter(df_merged, x='value', y='Taker_Ratio', color='Regime',
                             trendline="ols",
                             title="Execution Urgency (Taker Ratio) vs Sentiment Score",
                             labels={'value': 'Fear & Greed Index (0-100)', 'Taker_Ratio': '% Executed as Taker'},
                             color_discrete_map={'Fear':'red', 'Neutral':'gray', 'Greed':'green'})
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")
st.markdown("### Raw Data Explorer")
st.dataframe(filtered_df.style.highlight_max(axis=0))

st.sidebar.markdown("---")
st.sidebar.markdown("**Insights**:")
st.sidebar.markdown("- **Fear**: Users pay high spreads (Takers) leading to PnL destruction.")
st.sidebar.markdown("- **Greed**: System returns to structural Maker stability with elevated Win Rates.")
