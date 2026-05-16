import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="EasyCharts Pro - Ultra Scanner", layout="wide", page_icon="🚀")

st.markdown("""
<style>
    .header {background: linear-gradient(135deg, #6b46c1, #7c3aed); padding: 35px; border-radius: 20px; text-align: center; color: white; margin-bottom: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.3);}
    .scan-btn {background: linear-gradient(135deg, #ef4444, #f87171); color: white; padding: 15px; border-radius: 12px; text-align: center; font-weight: bold; font-size: 18px; margin: 15px 0; cursor: pointer;}
    .metric-card {padding: 20px; border-radius: 15px; text-align: center; color: white; font-weight: bold; box-shadow: 0 5px 15px rgba(0,0,0,0.2); min-height: 140px;}
    .nifty-card {background: linear-gradient(135deg, #a855f7, #c084fc);}
    .bank-card {background: linear-gradient(135deg, #22c55e, #86efac); color: black;}
    .panel {background: linear-gradient(135deg, #f59e0b, #fb923c); color: white; padding: 12px; border-radius: 10px; font-weight: bold; text-align: center; margin: 15px 0;}
    .status-bar {background: #ecfdf5; color: #166534; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; margin: 15px 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h1>🚀 EasyCharts Pro - Ultra Scanner</h1>
    <p>AI-Powered Multi-Index & Option Master Scanner</p>
</div>
""", unsafe_allow_html=True)

if st.button("🚀 START MARKET SCAN", type="primary", use_container_width=True):
    with st.spinner("Scanning Nifty 200 stocks..."):
        symbols = ["RELIANCE.NS","HDFCBANK.NS","INFY.NS","TCS.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","HINDUNILVR.NS","AXISBANK.NS","KOTAKBANK.NS","ADANIENT.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","ASIANPAINT.NS","BAJFINANCE.NS","DMART.NS","TRENT.NS","ZOMATO.NS","NYKAA.NS","IRCTC.NS","HAL.NS","BEL.NS","PFC.NS","RECLTD.NS","POWERGRID.NS","NTPC.NS","ONGC.NS"]

        def scan_stock(sym):
            try:
                ticker = yf.Ticker(sym)
                df = ticker.history(period="3mo")
                if df.empty or len(df) < 30: return None
                
                current = df['Close'].iloc[-1]
                change = ((current - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                volume_ratio = df['Volume'].iloc[-1] / df['Volume'].iloc[-20:].mean()
                high20 = df['High'].iloc[-20:].max()
                dist = ((high20 - current) / high20) * 100
                
                if dist < 2.0 and change > 0.8 and volume_ratio > 1.4:
                    return {"Type": "Live Breakout", "Symbol": sym.replace(".NS",""), "LTP": round(current,2), "%Chg": round(change,2), "Volx": round(volume_ratio,2)}
                elif dist < 4.0 and volume_ratio > 1.2:
                    return {"Type": "Pre-Breakout", "Symbol": sym.replace(".NS",""), "LTP": round(current,2), "%Chg": round(change,2), "Volx": round(volume_ratio,2)}
                elif change > 2.5 or volume_ratio > 2.0:
                    return {"Type": "Strong Momentum", "Symbol": sym.replace(".NS",""), "LTP": round(current,2), "%Chg": round(change,2), "Volx": round(volume_ratio,2)}
            except:
                return None

        results = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(scan_stock, s) for s in symbols]
            for future in as_completed(futures):
                if future.result():
                    results.append(future.result())

        df = pd.DataFrame(results)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="panel">🔵 Pre-Breakout (Early Stage)</div>', unsafe_allow_html=True)
            pre = df[df["Type"] == "Pre-Breakout"]
            st.dataframe(pre[["Symbol","LTP","%Chg"]], use_container_width=True, hide_index=True)

        with col2:
            st.markdown('<div class="panel">🟢 Live Breakout</div>', unsafe_allow_html=True)
            live = df[df["Type"] == "Live Breakout"]
            st.dataframe(live[["Symbol","LTP","%Chg"]], use_container_width=True, hide_index=True)

        with col3:
            st.markdown('<div class="panel">🔥 Strong Momentum</div>', unsafe_allow_html=True)
            mom = df[df["Type"] == "Strong Momentum"]
            st.dataframe(mom[["Symbol","LTP","%Chg"]], use_container_width=True, hide_index=True)

        st.success(f"✅ Scan Completed at {datetime.now().strftime('%I:%M:%S %p')} | Signals Found: {len(df)}")

else:
    st.info("👆 'START MARKET SCAN' ബട്ടൺ ക്ലിക്ക് ചെയ്താൽ സ്കാൻ തുടങ്ങും")

st.caption("Beautiful UI • No pandas_ta dependency • Stable on Streamlit Cloud")
