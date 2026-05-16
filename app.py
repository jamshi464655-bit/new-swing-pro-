import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import time

# 1. പേജ് സെറ്റപ്പ്
st.set_page_config(page_title="SwingPro Nifty 500", layout="wide")

# ============================================
# Nifty 500 സ്റ്റോക്കുകളുടെ പൂർണ്ണ ലിസ്റ്റ് (Hardcoded)
# ============================================
def get_nifty_500_symbols():
    """Nifty 500 stocks list - വിശ്വസനീയമായ ലിസ്റ്റ്"""
    symbols = [
        # NIFTY 50
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "ITC", "SBIN",
        "BHARTIARTL", "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "TITAN",
        "SUNPHARMA", "ULTRACEMCO", "BAJFINANCE", "NESTLEIND", "HCLTECH", "WIPRO", "POWERGRID",
        "NTPC", "TATAMOTORS", "BAJAJFINSV", "M&M", "TECHM", "ADANIPORTS", "ONGC", "TATASTEEL",
        "COALINDIA", "HINDALCO", "INDUSINDBK", "JSWSTEEL", "GRASIM", "DIVISLAB", "DRREDDY",
        "CIPLA", "APOLLOHOSP", "BRITANNIA", "EICHERMOT", "HEROMOTOCO", "BAJAJ-AUTO",
        "TATACONSUM", "SBILIFE", "HDFCLIFE", "ADANIENT", "ADANIGREEN", "TATAPOWER", "PIDILITIND",
        
        # NIFTY NEXT 50
        "ADANIENSOL", "SIEMENS", "HAVELLS", "DLF", "DMART", "INDIGO", "VEDL", "GODREJCP",
        "GAIL", "BOSCHLTD", "CHOLAFIN", "MUTHOOTFIN", "PNB", "CANBK", "RECLTD", "NMDC",
        "ICICIGI", "SRF", "TORNTPHARM", "DABUR", "MARICO", "PEL", "BANKBARODA", "MOTHERSON",
        "SHREECEM", "AMBUJACEM", "TRENT", "INDUSTOWER", "BERGEPAINT", "COLPAL", "LTIM",
        "HINDPETRO", "BPCL", "IOCL", "SAIL", "LUPIN", "BIOCON", "NAUKRI", "ZOMATO", "PAYTM",
        "DIXON", "POLYCAB", "CROMPTON", "VOLTAS", "TVSMOTOR", "ASHOKLEY", "ESCORTS", "MRF",
        "CONCOR", "GMRINFRA", "PERSISTENT", "COFORGE", "LTTS", "MPHASIS", "OFSS", "L&TFH",
        "SBICARD", "ABCAPITAL", "AUBANK", "BANDHANBNK", "FEDERALBNK", "IDFCFIRSTB", "IDFC",
        "JINDALSTEL", "TATACHEM", "UPL", "APLAPOLLO", "ASTRAL", "CUMMINSIND", "DEEPAKNTR",
        "GODREJPROP", "HDFCAMC", "ICICIPRULI", "IRCTC", "JUBLFOOD", "LAURUSLABS", "NAVINFLUOR",
        "OBEROIRLTY", "PAGEIND", "PIIND", "POLICYBZR", "PVR", "SYNGENE", "TATACOMM", "UBL",
        "MCDOWELL-N", "WHIRLPOOL", "AAVAS", "ANGELONE", "ATUL", "AUROPHARMA", "BAJAJCON",
        "BALRAMCHIN", "BATAINDIA", "BEL", "BHEL", "BSE", "CARBORUNIV", "CESC", "CHAMBLFERT",
        "CYIENT", "DELTACORP", "DEVYANI", "EASEMYTRIP", "EMAMILTD", "FINEORG", "HAL",
        "HAPPSTMNDS", "HONAUT", "INDHOTEL", "JKCEMENT", "JKPAPER", "KAJARIACER", "KANSAINER",
        "KEI", "KPITTECH", "LALPATHLAB", "LINDEINDIA", "MAHINDCIE", "MASTEK", "METROPOLIS",
        "MFSL", "NATIONALUM", "NATCOPHARMA", "NCC", "NIIT", "NYKAA", "PNBHOUSING", "POONAWALLA",
        "PRAJIND", "RAMCOCEM", "RAYMOND", "RBLBANK", "RECLTD", "SAIL", "SOLARINDS", "SONATSOFTW",
        "SUDARSCHEM", "SUPRAJIT", "SUVENPHAR", "SYMPHONY", "TANLA", "TATAELXSI", "TATAMOTORS",
        "THERMAX", "TIINDIA", "TORNTPOWER", "TRIDENT", "TV18BRDCST", "TVSMOTOR", "UBL",
        "UNIONBANK", "VBL", "VEDL", "VOLTAS", "WELCORP", "WELSPUNIND", "YESBANK", "ZEEL",
        "ZENSAR", "ZYDUSLIFE"
    ]
    
    # Remove duplicates and sort
    return sorted(list(set(symbols)))

# ============================================
# CPR കണക്കാക്കുന്ന ഫംഗ്ഷൻ
# ============================================
def get_cpr(df):
    """Calculate CPR (Central Pivot Range)"""
    prev_day = df.iloc[-2]
    pivot = (prev_day['High'] + prev_day['Low'] + prev_day['Close']) / 3
    bc = (prev_day['High'] + prev_day['Low']) / 2  # Bottom CPR
    tc = (pivot - bc) + pivot  # Top CPR
    return pivot, bc, tc

# ============================================
# സ്റ്റോക്ക് അനാലിസിസ് ഫംഗ്ഷൻ
# ============================================
def analyze_stock(symbol):
    try:
        ticker = f"{symbol}.NS"
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        
        if len(df) < 50:
            return None

        ltp = round(df['Close'].iloc[-1], 2)
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        ema_200 = ta.ema(df['Close'], length=200).iloc[-1] if len(df) > 200 else df['Close'].mean()
        
        # MACD
        macd_df = ta.macd(df['Close'])
        if macd_df is not None and not macd_df.empty:
            macd_line = macd_df['MACD_12_26_9'].iloc[-1]
            macd_sig = macd_df['MACDs_12_26_9'].iloc[-1]
        else:
            macd_line = macd_sig = 0
        
        # CPR
        if len(df) >= 2:
            pivot, bc, tc = get_cpr(df)
        else:
            pivot = bc = tc = ltp

        # സിഗ്നൽ ലോജിക്
        signal = "⚪ WAIT"
        reason = "Neutral"
        confidence = 0

        if ltp > ema_200 and rsi > 50 and macd_line > macd_sig:
            if ltp > tc:
                signal = "🟢 STRONG BUY"
                reason = "Bullish + Above CPR Top"
                confidence = 85
            elif ltp > pivot:
                signal = "🟡 WATCH"
                reason = "Above Pivot, Near CPR Top"
                confidence = 65
            else:
                signal = "🔵 OPPORTUNITY"
                reason = "Above 200 EMA, Below Pivot"
                confidence = 55
        elif ltp > ema_200 and rsi > 40:
            signal = "🟠 MONITOR"
            reason = "Above 200 EMA, RSI Recovering"
            confidence = 45
        elif ltp < ema_200:
            signal = "🔴 AVOID"
            reason = "Below 200 EMA (Downtrend)"
            confidence = 0
        elif rsi < 30:
            signal = "🟣 OVERSOLD"
            reason = f"RSI {round(rsi,1)} - Possible Reversal"
            confidence = 30

        return {
            "Stock": symbol,
            "Signal": signal,
            "LTP": float(ltp),
            "RSI": round(float(rsi), 2),
            "Confidence": f"{confidence}%",
            "Reason": reason
        }
    except Exception as e:
        return None

# ============================================
# UI SECTION
# ============================================
st.markdown("""
    <style>
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #00C853 0%, #009624 100%);
        color: white;
        font-size: 18px;
        padding: 12px 24px;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'><h1>⚡ SwingPro Nifty 500 Scanner</h1><p>Technical Analysis Scanner for Nifty 500 Stocks</p></div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    batch_size = st.slider("Stocks to Scan", 50, 500, 200, 50)
    show_all = st.checkbox("Show all scanned stocks", value=False)
    st.markdown("---")
    st.markdown("### 📊 Signal Legend")
    st.markdown("""
    - 🟢 **STRONG BUY** - Bullish + Above CPR
    - 🟡 **WATCH** - Above Pivot
    - 🔵 **OPPORTUNITY** - Above 200 EMA
    - 🟠 **MONITOR** - Recovery mode
    - 🔴 **AVOID** - Below 200 EMA
    - 🟣 **OVERSOLD** - Possible reversal
    """)

# Main Button
if st.button('🚀 START NIFTY 500 SCAN', use_container_width=True):
    try:
        all_symbols = get_nifty_500_symbols()
        target_symbols = all_symbols[:batch_size]
        
        st.info(f"📊 Scanning {len(target_symbols)} Nifty 500 stocks...")
        
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        start_time = time.time()
        
        for i, s in enumerate(target_symbols):
            status_text.text(f"🔍 Scanning ({i+1}/{len(target_symbols)}): {s}")
            status = analyze_stock(s)
            if status:
                results.append(status)
            progress_bar.progress((i + 1) / len(target_symbols))
        
        end_time = time.time()
        status_text.success(f"✅ Scan Completed! Time taken: {round(end_time-start_time, 2)} seconds")
        
        if results:
            final_df = pd.DataFrame(results)
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            strong_buy = len(final_df[final_df['Signal'] == "🟢 STRONG BUY"])
            watch = len(final_df[final_df['Signal'] == "🟡 WATCH"])
            avoid = len(final_df[final_df['Signal'] == "🔴 AVOID"])
            
            with col1:
                st.metric("🟢 Strong Buy", strong_buy)
            with col2:
                st.metric("🟡 Watchlist", watch)
            with col3:
                st.metric("🔴 Avoid", avoid)
            with col4:
                st.metric("📊 Total Scanned", len(results))
            
            # Bullish Opportunities
            st.subheader("🎯 Top Bullish Opportunities")
            bullish_df = final_df[final_df['Signal'].isin(["🟢 STRONG BUY", "🟡 WATCH", "🔵 OPPORTUNITY"])]
            
            if not bullish_df.empty:
                st.dataframe(bullish_df.sort_values('Confidence', ascending=False), use_container_width=True)
            else:
                st.info("No bullish opportunities found at this moment")
            
            # Show all data if requested
            if show_all:
                with st.expander("📋 View Complete Scan Results"):
                    st.dataframe(final_df, use_container_width=True)
                    
                    # Download option
                    csv = final_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv,
                        file_name=f"nifty500_scan_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                # Show avoid list in expander
                avoid_df = final_df[final_df['Signal'] == "🔴 AVOID"]
                if not avoid_df.empty:
                    with st.expander(f"⚠️ Avoid List ({len(avoid_df)} stocks)"):
                        st.dataframe(avoid_df, use_container_width=True)
                        
        else:
            st.warning("No stocks were successfully analyzed. Please check your internet connection.")
            
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.info("💡 Tip: Try reducing the batch size or check your internet connection")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>⚠️ Disclaimer: This is for educational purposes only. Not investment advice.</p>", unsafe_allow_html=True)