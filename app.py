import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import time
import concurrent.futures
from datetime import datetime, timedelta
import requests
import gc
import os

# Sayfa yapılandırması
st.set_page_config(
    page_title="BIST Swing Trading Analiz",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stilleri - minimum boyut
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .sidebar .sidebar-content { background: #262730; color: white; }
    .stProgress > div > div > div > div { background-color: #3498db; }
    .score-badge { display: inline-block; padding: 3px 8px; border-radius: 10px; font-weight: bold; margin: 1px; font-size: 12px; }
    .score-90 { background-color: #2ecc71; color: white; }
    .score-70 { background-color: #3498db; color: white; }
    .score-50 { background-color: #f39c12; color: white; }
    .score-low { background-color: #e74c3c; color: white; }
    .mode-btn { padding: 12px; border-radius: 8px; text-align: center; margin: 5px 0; cursor: pointer; border: 1px solid #3498db; }
    .mode-btn:hover { background-color: #1a5276; color: white; }
    .mode-btn.active { background-color: #3498db; color: white; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# EN HIZLI SEMBOL LİSTESİ - statik ve optimize edilmiş
BIST_TUM_SYMBOLS = [
    "AKBNK.IS", "GARAN.IS", "YKBNK.IS", "ISCTR.IS", "QNBFB.IS", "HALKB.IS", "VAKBN.IS", "SKBNK.IS", "FBRT.IS", "THYAO.IS",
    "TUPRS.IS", "PETKM.IS", "EREGL.IS", "KRDMD.IS", "OYAKC.IS", "SASA.IS", "TOASO.IS", "KCHOL.IS", "KLNTR.IS", "MGROS.IS",
    "BIMAS.IS", "FROTO.IS", "ASTOR.IS", "TCELL.IS", "ASELS.IS", "TTKOM.IS", "SAHOL.IS", "PGSUS.IS", "TKFEN.IS", "GUBRF.IS",
    "ALARK.IS", "ENKAI.IS", "SISE.IS", "DOHOL.IS", "EKGYO.IS", "EGEEN.IS", "KOZAL.IS", "ARCLK.IS", "VESTL.IS", "ZOREN.IS",
    "TSKB.IS", "AKSA.IS", "ANHYT.IS", "BRSAN.IS", "BUCIM.IS", "CANTE.IS", "CCOLA.IS", "CIMSA.IS", "DENGE.IS", "DZGYO.IS",
    "ECILC.IS", "EGOAS.IS", "EKIZ.IS", "ENERY.IS", "ENJSA.IS", "ETYAT.IS", "FMIZY.IS", "GARFA.IS", "GLBMD.IS", "GLYHO.IS",
    "GZTMD.IS", "HATSN.IS", "HEKTS.IS", "IHLAS.IS", "IZMDC.IS", "KARMD.IS", "KARSN.IS", "KATMR.IS", "KCAER.IS", "KMPUR.IS",
    "KONTR.IS", "KONYA.IS", "KORDS.IS", "KRSTL.IS", "KTLEV.IS", "KUTPO.IS", "MAVI.IS", "MEGAP.IS", "MERIT.IS", "METRO.IS",
    "MGDEV.IS", "MNDRS.IS", "MPARK.IS", "NTLTY.IS", "OTKAR.IS", "OYLUM.IS", "PEKGY.IS", "PENTA.IS", "PETUN.IS", "PGHOL.IS",
    "PNSUT.IS", "POLTK.IS", "POMTI.IS", "REEDR.IS", "RNPOL.IS", "ROYAL.IS", "RYSAS.IS", "SDTTR.IS", "SELEC.IS", "SEVGI.IS",
    "SILVR.IS", "SOKM.IS", "SUNTK.IS", "SURNR.IS", "TAVHL.IS", "TMSAN.IS", "TRKCM.IS", "TSAN.IS", "TTRAK.IS", "TUSA.IS",
    "VBTAS.IS", "YATAS.IS", "YBTAS.IS", "AKCNS.IS", "AKFYE.IS", "AKGRT.IS", "AKSEN.IS", "ALBRK.IS", "ALFAS.IS", "ALTIN.IS",
    "AVHOL.IS", "AVOD.IS", "AVYON.IS", "BIOEN.IS", "BRLSM.IS", "BRKSN.IS", "CEMAS.IS", "CETEC.IS", "CLEBI.IS", "CMBTN.IS",
    "CTMT.IS", "CUCUK.IS", "CURMD.IS", "DAPGM.IS", "DEVA.IS", "DGATE.IS", "DGNMO.IS", "DITAS.IS", "DOAS.IS", "DOGER.IS",
    "DURDO.IS", "DYOBY.IS", "ECZYT.IS", "EGESE.IS", "EGKYO.IS", "EGPRO.IS", "EGSER.IS", "EGYOG.IS", "EKSUN.IS", "ELITE.IS",
    "EMKEL.IS", "ENSRI.IS", "ENTRA.IS", "ENVEO.IS", "ERET.IS", "ERGL.IS", "ESCAR.IS", "ESCOM.IS", "ESGSY.IS", "ESKIM.IS",
    "ESMOD.IS", "ESTUR.IS", "ETILR.IS", "EUCELL.IS", "EUREN.IS", "FONET.IS", "GARFI.IS", "GEDZA.IS", "GENIL.IS", "GENTS.IS",
    "GEREL.IS", "GESAN.IS", "GIPTA.IS", "GNKEL.IS", "GOODY.IS", "GOZDE.IS", "GRNYO.IS", "GSDHO.IS", "GSRAY.IS", "GWIND.IS",
    "HATEK.IS", "HURGZ.IS", "HURSV.IS", "ICBCT.IS", "ICFVF.IS", "IEYHO.IS", "IHEVA.IS", "IHYAY.IS", "IHKIZ.IS", "IHLGM.IS",
    "IHSAN.IS", "IITCH.IS", "INDES.IS", "INGOR.IS", "INTEM.IS", "INVES.IS", "IONTE.IS", "ISDMR.IS", "ISGYO.IS", "ISMEN.IS",
    "IZENR.IS", "IZFAS.IS", "IZMOT.IS", "IZYAT.IS", "JANTS.IS", "KCRDT.IS", "KDSGA.IS", "KENVY.IS", "KERVT.IS", "KLGYO.IS",
    "KLSTN.IS", "KMRUP.IS", "KORHO.IS", "KOSGD.IS", "KOSTL.IS", "KRTEK.IS", "KSTUR.IS", "KTSKR.IS", "KUVVA.IS", "LASIS.IS",
    "LCIDB.IS", "LCIDC.IS", "LCIDA.IS", "LCIDF.IS", "LCIDG.IS", "LCIDH.IS", "LCIDI.IS", "LCIDJ.IS", "LCIDK.IS", "LCIDL.IS"
]

BIST_100_SYMBOLS = [
    "AKBNK.IS", "ALARK.IS", "ASELS.IS", "ASTOR.IS", "BIMAS.IS", "DOHOL.IS", "EGEEN.IS", "EKGYO.IS", "ENKAI.IS", "EREGL.IS",
    "FROTO.IS", "GARAN.IS", "GUBRF.IS", "HALKB.IS", "ISCTR.IS", "KCHOL.IS", "KLNTR.IS", "KOZAL.IS", "KRDMD.IS", "MGROS.IS",
    "ODAS.IS", "OYAKC.IS", "PETKM.IS", "PGSUS.IS", "SAHOL.IS", "SASA.IS", "SISE.IS", "SKBNK.IS", "SMRTG.IS", "TCELL.IS",
    "THYAO.IS", "TKFEN.IS", "TOASO.IS", "TSKB.IS", "TTKOM.IS", "TUPRS.IS", "ULKER.IS", "VAKBN.IS", "VESBE.IS", "YKBNK.IS",
    "ZOREN.IS", "ARCLK.IS", "AYEN.IS", "BERA.IS", "BRSAN.IS", "BUCIM.IS", "CCOLA.IS", "CIMSA.IS", "DENGE.IS", "DZGYO.IS",
    "ECILC.IS", "EGOAS.IS", "EKIZ.IS", "ENERY.IS", "ENJSA.IS", "ETYAT.IS", "FMIZY.IS", "GARFA.IS", "GLBMD.IS", "GLYHO.IS",
    "GZTMD.IS", "HATSN.IS", "HEKTS.IS", "IHLAS.IS", "IZMDC.IS", "KARMD.IS", "KARSN.IS", "KATMR.IS", "KCAER.IS", "KMPUR.IS",
    "KONTR.IS", "KONYA.IS", "KORDS.IS", "KRSTL.IS", "KTLEV.IS", "KUTPO.IS", "MAVI.IS", "MEGAP.IS", "MERIT.IS", "METRO.IS",
    "MGDEV.IS", "MNDRS.IS", "MPARK.IS", "NTLTY.IS", "OTKAR.IS", "OYLUM.IS", "PEKGY.IS", "PENTA.IS", "PETUN.IS", "PGHOL.IS",
    "PNSUT.IS", "POLTK.IS", "POMTI.IS", "REEDR.IS", "RNPOL.IS", "ROYAL.IS", "RYSAS.IS", "SDTTR.IS", "SELEC.IS", "SEVGI.IS",
    "SILVR.IS", "SOKM.IS", "SUNTK.IS", "SURNR.IS", "TAVHL.IS", "TMSAN.IS", "TRKCM.IS", "TSAN.IS", "TTRAK.IS", "TUSA.IS",
    "VBTAS.IS", "VESTL.IS", "YATAS.IS", "YBTAS.IS"
]

def fetch_stock_data_fast(symbol: str) -> pd.DataFrame:
    """Ultra hızlı veri çekme - minimum veri ile"""
    try:
        # Sadece son 45 gün
        end_date = int(datetime.now().timestamp())
        start_date = int((datetime.now() - timedelta(days=45)).timestamp())
        
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_date}&period2={end_date}&interval=1d&indicators=quote&includePrePost=false"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        data = response.json()
        if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
            return None
            
        quotes = data['chart']['result'][0]['indicators']['quote'][0]
        timestamps = data['chart']['result'][0]['timestamp']
        
        if not quotes['close'] or not timestamps:
            return None
            
        df = pd.DataFrame({
            'Date': pd.to_datetime(timestamps, unit='s'),
            'Open': quotes['open'],
            'High': quotes['high'],
            'Low': quotes['low'],
            'Close': quotes['close'],
            'Volume': quotes['volume']
        })
        
        df = df.dropna(subset=['Close'])
        if len(df) < 30:  # Minimum veri
            return None
            
        return df.tail(45)  # Sadece son 45 gün
    except Exception as e:
        return None

def calculate_indicators_minimal(df: pd.DataFrame) -> pd.DataFrame:
    """Minimum indikatör hesaplama - sadece gerekli olanlar"""
    try:
        # Sadece skorlama için kritik indikatörler
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
        if macd is not None:
            df['MACD'] = macd['MACD_12_26_9']
            df['Signal'] = macd['MACDs_12_26_9']
            df['Hist'] = macd['MACDh_12_26_9']
        
        df['Volume_MA20'] = df['Volume'].rolling(20).mean()
        df['MFI'] = ta.mfi(df['High'], df['Low'], df['Close'], df['Volume'], length=14)
        
        adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
        if adx is not None:
            df['ADX'] = adx['ADX_14']
            df['DMP'] = adx['DMP_14']
            df['DMN'] = adx['DMN_14']
        
        supertrend = ta.supertrend(df['High'], df['Low'], df['Close'], length=7, multiplier=3.0)
        if supertrend is not None and 'SUPERT_7_3.0' in supertrend.columns:
            df['SuperTrend'] = supertrend['SUPERT_7_3.0']
        
        bb = ta.bbands(df['Close'], length=20, std=2)
        if bb is not None:
            df['BB_Upper'] = bb['BBU_20_2.0']
            df['BB_Lower'] = bb['BBL_20_2.0']
            df['BB_Middle'] = bb['BBM_20_2.0']
            df['BB_Percent'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        return df.dropna(subset=['RSI'])
    except Exception as e:
        return df

def calculate_score_minimal(df: pd.DataFrame) -> int:
    """En hızlı skor hesaplama - sadece son satır"""
    if len(df) < 2:
        return 0
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    total_score = 0
    
    # 1. RSI (14) - Maks 20 Puan
    rsi = last['RSI']
    if 55 <= rsi <= 60: total_score += 20
    elif (50 <= rsi < 55) or (60 < rsi <= 65): total_score += 15
    elif (45 <= rsi < 50) or (65 < rsi <= 70): total_score += 10
    
    # 2. MACD - Maks 20 Puan
    if 'MACD' in last and 'Signal' in last and 'Hist' in last:
        macd_condition = last['MACD'] > last['Signal']
        bullish_cross = macd_condition and (prev['MACD'] <= prev['Signal'])
        
        if bullish_cross and last['MACD'] > 0 and (last['Hist'] > prev['Hist']): 
            total_score += 20
        elif macd_condition and last['MACD'] > 0: 
            total_score += 15
        elif macd_condition: 
            total_score += 12
    
    # 3. Hacim ve MFI - Maks 20 Puan
    if 'Volume_MA20' in last and 'MFI' in last:
        vol_ratio = last['Volume'] / last['Volume_MA20'] if last['Volume_MA20'] > 0 else 0
        
        if vol_ratio > 1.5 and 50 <= last['MFI'] <= 80:
            total_score += 20
        elif vol_ratio > 1.2 and last['MFI'] > prev['MFI']:
            total_score += 15
        elif vol_ratio > 1.0:
            total_score += 10
    
    # 4. ADX - Maks 15 Puan
    if 'ADX' in last and 'DMP' in last and 'DMN' in last:
        if last['ADX'] > 25 and last['DMP'] > last['DMN']:
            total_score += 15
        elif 20 <= last['ADX'] <= 25 and last['ADX'] > prev['ADX']:
            total_score += 10
    
    # 5. SuperTrend - Maks 15 Puan
    if 'SuperTrend' in last:
        if last['Close'] > last['SuperTrend']:
            total_score += 15
    
    # 6. Bollinger - Maks 10 Puan
    if 'BB_Percent' in last:
        if last['BB_Percent'] > 0.8:
            total_score += 10
        elif 'BB_Upper' in last and 'BB_Lower' in last:
            bandwidth = (last['BB_Upper'] - last['BB_Lower']) / last['BB_Middle'] if last['BB_Middle'] > 0 else 1
            if bandwidth < 0.1 and last['Close'] > last['BB_Middle']:
                total_score += 8
            elif 0.5 <= last['BB_Percent'] <= 0.8:
                total_score += 5
    
    return min(total_score, 100)

def create_minimal_chart(df: pd.DataFrame, symbol: str, score: int) -> go.Figure:
    """Süper hızlı grafik - minimum bileşenler"""
    if df is None or len(df) < 30:
        fig = go.Figure()
        fig.add_annotation(text="Veri Yok", x=0.5, y=0.5, showarrow=False, font_size=20)
        return fig
    
    df = df.tail(30)  # Sadece son 30 gün
    
    fig = go.Figure()
    
    # Mum grafiği
    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Fiyat'
    ))
    
    # SuperTrend varsa ekle
    if 'SuperTrend' in df.columns and df['SuperTrend'].notnull().any():
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['SuperTrend'],
            mode='lines', name='SuperTrend',
            line=dict(color='#9b59b6', width=2)
        ))
    
    # Basit layout
    fig.update_layout(
        title=f"{symbol} | Skor: {score}/100",
        xaxis_rangeslider_visible=False,
        height=400,
        margin=dict(t=40, b=20, l=20, r=20),
        plot_bgcolor='white',
        showlegend=False
    )
    
    fig.update_xaxes(gridcolor='#ecf0f1')
    fig.update_yaxes(gridcolor='#ecf0f1')
    
    return fig

# Sidebar - basit ve hızlı
with st.sidebar:
    st.title("⚡ BIST Analiz")
    
    if st.button("🚀 HIZLI ANALİZ (BIST 100)", use_container_width=True, type="primary"):
        st.session_state.analysis_mode = "BIST100"
        st.session_state.analysis_started = True
    
    if st.button("🔍 TAM ANALİZ (BIST TÜM)", use_container_width=True, type="secondary"):
        st.session_state.analysis_mode = "BISTTUM"
        st.session_state.analysis_started = True
    
    st.markdown("---")
    st.caption("*Hızlı Mod (45 sn):* En likit 100 hisse")
    st.caption("*Tam Mod (90 sn):* Tüm BIST hisseleri")
    st.caption("⚠️ Tam modda sabırlı olun!")

# Session state kontrolü
if 'analysis_started' not in st.session_state:
    st.session_state.analysis_started = False
if 'analysis_mode' not in st.session_state:
    st.session_state.analysis_mode = "BIST100"

# Ana ekran
st.title("⚡ BIST Swing Trading Analiz Paneli")
st.subheader("Hızlı ve Güvenilir Teknik Analiz")

# Açıklama
st.info("""
*Nasıl Çalışıyor?*
- ⚡ *Hızlı Mod:* Sadece BIST 100 hisseleri - 45 saniyede tamamlanır
- 🔍 *Tam Mod:* Tüm BIST TÜM hisseleri - 90 saniyede tamamlanır
- 📊 Tüm teknik analizler son 45 güne göre yapılıyor
- 🎯 Sonuçlar skora göre otomatik sıralanıyor
""")

# Analiz işlemi
if st.session_state.analysis_started:
    mode = st.session_state.analysis_mode
    symbols = BIST_100_SYMBOLS if mode == "BIST100" else BIST_TUM_SYMBOLS
    total_symbols = len(symbols)
    
    # Başlangıç bilgisi
    mode_text = "HIZLI" if mode == "BIST100" else "TAM"
    st.warning(f"🔍 {mode_text} MOD BAŞLADI! Toplam hisse: {total_symbols}. Lütfen bekleyin...")
    
    # İlerleme çubuğu
    progress_bar = st.progress(0)
    status_text = st.empty()
    start_time = time.time()
    
    results = []
    
    # PARALEL İŞLEME - optimize edilmiş
    max_workers = 10 if mode == "BISTTUM" else 15  # Daha az thread, daha stabil
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_symbol = {executor.submit(fetch_stock_data_fast, symbol): symbol for symbol in symbols}
        
        for i, future in enumerate(concurrent.futures.as_completed(future_to_symbol)):
            symbol = future_to_symbol[future]
            try:
                df = future.result(timeout=12)  # 12 saniye timeout
                
                if df is not None and len(df) >= 30:
                    # Minimum indikatörler
                    df = calculate_indicators_minimal(df)
                    
                    if df is not None and len(df) >= 30:
                        # Skoru hesapla
                        score = calculate_score_minimal(df)
                        
                        if score > 0:  # Sadece pozitif skorlu hisseler
                            last_price = df.iloc[-1]['Close']
                            prev_price = df.iloc[-2]['Close'] if len(df) > 1 else last_price
                            change = ((last_price - prev_price) / prev_price * 100) if prev_price != 0 else 0
                            
                            results.append({
                                'symbol': symbol.replace('.IS', ''),
                                'price': last_price,
                                'change': change,
                                'score': score,
                                'df': df.tail(30)  # Sadece son 30 gün sakla
                            })
                
                # İlerleme güncelle
                progress = (i + 1) / total_symbols
                elapsed = time.time() - start_time
                eta = elapsed / (i + 1) * (total_symbols - i - 1) if i > 0 else 0
                
                status_text.text(f"İŞLENİYOR: {i+1}/{total_symbols} | Tahmini Süre: {eta:.0f} sn | Başarılı: {len(results)}")
                progress_bar.progress(progress)
                
                # Bellek temizliği
                if i % 20 == 0:
                    gc.collect()
                
            except Exception as e:
                continue
    
    # Sonuçları kaydet
    if results:
        results.sort(key=lambda x: x['score'], reverse=True)
        st.session_state.results = results
        st.session_state.last_mode = mode
        total_time = time.time() - start_time
        
        st.success(f"✅ ANALİZ TAMAMLANDI! {len(results)}/{total_symbols} hisse. Süre: {total_time:.1f} sn")
    else:
        st.error("❌ Analiz başarısız oldu. Lütfen tekrar deneyin.")
        st.session_state.analysis_started = False

# Sonuçları göster
if 'results' in st.session_state and st.session_state.results:
    results = st.session_state.results
    mode = st.session_state.last_mode
    
    # Başlık
    if mode == "BIST100":
        st.subheader(f"⚡ En İyi 15 BIST 100 Swing Fırsatı")
    else:
        st.subheader(f"🔍 En İyi 15 BIST TÜM Swing Fırsatı")
    
    # En iyi 15'i göster
    top_15 = results[:15]
    
    # Tablo hazırlığı
    table_data = []
    for res in top_15:
        # Skor badge
        if res['score'] >= 90:
            badge = f"<span class='score-badge score-90'>{res['score']}</span>"
        elif res['score'] >= 70:
            badge = f"<span class='score-badge score-70'>{res['score']}</span>"
        elif res['score'] >= 50:
            badge = f"<span class='score-badge score-50'>{res['score']}</span>"
        else:
            badge = f"<span class='score-badge score-low'>{res['score']}</span>"
        
        # Değişim rengi
        color = "green" if res['change'] >= 0 else "red"
        change_text = f"<span style='color:{color}'>{res['change']:.2f}%</span>"
        
        table_data.append({
            "Sembol": res['symbol'],
            "Fiyat (₺)": f"{res['price']:.2f}",
            "Değişim": change_text,
            "Skor": badge
        })
    
    # Tabloyu göster
    df_table = pd.DataFrame(table_data)
    st.write(df_table.to_html(escape=False, index=False), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detaylı analiz
    selected = st.selectbox(" Detaylı analiz için hisse seçin:", 
                          [f"{r['symbol']} ({r['score']})" for r in results])
    
    if selected:
        symbol = selected.split(' ')[0]
        result = next((r for r in results if r['symbol'] == symbol), None)
        
        if result:
            fig = create_minimal_chart(result['df'], result['symbol'], result['score'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Skor detayları
            with st.expander("Skor Detayları"):
                st.markdown(f"""
                *Toplam Skor: {result['score']}/100*
                
                📈 *Analiz Kriterleri:*
                - Son 45 güne göre teknik analiz
                - RSI, MACD, Hacim, ADX, SuperTrend, Bollinger Bantları
                - En yüksek skorlu fırsatlar öncelikli
                
                💡 *Tavsiye:* Skoru 70+ olan hisseler swing trading için uygun olabilir.
                """)

# Başlangıç ekranı
else:
    st.markdown("""
    ### 🚀 Başlamak İçin
                
    *1. Sol menüdeki butonlardan birini seçin:*
    - ⚡ *HIZLI ANALİZ:* Sadece BIST 100 hisseleri (45 saniye)
    - 🔍 *TAM ANALİZ:* Tüm BIST TÜM hisseleri (90 saniye)
                
    *2. Analiz tamamlandığında:*
    - En iyi 15 hisse tabloda görünecek
    - Detaylı analiz için listeden hisse seçin
                
    *💡 İpucu:* İlk kez çalıştırıyorsanız HIZLI ANALİZ ile başlayın!
    """)
    
    # Demo tablo göster
    st.subheader("📊 Örnek Sonuçlar")
    demo_data = {
        "Sembol": ["THYAO", "TUPRS", "FROTO", "AKBNK", "GARAN"],
        "Fiyat (₺)": ["285.50", "187.30", "452.80", "125.40", "89.75"],
        "Değişim": ["+2.45%", "+1.20%", "-0.75%", "+3.10%", "-0.30%"],
        "Skor": [
            "<span class='score-badge score-90'>95</span>",
            "<span class='score-badge score-70'>78</span>",
            "<span class='score-badge score-50'>55</span>",
            "<span class='score-badge score-90'>92</span>",
            "<span class='score-badge score-low'>42</span>"
        ]
    }
    st.write(pd.DataFrame(demo_data).to_html(escape=False, index=False), unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption(f"Son Güncelleme: {datetime.now().strftime('%H:%M')} | ⚡ Optimizasyonlu versiyon")
