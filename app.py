import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

st.set_page_config(page_title="SwingPro Nifty 500", layout="wide")

st.markdown("""
<style>
    .header {background: linear-gradient(135deg, #6b46c1, #7c3aed); padding: 35px; border-radius: 20px; text-align: center; color: white; margin-bottom: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.3);}
    .scan-btn {background: linear-gradient(135deg, #ef4444, #f87171); color: white; padding: 15px; border-radius: 12px; text-align: center; font-weight: bold; font-size: 18px; margin: 15px 0; cursor: pointer;}
    .metric-card {padding: 20px; border-radius: 15px; text-align: center; color: white; font-weight: bold; box-shadow: 0 5px 15px rgba(0,0,0,0.2); min-height: 140px;}
    .nifty-card {background: linear-gradient(135deg, #a855f7, #c084fc);}
    .panel {background: linear-gradient(135deg, #f59e0b, #fb923c); color: white; padding: 12px; border-radius: 10px; font-weight: bold; text-align: center; margin: 15px 0;}
    .status-bar {background: #ecfdf5; color: #166534; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; margin: 15px 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h1>🚀 SwingPro Nifty 500</h1>
    <p>AI-Powered Swing Trading Scanner</p>
</div>
""", unsafe_allow_html=True)

URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsnZ6oD_zaP3JLOVaAbR1ZTzn2TVQ26agPr_G89Iey669ijjuJnwgbiaJDtdBiF1ixVyZ0gtfTA1e8/pub?output=csv"

def get_cpr(df):
    prev_day = df.iloc[-2]
    pivot = (prev_day['High'] + prev_day['Low'] + prev_day['Close']) / 3
    bc = (prev_day['High'] + prev_day['Low']) / 2
    tc = (pivot - bc) + pivot
    return pivot, bc, tc

def analyze_stock(symbol):
    try:
        ticker = f"{symbol}.NS"
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        if len(df) < 100: return None

        ltp = round(df['Close'].iloc[-1], 2)
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        ema_200 = ta.ema(df['Close'], length=200).iloc[-1]
        
        macd_df = ta.macd(df['Close'])
        macd_line = macd_df['MACD_12_26_9'].iloc[-1]
        macd_sig = macd_df['MACDs_12_26_9'].iloc[-1]
        
        pivot, bc, tc = get_cpr(df)

        signal = "⚪ WAIT"
        reason = "Neutral"

        if ltp > ema_200 and rsi > 50 and macd_line > macd_sig:
            if ltp > tc:
                signal = "🟢 STRONG BUY"
                reason = "Bullish + Above CPR"
            else:
                signal = "🟡 WATCH"
                reason = "Above 200 EMA, Near CPR"
        elif ltp < ema_200:
            signal = "🔴 AVOID"
            reason = "Below 200 EMA"

        return {
            "Stock": symbol,
            "Signal": signal,
            "LTP": float(ltp),
            "RSI": round(float(rsi), 2),
            "Reason": reason
        }
    except:
        return None

if st.button('🚀 Start Nifty 500 Full Scan', type="primary", use_container_width=True):
    try:
        sheet_df = pd.read_csv(URL)
        symbols = sheet_df['Symbol'].tolist()
        target_symbols = symbols[:500] 
        
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, s in enumerate(target_symbols):
            status_text.text(f"Scanning {i+1}/{len(target_symbols)}: {s}")
            status = analyze_stock(s)
            if status:
                results.append(status)
            progress_bar.progress((i + 1) / len(target_symbols))
        
        status_text.success("Scan Completed! ✅")
        
        if results:
            final_df = pd.DataFrame(results)
            bullish_df = final_df[final_df['Signal'] == "🟢 STRONG BUY"]
            
            st.subheader("📊 Bullish Opportunities (Strong Buy)")
            st.dataframe(bullish_df, use_container_width=True, hide_index=True)
            
            with st.expander("Show All Scanned Data"):
                st.dataframe(final_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error: {e}")

st.caption("Swing Trading Scanner • Nifty 500 • Beautiful UI")
