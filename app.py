import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import requests
import json
import time

# ── PAGE CONFIG ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinSentinel — AI Market Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── THEME / CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* Dark background */
  .stApp { background-color: #060D1F; }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background-color: #0C1830;
    border-right: 1px solid rgba(255,255,255,0.07);
  }
  [data-testid="stSidebar"] * { color: #8BA3C7 !important; }
  [data-testid="stSidebar"] .sidebar-title { color: #E8F0FE !important; }

  /* Main text */
  h1, h2, h3, h4, p, label, .stMarkdown { color: #E8F0FE !important; }

  /* Metric cards */
  [data-testid="stMetric"] {
    background: #111E35;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 16px !important;
  }
  [data-testid="stMetricLabel"] { color: #8BA3C7 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px; }
  [data-testid="stMetricValue"] { color: #E8F0FE !important; font-family: 'DM Mono', monospace !important; }
  [data-testid="stMetricDelta"] { font-family: 'DM Mono', monospace !important; }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background-color: #0C1830;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    gap: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    color: #8BA3C7 !important;
    background: transparent;
    border-radius: 0;
    font-size: 13px;
    font-weight: 500;
  }
  .stTabs [aria-selected="true"] {
    color: #38BDF8 !important;
    border-bottom: 2px solid #38BDF8 !important;
    background: transparent !important;
  }
  .stTabs [data-baseweb="tab-panel"] {
    background: #111E35;
    border: 1px solid rgba(255,255,255,0.07);
    border-top: none;
    border-radius: 0 0 12px 12px;
    padding: 16px;
  }

  /* Dataframe */
  [data-testid="stDataFrame"] { background: #111E35 !important; }
  .dvn-scroller { background: #111E35 !important; }

  /* Input */
  .stTextInput input, .stTextArea textarea {
    background: #111E35 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    color: #E8F0FE !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
  }
  .stTextInput input::placeholder { color: #4A6080 !important; }

  /* Buttons */
  .stButton button {
    background: #38BDF8 !important;
    color: #060D1F !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
  }
  .stButton button:hover { opacity: 0.85 !important; }

  /* Selectbox */
  .stSelectbox select, [data-baseweb="select"] {
    background: #111E35 !important;
    color: #E8F0FE !important;
    border-color: rgba(255,255,255,0.07) !important;
  }

  /* Divider */
  hr { border-color: rgba(255,255,255,0.07) !important; }

  /* Cards */
  .fin-card {
    background: #111E35;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 14px;
  }
  .ai-card {
    background: linear-gradient(135deg, rgba(139,92,246,0.08), rgba(56,189,248,0.05));
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 18px;
  }
  .ai-response {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid #8B5CF6;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin-top: 12px;
    color: #8BA3C7;
    font-size: 13px;
    line-height: 1.7;
  }
  .insight-block {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 14px;
  }
  .tag-bull { background: rgba(16,185,129,0.15); color: #10B981; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
  .tag-bear { background: rgba(239,68,68,0.15);  color: #EF4444; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
  .tag-neut { background: rgba(245,158,11,0.15); color: #F59E0B; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
  .kpi-val  { font-family: 'DM Mono', monospace; font-size: 28px; font-weight: 700; }
  .section-title { font-size: 13px; font-weight: 600; color: #E8F0FE; letter-spacing: 0.3px; }
  .muted { color: #8BA3C7; font-size: 12px; }
  .ticker-bar {
    background: #0C1830;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    padding: 8px 0;
    overflow: hidden;
    white-space: nowrap;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
  }
  .up   { color: #10B981; }
  .down { color: #EF4444; }
</style>
""", unsafe_allow_html=True)

# ── PLOTLY THEME ──────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor='#111E35',
    plot_bgcolor='#111E35',
    font=dict(family='DM Sans', color='#8BA3C7', size=11),
    margin=dict(l=40, r=20, t=30, b=40),
    xaxis=dict(gridcolor='rgba(255,255,255,0.04)', linecolor='rgba(255,255,255,0.07)', tickfont=dict(size=10)),
    yaxis=dict(gridcolor='rgba(255,255,255,0.04)', linecolor='rgba(255,255,255,0.07)', tickfont=dict(size=10)),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=10, color='#8BA3C7'), orientation='h', yanchor='bottom', y=1.02),
    hovermode='x unified',
    hoverlabel=dict(bgcolor='#162448', font=dict(color='#E8F0FE', size=11), bordercolor='#38BDF8'),
)

COLORS = {
    'blue': '#38BDF8', 'green': '#10B981', 'red': '#EF4444',
    'amber': '#F59E0B', 'purple': '#8B5CF6', 'teal': '#14B8A6',
    'gray': '#8BA3C7', 'navy': '#1A3A5C',
}

# ── DATA ──────────────────────────────────────────────────────────────
months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar']

SENTIMENT_DATA = {
    'months': months,
    'bull':   [48, 52, 58, 54, 63, 67],
    'bear':   [30, 25, 22, 26, 18, 16],
    'nlp':    [55, 60, 66, 62, 70, 74],
}

VAR_DATA = {
    'months': months,
    'var95':  [2.1, 2.4, 2.9, 3.2, 2.7, 2.8],
    'var99':  [3.4, 3.9, 4.5, 5.0, 4.2, 4.4],
}

SECTORS = pd.DataFrame({
    'Sector':   ['Technology', 'Energy', 'Financials', 'Healthcare', 'Consumer Disc.', 'Utilities', 'Real Estate'],
    'Return':   [2.4, 1.8, 0.9, 0.3, -0.4, -0.9, -1.6],
    'Sentiment':['Bullish', 'Bullish', 'Bullish', 'Neutral', 'Neutral', 'Bearish', 'Bearish'],
})

FACTORS = pd.DataFrame({
    'Factor':  ['Sentiment', 'Momentum', 'Quality', 'Size', 'Low Vol', 'Value'],
    'Return':  [3.2, 2.8, 1.4, 0.7, 1.1, -0.6],
})

RECENT_EARNINGS = pd.DataFrame({
    'Ticker': ['NVDA', 'MSFT', 'META', 'GOOGL', 'AMZN', 'TSLA'],
    'Company': ['NVIDIA Corp', 'Microsoft', 'Meta Platforms', 'Alphabet', 'Amazon', 'Tesla'],
    'Date': ['Feb 28', 'Jan 31', 'Jan 29', 'Jan 30', 'Feb 1', 'Jan 24'],
    'Sentiment': ['Bullish', 'Bullish', 'Bullish', 'Neutral', 'Bullish', 'Bearish'],
    'NLP Score': ['+0.87', '+0.72', '+0.68', '+0.31', '+0.61', '-0.44'],
    'AI Signal': ['▲ Strong Buy', '▲ Buy', '▲ Buy', '→ Hold', '▲ Buy', '▼ Reduce'],
    'Post-Earnings Move': ['+12.4%', '+4.8%', '+6.2%', '+1.1%', '+5.9%', '-11.2%'],
})

UPCOMING_EARNINGS = pd.DataFrame({
    'Ticker': ['ORCL', 'JPM', 'GS', 'NFLX', 'TSM', 'META', 'MSFT', 'GOOGL'],
    'Company': ['Oracle Corp', 'JPMorgan Chase', 'Goldman Sachs', 'Netflix', 'TSMC', 'Meta Platforms', 'Microsoft', 'Alphabet'],
    'Expected Date': ['Apr 10', 'Apr 11', 'Apr 14', 'Apr 15', 'Apr 17', 'Apr 23', 'Apr 24', 'Apr 25'],
    'EPS Estimate': ['$1.64', '$4.19', '$8.56', '$5.68', '$2.11', '$5.25', '$3.22', '$2.01'],
    'Rev Estimate': ['$14.1B', '$43.6B', '$12.9B', '$10.2B', '$25.6B', '$41.2B', '$68.4B', '$89.1B'],
    'AI Outlook': ['Bullish', 'Bullish', 'Neutral', 'Bullish', 'Bullish', 'Bullish', 'Bullish', 'Neutral'],
    'Key Watchpoint': [
        'Cloud rev guidance', 'Net interest income', 'Trading desk perf',
        'Subscriber growth', 'AI chip demand', 'Capex for AI infra',
        'Azure AI growth', 'Search vs AI cannibaliz.',
    ],
})

ANOMALIES = pd.DataFrame({
    'Ticker': ['TSLA', 'INTC', 'PFE', 'RIVN', 'NYCB', 'DIS'],
    'Company': ['Tesla', 'Intel', 'Pfizer', 'Rivian', 'NY Comm Bank', 'Walt Disney'],
    'Anomaly Type': ['Tone Collapse', 'Guidance Divergence', 'Sentiment Reversal', 'Liquidity Signal', 'Stress Indicator', 'Mgmt Confidence Drop'],
    'Severity': ['High', 'High', 'Medium', 'High', 'High', 'Medium'],
    'AI Detection Detail': [
        'Hedging language +78% vs prior call. CEO confidence at 24-month low.',
        'Revenue guidance 11% below consensus. CapEx signals restructuring.',
        'Narrative shift from pipeline optimism to litigation risk. Neg tone +45%.',
        'Cash runway language entered earnings call for first time.',
        'Loan loss provision language 3.2× above sector average.',
        'Forward guidance hedging index at 5-year high.',
    ],
    'Detected': ['2h ago', '1d ago', '2d ago', '3d ago', '5d ago', '6d ago'],
})

MACRO = [
    ('US CPI YoY',     '3.1%',   'Neutral', '▼'),
    ('Fed Funds Rate', '5.25%',  'Bearish', '→'),
    ('10Y Treasury',   '4.58%',  'Bearish', '▲'),
    ('US PMI',         '52.4',   'Bullish', '▲'),
    ('Unemployment',   '3.7%',   'Bullish', '→'),
    ('USD Index',      '104.2',  'Neutral', '▼'),
    ('VIX',            '18.42',  'Neutral', '▲'),
    ('Gold ($/oz)',    '$2,312',  'Bullish', '▲'),
]

TICKER = [
    ('SPY',  '568.34', '+0.84%', True),
    ('QQQ',  '481.22', '+1.12%', True),
    ('BTC',  '87,440', '-1.23%', False),
    ('AAPL', '228.50', '+0.56%', True),
    ('MSFT', '419.80', '+0.91%', True),
    ('NVDA', '882.70', '+2.34%', True),
    ('TSLA', '245.60', '-1.78%', False),
    ('GLD',  '231.50', '+0.23%', True),
    ('VIX',  '18.42',  '+3.20%', False),
    ('DXY',  '104.20', '-0.18%', False),
]

AI_RESPONSES = [
    "**FinBERT + Claude Analysis:** NLP scan of 4,200+ articles this week identifies three primary tech sentiment drivers: (1) NVDA forward guidance reinforcing AI infrastructure thesis — bullish tone at 87% confidence; (2) Fed language shift toward neutral — bond-equity correlation easing; (3) Institutional net buying in semiconductors up $2.1B per alternative data. **Recommendation:** Maintain overweight AI-exposed tech with momentum factor tilt.",
    "**Risk Assessment:** Cross-asset correlation rising — 30-day rolling S&P 500/IG credit correlation at 0.78, up from 0.52. VIX term structure showing mild backwardation in 30–60 day window, historically a precursor to volatility events within 45 days (64% of cases). Portfolio heat concentrated in mega-cap growth. **Recommendation:** Consider tactical rotation toward defensives for risk-adjusted improvement.",
    "**Macro Regime Model (87.4% confidence):** Current state = Late Cycle Expansion. Supporting signals: PMI above 52; yield curve -28bps, inverted but improving; IG credit spreads at 128bps — below stress threshold. Historical analogues suggest 6–12 months of equity expansion possible, though tail risk is elevated given geopolitical uncertainty signals in news flow.",
    "**Earnings Season NLP Summary:** Q4 2025 management confidence language up 14% vs Q3. However, CapEx guidance language reduced in 38% of S&P 500 calls — potential demand signal softening for industrials. AI/ML investment commitment language at all-time high across Tech, Finance, and Healthcare — supporting AI infrastructure bull thesis through 2026.",
    "**Sentiment Factor Analysis:** Current composite NLP sentiment score at 74 — highest in rolling 12-month window. Bull/Bear ratio at 4.2:1, historically associated with positive 60-day forward returns in 71% of cases. Key risk: sentiment positioning is stretched; crowding risk in large-cap tech is elevated with potential for sentiment-driven mean reversion on negative catalysts.",
]

# ── SIDEBAR ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ FinSentinel")
    st.markdown("<div class='muted'>AI Market Intelligence Platform</div>", unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navigation",
        ["📊 Market Overview", "🧠 Sentiment Engine", "⬡ Risk Monitor", "📋 Earnings Intel", "🤖 AI Copilot"],
        label_visibility="collapsed"
    )
    st.divider()

    st.markdown("**Market Sentiment Pulse**")
    st.progress(0.67, text="Bullish 67%")
    st.progress(0.22, text="Neutral 22%")
    st.progress(0.11, text="Bearish 11%")
    st.divider()

    st.markdown("**Filters**")
    time_range = st.selectbox("Time Range", ["1M", "3M", "6M", "1Y"], index=2)
    asset_class = st.multiselect("Asset Class", ["Equities", "Fixed Income", "Commodities", "FX"], default=["Equities"])
    st.divider()

    st.markdown(f"<div class='muted'>🟢 Live  |  {datetime.now().strftime('%H:%M:%S')} UTC</div>", unsafe_allow_html=True)

# ── TICKER BAR ────────────────────────────────────────────────────────
ticker_html = " &nbsp;&nbsp;|&nbsp;&nbsp; ".join(
    f"<span style='color:#E8F0FE;font-weight:600'>{sym}</span> "
    f"<span style='color:#8BA3C7'>{price}</span> "
    f"<span style='color:{'#10B981' if up else '#EF4444'}'>{chg}</span>"
    for sym, price, chg, up in TICKER * 3
)
st.markdown(f"<div class='ticker-bar'>{ticker_html}</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# PAGE: MARKET OVERVIEW
# ═══════════════════════════════════════════════════════════════════════
if page == "📊 Market Overview":

    st.markdown("## Market Intelligence Overview")
    st.markdown("<div class='muted'>AI-Driven Sentiment Analysis & Portfolio Risk Management — Financial Systems</div>", unsafe_allow_html=True)
    st.divider()

    # KPI ROW
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1: st.metric("Market Sentiment Score", "67.4", "+4.2 pts", delta_color="normal")
    with k2: st.metric("Portfolio VaR (95%)", "−2.8%", "−0.3% vs prev", delta_color="inverse")
    with k3: st.metric("NLP Signal Strength", "0.84", "+0.06", delta_color="normal")
    with k4: st.metric("Sector Dispersion", "12.3%", "+1.8%", delta_color="inverse")
    with k5: st.metric("AI Confidence Index", "87.4%", "+2.1%", delta_color="normal")

    st.markdown("<br>", unsafe_allow_html=True)

    # AI INSIGHT PANEL
    st.markdown("""
    <div class='ai-card'>
      <div style='display:flex;align-items:center;gap:12px;margin-bottom:14px'>
        <div style='width:36px;height:36px;border-radius:9px;background:linear-gradient(135deg,#8B5CF6,#38BDF8);display:flex;align-items:center;justify-content:center;font-size:18px'>✦</div>
        <div>
          <div style='font-size:14px;font-weight:600;color:#E8F0FE'>AI Analyst Copilot</div>
          <div style='font-size:11px;color:#8BA3C7'>Powered by FinBERT + Claude — Institutional-Grade Insights</div>
        </div>
        <div style='margin-left:auto;text-align:right'>
          <div style='font-size:22px;font-weight:700;color:#10B981;font-family:monospace'>87.4%</div>
          <div style='font-size:10px;color:#8BA3C7'>Model Confidence</div>
        </div>
      </div>
      <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px'>
        <div class='insight-block'>
          <span class='tag-bull'>▲ Bullish Signal</span>
          <p style='font-size:12px;color:#8BA3C7;margin-top:8px;line-height:1.6'>Fed communication tone shifted from hawkish to neutral. NLP detects 34% reduction in tightening language — historically signals 60-day equity upside of 4–7%.</p>
        </div>
        <div class='insight-block'>
          <span class='tag-bear'>▼ Risk Flag</span>
          <p style='font-size:12px;color:#8BA3C7;margin-top:8px;line-height:1.6'>Tech sector earnings call hedging language spiked 28% QoQ. Terms "cautious," "uncertain," "monitoring" at above 5-year average frequency.</p>
        </div>
        <div class='insight-block'>
          <span class='tag-neut'>◆ Macro Alert</span>
          <p style='font-size:12px;color:#8BA3C7;margin-top:8px;line-height:1.6'>Cross-asset correlation rising: S&P 500 / IG credit 30-day correlation at 0.78, up from 0.52. Regime stress probability at 38%.</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # CHARTS ROW 1
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-title'>📈 Market Sentiment Index</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=SENTIMENT_DATA['bull'], name='Bullish',
            line=dict(color=COLORS['green'], width=2.5), fill='tozeroy',
            fillcolor='rgba(16,185,129,0.08)', mode='lines+markers',
            marker=dict(size=5, color=COLORS['green'])))
        fig.add_trace(go.Scatter(x=months, y=SENTIMENT_DATA['bear'], name='Bearish',
            line=dict(color=COLORS['red'], width=2.5), fill='tozeroy',
            fillcolor='rgba(239,68,68,0.06)', mode='lines+markers',
            marker=dict(size=5, color=COLORS['red'])))
        fig.add_trace(go.Scatter(x=months, y=SENTIMENT_DATA['nlp'], name='NLP Score',
            line=dict(color=COLORS['blue'], width=2, dash='dash'), mode='lines+markers',
            marker=dict(size=4, color=COLORS['blue'])))
        fig.update_layout(**PLOT_LAYOUT, height=280, yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown("<div class='section-title'>⬡ Portfolio VaR History</div>", unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=months, y=VAR_DATA['var95'], name='VaR 95%',
            marker_color=COLORS['red'], marker_line_width=0, opacity=0.8))
        fig2.add_trace(go.Bar(x=months, y=VAR_DATA['var99'], name='VaR 99%',
            marker_color=COLORS['purple'], marker_line_width=0, opacity=0.6))
        fig2.update_layout(**PLOT_LAYOUT, height=280, barmode='group',
            yaxis=dict(**PLOT_LAYOUT['yaxis'], ticksuffix='%'))
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    # CHARTS ROW 2
    col3, col4, col5 = st.columns(3)

    with col3:
        st.markdown("<div class='section-title'>⊞ Sector Sentiment</div>", unsafe_allow_html=True)
        colors_bar = [COLORS['green'] if v >= 0 else COLORS['red'] for v in SECTORS['Return']]
        fig3 = go.Figure(go.Bar(
            x=SECTORS['Return'], y=SECTORS['Sector'], orientation='h',
            marker_color=colors_bar, marker_line_width=0, opacity=0.85,
            text=[f"{v:+.1f}%" for v in SECTORS['Return']],
            textposition='outside', textfont=dict(size=10, color='#8BA3C7')
        ))
        fig3.update_layout(**PLOT_LAYOUT, height=300,
            xaxis=dict(**PLOT_LAYOUT['xaxis'], ticksuffix='%'))
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

    with col4:
        st.markdown("<div class='section-title'>◈ Factor Attribution</div>", unsafe_allow_html=True)
        colors_f = [COLORS['green'] if v >= 0 else COLORS['red'] for v in FACTORS['Return']]
        fig4 = go.Figure(go.Bar(
            x=FACTORS['Return'], y=FACTORS['Factor'], orientation='h',
            marker_color=colors_f, marker_line_width=0, opacity=0.85,
            text=[f"{v:+.1f}%" for v in FACTORS['Return']],
            textposition='outside', textfont=dict(size=10, color='#8BA3C7')
        ))
        fig4.update_layout(**PLOT_LAYOUT, height=300,
            xaxis=dict(**PLOT_LAYOUT['xaxis'], ticksuffix='%'))
        st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})

    with col5:
        st.markdown("<div class='section-title'>◷ Macro Signal Monitor</div>", unsafe_allow_html=True)
        for name, val, sig, trend in MACRO:
            col_sig = '#10B981' if sig == 'Bullish' else '#EF4444' if sig == 'Bearish' else '#F59E0B'
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;align-items:center;
              padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.04)'>
              <span style='font-size:12px;color:#8BA3C7'>{name}</span>
              <div style='display:flex;align-items:center;gap:8px'>
                <span style='color:{col_sig};font-size:12px;font-weight:600'>{trend}</span>
                <span style='font-family:monospace;font-size:12px;color:#E8F0FE'>{val}</span>
              </div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# PAGE: SENTIMENT ENGINE
# ═══════════════════════════════════════════════════════════════════════
elif page == "🧠 Sentiment Engine":

    st.markdown("## Sentiment Analysis Engine")
    st.markdown("<div class='muted'>NLP-driven sentiment classification across news, filings, and earnings transcripts</div>", unsafe_allow_html=True)
    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Composite NLP Score", "74.0", "+4.2 pts")
    with c2: st.metric("Articles Processed Today", "12,847", "+1,204")
    with c3: st.metric("Bull/Bear Ratio", "4.2:1", "+0.8")
    with c4: st.metric("Signal Confidence", "87.4%", "+2.1%")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("<div class='section-title'>📈 Sentiment Trend — 6 Month Rolling</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=SENTIMENT_DATA['bull'], name='Bullish %',
            line=dict(color=COLORS['green'], width=3),
            fill='tozeroy', fillcolor='rgba(16,185,129,0.1)',
            mode='lines+markers', marker=dict(size=7, color=COLORS['green'])))
        fig.add_trace(go.Scatter(x=months, y=SENTIMENT_DATA['bear'], name='Bearish %',
            line=dict(color=COLORS['red'], width=3),
            fill='tozeroy', fillcolor='rgba(239,68,68,0.08)',
            mode='lines+markers', marker=dict(size=7, color=COLORS['red'])))
        fig.add_trace(go.Scatter(x=months, y=SENTIMENT_DATA['nlp'], name='NLP Composite',
            line=dict(color=COLORS['blue'], width=2.5, dash='dot'),
            mode='lines+markers', marker=dict(size=6, color=COLORS['blue'])))
        fig.add_hline(y=50, line_dash='dash', line_color='rgba(255,255,255,0.2)',
                      annotation_text='Neutral 50', annotation_font_color='#8BA3C7')
        fig.update_layout(**PLOT_LAYOUT, height=350, yaxis_range=[0, 100],
            yaxis=dict(**PLOT_LAYOUT['yaxis'], ticksuffix='%'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown("<div class='section-title'>🥧 Current Distribution</div>", unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=['Bullish', 'Neutral', 'Bearish'],
            values=[67, 22, 11],
            marker_colors=[COLORS['green'], COLORS['amber'], COLORS['red']],
            hole=0.55,
            textfont=dict(size=11, color='white'),
        ))
        fig_pie.update_layout(
            paper_bgcolor='#111E35', plot_bgcolor='#111E35',
            margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(font=dict(color='#8BA3C7', size=10), orientation='h', y=-0.1),
            height=240, showlegend=True,
            annotations=[dict(text='67%<br><span style="font-size:10px">Bull</span>',
                              x=0.5, y=0.5, font_size=14, showarrow=False, font_color='#10B981')]
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

        st.markdown("<div class='section-title'>📡 NLP Data Sources</div>", unsafe_allow_html=True)
        sources = [('News Wires', '52%', COLORS['blue']), ('Earnings Calls', '24%', COLORS['purple']),
                   ('Social Media', '14%', COLORS['amber']), ('Filings', '10%', COLORS['teal'])]
        for name, pct, col in sources:
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;padding:4px 0'>
              <span style='font-size:12px;color:#8BA3C7'>{name}</span>
              <span style='font-size:12px;color:{col};font-family:monospace;font-weight:600'>{pct}</span>
            </div>""", unsafe_allow_html=True)

    # News volume chart
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>≋ Daily News Sentiment Volume</div>", unsafe_allow_html=True)
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Mon', 'Tue']
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(x=days, y=[142, 188, 205, 176, 230, 198, 214], name='Positive',
        marker_color=COLORS['green'], opacity=0.8, marker_line_width=0))
    fig5.add_trace(go.Bar(x=days, y=[80, 95, 88, 110, 92, 85, 100], name='Neutral',
        marker_color=COLORS['amber'], opacity=0.6, marker_line_width=0))
    fig5.add_trace(go.Bar(x=days, y=[55, 42, 38, 62, 44, 50, 36], name='Negative',
        marker_color=COLORS['red'], opacity=0.7, marker_line_width=0))
    fig5.update_layout(**PLOT_LAYOUT, height=250, barmode='stack',
        yaxis=dict(**PLOT_LAYOUT['yaxis'], title='Articles'))
    st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})

# ═══════════════════════════════════════════════════════════════════════
# PAGE: RISK MONITOR
# ═══════════════════════════════════════════════════════════════════════
elif page == "⬡ Risk Monitor":

    st.markdown("## Portfolio Risk Monitor")
    st.markdown("<div class='muted'>AI-enhanced VaR, dynamic covariance, and regime detection</div>", unsafe_allow_html=True)
    st.divider()

    r1, r2, r3, r4 = st.columns(4)
    with r1: st.metric("VaR 95% (Daily)", "−2.8%", "−0.3% vs prior month", delta_color="inverse")
    with r2: st.metric("VaR 99% (Daily)", "−4.4%", "+0.2% vs prior month", delta_color="inverse")
    with r3: st.metric("Regime Status", "Late Cycle", "Expansion phase")
    with r4: st.metric("Stress Probability", "38%", "+6% this week", delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-title'>⬡ VaR Trend (95% & 99%)</div>", unsafe_allow_html=True)
        fig_var = go.Figure()
        fig_var.add_trace(go.Bar(x=months, y=VAR_DATA['var95'], name='VaR 95%',
            marker_color=COLORS['red'], opacity=0.8, marker_line_width=0))
        fig_var.add_trace(go.Bar(x=months, y=VAR_DATA['var99'], name='VaR 99%',
            marker_color=COLORS['purple'], opacity=0.6, marker_line_width=0))
        fig_var.update_layout(**PLOT_LAYOUT, height=300, barmode='group',
            yaxis=dict(**PLOT_LAYOUT['yaxis'], ticksuffix='%', title='Daily VaR (%)'))
        st.plotly_chart(fig_var, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown("<div class='section-title'>◉ Implied Volatility Term Structure</div>", unsafe_allow_html=True)
        tenors = ['1W', '2W', '1M', '2M', '3M', '6M', '1Y']
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(x=tenors, y=[18.2, 19.4, 20.8, 21.3, 22.1, 23.4, 24.9],
            name='ATM IV', line=dict(color=COLORS['blue'], width=2.5),
            fill='tozeroy', fillcolor='rgba(56,189,248,0.07)', mode='lines+markers'))
        fig_vol.add_trace(go.Scatter(x=tenors, y=[22.1, 23.5, 25.2, 26.0, 27.1, 28.4, 29.8],
            name='25D Put Skew', line=dict(color=COLORS['red'], width=2),
            mode='lines+markers'))
        fig_vol.update_layout(**PLOT_LAYOUT, height=300,
            yaxis=dict(**PLOT_LAYOUT['yaxis'], ticksuffix='%', title='Implied Vol (%)'))
        st.plotly_chart(fig_vol, use_container_width=True, config={'displayModeBar': False})

    # Correlation heatmap
    st.markdown("<div class='section-title'>≋ Cross-Asset Correlation Matrix</div>", unsafe_allow_html=True)
    assets = ['SPY', 'QQQ', 'TLT', 'GLD', 'DXY', 'VIX']
    corr_data = np.array([
        [1.00,  0.95, -0.62,  0.18, -0.34, -0.78],
        [0.95,  1.00, -0.58,  0.15, -0.31, -0.82],
        [-0.62,-0.58,  1.00,  0.42,  0.28,  0.55],
        [0.18,  0.15,  0.42,  1.00, -0.44,  0.12],
        [-0.34,-0.31,  0.28, -0.44,  1.00,  0.22],
        [-0.78,-0.82,  0.55,  0.12,  0.22,  1.00],
    ])
    fig_corr = go.Figure(go.Heatmap(
        z=corr_data, x=assets, y=assets,
        colorscale=[[0, '#EF4444'], [0.5, '#111E35'], [1, '#10B981']],
        zmid=0, zmin=-1, zmax=1,
        text=[[f'{v:.2f}' for v in row] for row in corr_data],
        texttemplate='%{text}', textfont=dict(size=11, color='white'),
    ))
    fig_corr.update_layout(
        paper_bgcolor='#111E35', plot_bgcolor='#111E35',
        font=dict(color='#8BA3C7', size=11),
        margin=dict(l=40, r=20, t=20, b=40), height=320,
    )
    st.plotly_chart(fig_corr, use_container_width=True, config={'displayModeBar': False})

# ═══════════════════════════════════════════════════════════════════════
# PAGE: EARNINGS INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════
elif page == "📋 Earnings Intel":

    st.markdown("## Earnings Intelligence")
    st.markdown("<div class='muted'>NLP-scored earnings call analysis with AI-generated signals</div>", unsafe_allow_html=True)
    st.divider()

    # ── WORKING TABS ──────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📅 Recent Calls", "🔮 Upcoming Earnings", "⚠️ Anomaly Alerts"])

    with tab1:
        st.markdown("##### Q4 2025 / Q1 2026 Earnings — NLP Sentiment Analysis")

        # Color-code sentiment column
        def style_sentiment(val):
            if val == 'Bullish':  return 'color: #10B981; font-weight: 600'
            if val == 'Bearish':  return 'color: #EF4444; font-weight: 600'
            return 'color: #F59E0B; font-weight: 600'

        def style_move(val):
            return f"color: {'#10B981' if val.startswith('+') else '#EF4444'}; font-family: monospace; font-weight: 600"

        def style_score(val):
            return f"color: {'#10B981' if val.startswith('+') else '#EF4444'}; font-family: monospace"

        styled = RECENT_EARNINGS.style\
            .applymap(style_sentiment, subset=['Sentiment'])\
            .applymap(style_move, subset=['Post-Earnings Move'])\
            .applymap(style_score, subset=['NLP Score'])\
            .set_properties(**{'background-color': '#111E35', 'color': '#8BA3C7',
                               'border-color': 'rgba(255,255,255,0.07)'})\
            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#0C1830'), ('color', '#8BA3C7'),
                                              ('font-size', '11px'), ('text-transform', 'uppercase'),
                                              ('letter-spacing', '0.5px'), ('padding', '10px 14px')]},
                {'selector': 'td', 'props': [('padding', '10px 14px'), ('font-size', '13px')]},
            ])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### Post-Earnings Price Reaction")
        moves = [float(v.replace('%', '')) for v in RECENT_EARNINGS['Post-Earnings Move']]
        fig_earn = go.Figure(go.Bar(
            x=RECENT_EARNINGS['Ticker'], y=moves,
            marker_color=[COLORS['green'] if v >= 0 else COLORS['red'] for v in moves],
            text=[f"{v:+.1f}%" for v in moves], textposition='outside',
            textfont=dict(size=11, color='#8BA3C7'), marker_line_width=0, opacity=0.85
        ))
        fig_earn.update_layout(**PLOT_LAYOUT, height=260,
            yaxis=dict(**PLOT_LAYOUT['yaxis'], ticksuffix='%', zeroline=True,
                       zerolinecolor='rgba(255,255,255,0.15)'))
        st.plotly_chart(fig_earn, use_container_width=True, config={'displayModeBar': False})

    with tab2:
        st.markdown("##### Upcoming Earnings — AI Outlook & Key Watchpoints")

        def style_outlook(val):
            if val == 'Bullish': return 'color: #10B981; font-weight: 600'
            if val == 'Bearish': return 'color: #EF4444; font-weight: 600'
            return 'color: #F59E0B; font-weight: 600'

        styled2 = UPCOMING_EARNINGS.style\
            .applymap(style_outlook, subset=['AI Outlook'])\
            .set_properties(**{'background-color': '#111E35', 'color': '#8BA3C7',
                               'border-color': 'rgba(255,255,255,0.07)'})\
            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#0C1830'), ('color', '#8BA3C7'),
                                              ('font-size', '11px'), ('text-transform', 'uppercase'),
                                              ('letter-spacing', '0.5px'), ('padding', '10px 14px')]},
                {'selector': 'td', 'props': [('padding', '10px 14px'), ('font-size', '13px')]},
            ])
        st.dataframe(styled2, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("##### AI-Detected NLP Anomalies — Earnings Call Signals")

        sev_map = {'High': '🔴 High', 'Medium': '🟡 Medium', 'Low': '🟢 Low'}
        ANOMALIES_DISPLAY = ANOMALIES.copy()
        ANOMALIES_DISPLAY['Severity'] = ANOMALIES_DISPLAY['Severity'].map(sev_map)

        def style_sev(val):
            if '🔴' in str(val): return 'color: #EF4444; font-weight: 600'
            if '🟡' in str(val): return 'color: #F59E0B; font-weight: 600'
            return 'color: #10B981; font-weight: 600'

        styled3 = ANOMALIES_DISPLAY.style\
            .applymap(style_sev, subset=['Severity'])\
            .set_properties(**{'background-color': '#111E35', 'color': '#8BA3C7',
                               'border-color': 'rgba(255,255,255,0.07)'})\
            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#0C1830'), ('color', '#8BA3C7'),
                                              ('font-size', '11px'), ('text-transform', 'uppercase'),
                                              ('letter-spacing', '0.5px'), ('padding', '10px 14px')]},
                {'selector': 'td', 'props': [('padding', '10px 14px'), ('font-size', '13px')]},
            ])
        st.dataframe(styled3, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════
# PAGE: AI COPILOT
# ═══════════════════════════════════════════════════════════════════════
elif page == "🤖 AI Copilot":

    st.markdown("## AI Analyst Copilot")
    st.markdown("<div class='muted'>Ask anything about markets, sentiment, risk, or portfolio strategy</div>", unsafe_allow_html=True)
    st.divider()

    st.markdown("""
    <div class='ai-card'>
      <div style='display:flex;align-items:center;gap:12px;margin-bottom:4px'>
        <div style='width:36px;height:36px;border-radius:9px;background:linear-gradient(135deg,#8B5CF6,#38BDF8);display:flex;align-items:center;justify-content:center;font-size:18px'>✦</div>
        <div>
          <div style='font-size:14px;font-weight:600;color:#E8F0FE'>FinSentinel AI Analyst</div>
          <div style='font-size:11px;color:#8BA3C7'>FinBERT + LLM Integration — Evidence-Backed Institutional Insights</div>
        </div>
        <div style='margin-left:auto;padding:4px 12px;background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);border-radius:20px;font-size:11px;color:#10B981;font-weight:600'>● Active</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Suggested questions
    st.markdown("**Suggested Questions:**")
    sq_cols = st.columns(3)
    suggestions = [
        "What is driving tech sector sentiment?",
        "Analyze current portfolio risk levels",
        "What does the macro regime signal?",
        "Summarize this week's earnings anomalies",
        "Should I reduce equity exposure now?",
        "What is the NLP sentiment on Fed policy?",
    ]
    for i, sug in enumerate(suggestions):
        with sq_cols[i % 3]:
            if st.button(sug, key=f"sug_{i}"):
                st.session_state['ai_query'] = sug

    st.markdown("<br>", unsafe_allow_html=True)

    # Query input
    query = st.text_input(
        "Your Question",
        value=st.session_state.get('ai_query', ''),
        placeholder="e.g. What is driving tech sector sentiment this week?",
        label_visibility="collapsed",
        key="ai_input"
    )

    col_btn, col_conf = st.columns([1, 4])
    with col_btn:
        analyze = st.button("✦ Analyze →", type="primary")
    with col_conf:
        st.markdown("<div style='padding-top:8px;font-size:11px;color:#8BA3C7'>Model: FinBERT + Claude  •  Confidence: 87.4%  •  Sources: 4,200+ articles</div>", unsafe_allow_html=True)

    if analyze and query:
        with st.spinner("✦ Analyzing with FinBERT + AI..."):
            time.sleep(1.2)
        idx = hash(query) % len(AI_RESPONSES)
        st.markdown(f"""
        <div class='ai-response'>
          <strong style='color:#8B5CF6'>✦ AI Analyst Response:</strong><br><br>
          {AI_RESPONSES[idx]}
        </div>
        """, unsafe_allow_html=True)
        st.session_state.pop('ai_query', None)

    st.divider()
    st.markdown("**AI Insight Library — Pre-Generated Analysis**")
    for i, resp in enumerate(AI_RESPONSES):
        titles = ["Tech Sector Sentiment Driver", "Cross-Asset Risk Assessment",
                  "Macro Regime Classification", "Earnings Season NLP Summary", "Sentiment Factor Positioning"]
        with st.expander(f"✦ {titles[i]}"):
            st.markdown(f"<div style='color:#8BA3C7;font-size:13px;line-height:1.7'>{resp}</div>",
                        unsafe_allow_html=True)
