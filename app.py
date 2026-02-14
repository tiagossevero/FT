"""
FOODTEST - Dashboard Completo de Analytics v3.0
Plataforma de Analise Sensorial, Gestao e Inteligencia de Dados
Inclui: Analise Estatistica Avancada, EDA, Performance de Produtos, Engajamento e Gamificacao
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.templates.default = "plotly_white"
import json, os, glob, csv
from datetime import datetime, timedelta
from io import StringIO
import warnings
warnings.filterwarnings('ignore')
from sqlalchemy import create_engine, text
try:
    from scipy import stats as scipy_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
from plotly.subplots import make_subplots

# Force light theme programmatically (equivalent to config.toml but in app.py)
try:
    st._config.set_option('theme.base', 'light')
    st._config.set_option('theme.backgroundColor', '#F5F7FA')
    st._config.set_option('theme.secondaryBackgroundColor', '#FFFFFF')
    st._config.set_option('theme.textColor', '#202124')
    st._config.set_option('theme.primaryColor', '#0052CC')
except: pass

# ============================================================================
# CONFIG
# ============================================================================
CL = {
    'primary':'#0052CC','secondary':'#00B4D8','accent1':'#0052CC','accent2':'#00B4D8',
    'success':'#31A24C','warning':'#FF9500','danger':'#EE5A52','purple':'#7B61FF',
    'dark':'#202124','orange':'#FF9500','teal':'#00B4D8','pink':'#E8457C',
}
PAL = ['#0052CC','#00B4D8','#31A24C','#FF9500','#7B61FF','#E8457C','#0097A7','#5C6BC0','#EE5A52','#43A047','#8D6E63','#78909C','#F06292','#4DB6AC','#FFB74D']
CARD_COLORS = ['#0052CC','#00B4D8','#31A24C','#FF9500','#7B61FF','#0097A7','#E8457C','#5C6BC0','#EE5A52','#43A047']
st.set_page_config(page_title="Foodtest Analytics", page_icon="", layout="wide", initial_sidebar_state="expanded")

# ============================================================================
# LOADING SCREEN - Usa st.empty() para controlar ciclo de vida (JS nao executa em st.markdown)
# ============================================================================
LOADING_SCREEN_HTML = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
.loading-container {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 9999;
}
.loading-logo { font-size: 4rem; margin-bottom: 20px; animation: pulse 2s infinite; }
.loading-text { color: white; font-family: 'Inter', sans-serif; font-size: 1.5rem; font-weight: 600; margin-bottom: 30px; }
.loading-spinner {
    width: 50px; height: 50px; border: 4px solid rgba(255,255,255,0.3);
    border-top: 4px solid white; border-radius: 50%; animation: spin 1s linear infinite;
}
.loading-progress { width: 200px; height: 4px; background: rgba(255,255,255,0.3); border-radius: 2px; margin-top: 20px; overflow: hidden; }
.loading-progress-bar { width: 30%; height: 100%; background: white; border-radius: 2px; animation: loading 2s ease-in-out infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
@keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
@keyframes loading { 0% { transform: translateX(-100%); } 50% { transform: translateX(250%); } 100% { transform: translateX(-100%); } }
</style>
<div class="loading-container">
    <div class="loading-logo">🍽️</div>
    <div class="loading-text">Foodtest Analytics</div>
    <div class="loading-spinner"></div>
    <div class="loading-progress"><div class="loading-progress-bar"></div></div>
</div>
"""

# Skeleton loading cards
def skeleton_card():
    """Card com efeito shimmer enquanto carrega"""
    return """
    <style>
    .skeleton {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 8px;
    }
    @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
    .skeleton-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 16px; }
    .skeleton-title { height: 24px; width: 60%; margin-bottom: 12px; }
    .skeleton-text { height: 16px; width: 100%; margin-bottom: 8px; }
    .skeleton-text.short { width: 40%; }
    .skeleton-chart { height: 200px; width: 100%; margin-top: 16px; }
    </style>
    <div class="skeleton-card">
        <div class="skeleton skeleton-title"></div>
        <div class="skeleton skeleton-text"></div>
        <div class="skeleton skeleton-text"></div>
        <div class="skeleton skeleton-text short"></div>
        <div class="skeleton skeleton-chart"></div>
    </div>
    """

def show_skeleton_grid(cols=4):
    """Mostra grid de skeletons enquanto dados carregam"""
    columns = st.columns(cols)
    for col in columns:
        with col:
            st.markdown(skeleton_card(), unsafe_allow_html=True)

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
:root,html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"]{
--primary:#0052CC;--primary-light:#E6EFFA;--primary-dark:#003D99;
--secondary:#00B4D8;--secondary-light:#E0F7FA;
--success:#31A24C;--success-light:#E8F5E9;
--warning:#FF9500;--warning-light:#FFF3E0;
--danger:#EE5A52;--danger-light:#FEECEB;
--bg:#F5F7FA;--card:#FFFFFF;
--border:#E8EAED;--border-light:#F0F2F5;
--text-primary:#202124;--text-secondary:#5E6368;--text-muted:#9AA0A6;
--font-heading:'Poppins',sans-serif;--font-body:'Inter',sans-serif;--font-mono:'JetBrains Mono',monospace;
--sp-1:4px;--sp-2:8px;--sp-3:12px;--sp-4:16px;--sp-5:20px;--sp-6:24px;--sp-7:32px;--sp-8:40px;
--radius-sm:6px;--radius-md:8px;--radius-lg:12px;--radius-xl:16px;
--shadow-sm:0 1px 2px rgba(0,0,0,0.06);--shadow-md:0 2px 8px rgba(0,0,0,0.08);--shadow-lg:0 4px 16px rgba(0,0,0,0.12);
color-scheme:light!important;
}
/* === BASE === */
html,body,.main,.stApp,
[data-testid="stAppViewContainer"],[data-testid="stHeader"],[data-testid="stToolbar"],
[data-testid="stBottomBlockContainer"],[data-testid="stMainBlockContainer"],
.block-container,[data-testid="stVerticalBlock"],[data-testid="stHorizontalBlock"]{
background:var(--bg)!important;background-color:var(--bg)!important;color:var(--text-primary)!important}
.stApp{font-family:var(--font-body)!important;font-size:14px}
h1,h2,h3,h4{font-family:var(--font-heading)!important;font-weight:700!important;color:var(--text-primary)!important}
p,span,label,li,td,th{color:var(--text-primary)!important}
.block-container{padding:var(--sp-6) var(--sp-7) var(--sp-8)!important;max-width:1440px}
/* === SIDEBAR === */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"]>div,
section[data-testid="stSidebar"]>div>div,
section[data-testid="stSidebar"]>div>div>div{background:var(--card)!important;background-color:var(--card)!important}
section[data-testid="stSidebar"]{border-right:1px solid var(--border)!important;width:260px!important;min-width:260px!important}
section[data-testid="stSidebar"] *{color:var(--text-primary)!important}
section[data-testid="stSidebar"] .stRadio>div{gap:2px!important}
section[data-testid="stSidebar"] .stRadio label{padding:8px 12px 8px 16px;border-radius:var(--radius-md);transition:all .2s ease;font-size:.82rem!important;font-family:var(--font-body)!important;font-weight:500;letter-spacing:0}
section[data-testid="stSidebar"] .stRadio label:hover{background:var(--primary-light);color:var(--primary)!important}
section[data-testid="stSidebar"] .stRadio label[data-checked="true"]{background:var(--primary-light);color:var(--primary)!important;font-weight:600;border-left:3px solid var(--primary)}
section[data-testid="stSidebar"] .stTextInput input{background:var(--bg)!important;border:1px solid var(--border)!important;color:var(--text-primary)!important;border-radius:var(--radius-md)!important;font-family:var(--font-body)!important}
section[data-testid="stSidebar"] .stButton button{background:var(--primary)!important;color:#fff!important;border:none!important;border-radius:var(--radius-md)!important;font-family:var(--font-body)!important;font-weight:600;letter-spacing:.3px;padding:8px 16px;transition:all .2s}
section[data-testid="stSidebar"] .stButton button:hover{background:var(--primary-dark)!important;box-shadow:var(--shadow-md)}
.nav-section{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;color:var(--text-muted)!important;padding:16px 16px 6px;margin-top:8px}
.nav-section:first-of-type{margin-top:0}
/* === METRIC CARDS === */
.mc{background:var(--card);border-radius:var(--radius-lg);padding:var(--sp-5) var(--sp-6);box-shadow:var(--shadow-sm);transition:all .2s ease;border:1px solid var(--border);position:relative;overflow:hidden}
.mc:hover{box-shadow:var(--shadow-md);transform:translateY(-1px)}
.mc-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:8px;flex-shrink:0}
.mc-header{display:flex;align-items:center;margin-bottom:var(--sp-2)}
.mc-label{font-size:.7rem;color:var(--text-secondary)!important;text-transform:uppercase;letter-spacing:.8px;font-weight:600;font-family:var(--font-body)}
.mc-value{font-family:var(--font-mono);font-size:1.65rem;font-weight:600;color:var(--text-primary)!important;margin:0;line-height:1.2}
.mc-delta{font-size:.72rem;padding:2px 8px;border-radius:var(--radius-sm);display:inline-block;margin-top:var(--sp-2);font-weight:600;font-family:var(--font-mono)}
.delta-pos{background:var(--success-light);color:var(--success)!important}
.delta-neg{background:var(--danger-light);color:var(--danger)!important}
/* === SECTION HEADERS === */
.sh{color:var(--text-primary)!important;font-size:1.25rem;font-weight:700;margin:0;font-family:var(--font-heading);background:none!important;-webkit-text-fill-color:var(--text-primary)!important;line-height:1.3}
.sh-sub{color:var(--text-secondary)!important;font-size:.85rem;font-weight:400;margin-top:4px;margin-bottom:0;font-family:var(--font-body)}
.page-header{margin-bottom:var(--sp-6);padding-bottom:var(--sp-5);border-bottom:1px solid var(--border)}
.page-header h2{margin-bottom:2px!important}
/* === BREADCRUMB === */
.breadcrumb{font-size:.75rem;color:var(--text-muted)!important;margin-bottom:var(--sp-4);font-family:var(--font-body);font-weight:500}
.breadcrumb .bc-sep{margin:0 6px;color:var(--text-muted)!important}
.breadcrumb .bc-current{color:var(--text-primary)!important;font-weight:600}
/* === HEADER BAR === */
.header-bar{display:flex;justify-content:space-between;align-items:center;padding:var(--sp-3) 0;margin-bottom:var(--sp-4)}
.header-status{display:flex;align-items:center;gap:var(--sp-4);font-size:.75rem;color:var(--text-secondary)!important;font-family:var(--font-body)}
.status-dot{width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:4px}
.status-online{background:var(--success)}
.status-sync{background:var(--warning)}
/* === CHART CARDS === */
.chart-card{background:var(--card)!important;border-radius:var(--radius-lg);padding:var(--sp-5) var(--sp-6);box-shadow:var(--shadow-sm);margin-bottom:var(--sp-4);border:1px solid var(--border)}
.chart-title{font-size:.9rem;font-weight:600;color:var(--text-primary)!important;margin-bottom:var(--sp-3);font-family:var(--font-heading)}
.chart-subtitle{font-size:.75rem;color:var(--text-secondary)!important;margin-top:-8px;margin-bottom:var(--sp-3);font-family:var(--font-body)}
/* === INSIGHT BOXES === */
.ib{background:var(--card)!important;border-radius:var(--radius-lg);padding:var(--sp-5) var(--sp-6);color:var(--text-primary)!important;margin:var(--sp-3) 0;border:1px solid var(--border);box-shadow:var(--shadow-sm);transition:all .2s}
.ib:hover{box-shadow:var(--shadow-md)}
.ib h4{color:var(--text-primary)!important;margin-bottom:var(--sp-2);font-size:.88rem;font-weight:600;font-family:var(--font-heading)}
.ib p{color:var(--text-secondary)!important;font-size:.82rem;line-height:1.65;font-family:var(--font-body);margin:0}
.it{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:var(--radius-sm);font-size:.62rem;font-weight:700;text-transform:uppercase;margin-bottom:var(--sp-2);letter-spacing:.6px;font-family:var(--font-body)}
.it-icon{font-size:.7rem;line-height:1}
.ts{background:rgba(123,97,255,.1);color:#7B61FF!important;border-left:3px solid #7B61FF}
.tt{background:rgba(0,82,204,.08);color:#0052CC!important;border-left:3px solid #0052CC}
.to{background:rgba(49,162,76,.08);color:#31A24C!important;border-left:3px solid #31A24C}
/* === FORMS & INPUTS === */
.stSelectbox div[data-baseweb="select"]>div,
.stMultiSelect div[data-baseweb="select"]>div{background:var(--card)!important;color:var(--text-primary)!important;border-color:var(--border)!important;border-radius:var(--radius-md)!important;font-family:var(--font-body)!important}
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input{background:var(--card)!important;color:var(--text-primary)!important;border-color:var(--border)!important;border-radius:var(--radius-md)!important;font-family:var(--font-body)!important}
[data-testid="stExpander"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--radius-md)!important}
[data-testid="stExpander"] summary span{color:var(--text-primary)!important;font-family:var(--font-body)!important;white-space:normal!important;overflow:visible!important;text-overflow:unset!important}
/* === DATA ELEMENTS === */
[data-testid="stDataFrame"],[data-testid="stDataFrame"]>div,[data-testid="stDataFrame"] iframe,
[data-testid="stDataFrameResizable"],[data-testid="stDataFrame"] [class*="glide"]{background:var(--card)!important;background-color:var(--card)!important}
[data-testid="stMetric"]{background:var(--card)!important;border-radius:var(--radius-md);border:1px solid var(--border);padding:var(--sp-4)!important}
[data-testid="stMetricValue"]{color:var(--text-primary)!important;font-family:var(--font-mono)!important}
[data-testid="stMetricLabel"]{color:var(--text-secondary)!important;font-family:var(--font-body)!important}
[data-testid="stMarkdownContainer"]{color:var(--text-primary)!important}
[data-testid="stMarkdownContainer"] p{color:var(--text-primary)!important}
/* === DROPDOWNS / MENUS === */
div[data-baseweb="popover"] ul{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--radius-md)!important}
div[data-baseweb="menu"] li{color:var(--text-primary)!important;font-family:var(--font-body)!important}
div[data-baseweb="menu"] li:hover{background:var(--primary-light)!important}
[data-baseweb="select"] [data-baseweb="tag"]{background:var(--primary-light)!important;color:var(--primary)!important;border-radius:var(--radius-sm)!important}
[data-baseweb="input"]{background:var(--card)!important;color:var(--text-primary)!important}
[data-baseweb="base-input"]{background:var(--card)!important}
.stAlert{background:var(--bg)!important;color:var(--text-primary)!important;border-radius:var(--radius-md)!important}
/* === TABLES === */
.stDataFrame table{background:var(--card)!important;color:var(--text-primary)!important}
.stDataFrame th{background:var(--bg)!important;color:var(--text-primary)!important;font-family:var(--font-body)!important;font-weight:600;font-size:.8rem}
.stDataFrame td{background:var(--card)!important;color:var(--text-primary)!important;font-family:var(--font-body)!important;font-size:.82rem}
/* === TABS === */
#MainMenu{visibility:hidden}footer{visibility:hidden}
.stTabs [data-baseweb="tab-list"]{gap:0;border-bottom:2px solid var(--border);padding:0}
.stTabs [data-baseweb="tab"]{background:transparent;border-radius:0;padding:10px 20px;border:none;font-weight:500;color:var(--text-secondary);font-family:var(--font-body);font-size:.85rem;transition:all .2s}
.stTabs [data-baseweb="tab"]:hover{color:var(--primary);background:var(--primary-light)}
.stTabs [aria-selected="true"]{background:transparent!important;color:var(--primary)!important;border-bottom:2px solid var(--primary)!important;font-weight:600}
/* === DIVIDERS & UTILITIES === */
.divider{height:1px;background:var(--border);margin:var(--sp-6) 0}
/* === RESPONSIVE === */
@media(max-width:768px){
.mc-value{font-size:1.3rem}
.mc{padding:var(--sp-4)}
.block-container{padding:var(--sp-4) var(--sp-4) var(--sp-6)!important}
section[data-testid="stSidebar"]{width:220px!important;min-width:220px!important}
}
/* ===== ESCONDE ELEMENTOS PADRAO DO STREAMLIT (Visual Limpo) ===== */
header[data-testid="stHeader"]{display:none!important}
[data-testid="stToolbar"]{display:none!important}
[data-testid="stDecoration"]{display:none!important}
[data-testid="stStatusWidget"]{display:none!important}
[data-testid="stAppViewContainer"]{padding-top:0!important}
.block-container{padding-top:1rem!important}
section[data-testid="stSidebar"]>div:first-child{padding-top:1rem!important}
</style>""", unsafe_allow_html=True)

# ============================================================================
# UI COMPONENTS
# ============================================================================
def mcard(v, l, d=None, dt='positive', c=None):
    bc = c if c else CL['primary']
    dh = ""
    if d:
        arrow = "+" if dt == "positive" else "-"
        dcls = "delta-pos" if dt == "positive" else "delta-neg"
        dh = f'<span class="mc-delta {dcls}">{arrow} {d}</span>'
    return f'<div class="mc"><div class="mc-header"><span class="mc-dot" style="background:{bc}"></span><span class="mc-label">{l}</span></div><div class="mc-value">{v}</div>{dh}</div>'

def gauge(v, t, mx=100):
    fig = go.Figure(go.Indicator(mode="gauge+number",value=v,title={'text':t,'font':{'size':13,'family':'Poppins','color':'#202124'}},
        number={'font':{'family':'JetBrains Mono','size':32,'color':'#202124'}},
        gauge={'axis':{'range':[0,mx],'tickfont':{'size':10,'color':'#5E6368'}},'bar':{'color':'#0052CC'},
        'steps':[{'range':[0,40],'color':'#FEECEB'},{'range':[40,60],'color':'#FFF3E0'},{'range':[60,80],'color':'#E8F5E9'},{'range':[80,100],'color':'#C8E6C9'}],
        'threshold':{'line':{'color':'#EE5A52','width':3},'thickness':.75,'value':60}}))
    fig.update_layout(height=220,margin=dict(l=20,r=20,t=40,b=20),paper_bgcolor='#FFFFFF',font_family='Inter',font_color='#202124')
    return fig

def ibox(tag, title, text):
    tc = {'Estratégico':'ts','Tático':'tt','Operacional':'to',
          'Estrategico':'ts'}.get(tag,'tt')
    icon_map = {'Estratégico':'&#9670;','Tático':'&#9654;','Operacional':'&#9679;',
                'Estrategico':'&#9670;'}
    icon = icon_map.get(tag,'&#9654;')
    return f'<div class="ib"><span class="it {tc}"><span class="it-icon">{icon}</span> {tag}</span><h4>{title}</h4><p>{text}</p></div>'

def spct(p, t): return round(p/t*100,1) if t>0 else 0

def hbar(xv, yv, cs='Blues', **kw):
    df=pd.DataFrame({'v':list(xv),'n':list(yv)})
    return px.bar(df,x='v',y='n',orientation='h',color='v',color_continuous_scale=cs,**kw)

def chart_layout(fig, h=400):
    fig.update_layout(height=h,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',
        font_family='Inter',font_color='#202124',margin=dict(l=10,r=10,t=40,b=10),
        xaxis=dict(gridcolor='#F0F2F5',zerolinecolor='#E8EAED',title_font=dict(size=12,color='#5E6368'),tickfont=dict(size=11,color='#5E6368')),
        yaxis=dict(gridcolor='#F0F2F5',zerolinecolor='#E8EAED',title_font=dict(size=12,color='#5E6368'),tickfont=dict(size=11,color='#5E6368')),
        title_font=dict(family='Poppins',size=14,color='#202124'))
    return fig

def add_labels(fig):
    bar_total=0
    for t in fig.data:
        if getattr(t,'type','')=='bar':
            vals=t.x if getattr(t,'orientation',None)=='h' else t.y
            if vals is not None:
                try: bar_total+=sum(float(v) for v in vals if v is not None)
                except: pass
    for t in fig.data:
        tp=getattr(t,'type','')
        if tp=='pie':
            t.update(textinfo='value+percent',textposition='inside',textfont_size=11)
        elif tp=='bar' and bar_total>0:
            vals=t.x if getattr(t,'orientation',None)=='h' else t.y
            if vals is not None:
                try:
                    nums=[float(v) if v is not None else 0 for v in vals]
                    def _fmt(v):
                        s=f"{int(v):,}" if v==int(v) else f"{v:,.1f}"
                        return f"{s} ({v/bar_total*100:.1f}%)"
                    t.update(text=[_fmt(v) for v in nums],textposition='auto',textfont_size=10)
                except: pass
        elif tp=='treemap':
            t.update(texttemplate='%{label}<br>%{value:,} (%{percentRoot:.1%})')
    return fig

_st_plotly=st.plotly_chart
def _plotly_white(fig,**kw):
    try:
        fig.update_layout(paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',
            font=dict(color='#202124',family='Inter',size=12),
            legend=dict(font=dict(color='#202124',size=11,family='Inter'),bgcolor='rgba(0,0,0,0)'),
            hoverlabel=dict(bgcolor='#202124',font_size=12,font_family='Inter'))
        add_labels(fig)
    except: pass
    return _st_plotly(fig,**kw)
st.plotly_chart=_plotly_white

def section_header(title, subtitle=None):
    h = f'<div class="page-header"><div class="breadcrumb">Foodtest<span class="bc-sep">/</span><span class="bc-current">{title}</span></div><h2 class="sh">{title}</h2>'
    if subtitle: h += f'<p class="sh-sub">{subtitle}</p>'
    h += '</div>'
    return h

def header_bar():
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    return f'<div class="header-bar"><div></div><div class="header-status"><span><span class="status-dot status-online"></span> Conectado</span><span>Atualizado: {now}</span></div></div>'

# ============================================================================
# CONEXÃO POSTGRESQL DIGITALOCEAN
# ============================================================================
@st.cache_resource(show_spinner=False)
def get_db_engine():
    """Cria conexão com PostgreSQL da DigitalOcean"""
    DB_CONFIG = {
        'host': 'postgres-vermelho-do-user-1297912-0.c.db.ondigitalocean.com',
        'port': 25060,
        'database': 'foodtest_production',
        'user': 'foodtest_view',
        'password': 'k9JuoWaWt8',
        'sslmode': 'require'
    }
    connection_string = (
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        f"?sslmode={DB_CONFIG['sslmode']}"
    )
    return create_engine(connection_string, pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=1800)

def query_db(sql: str) -> pd.DataFrame:
    """Executa query e retorna DataFrame"""
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            return pd.read_sql(text(sql), conn)
    except Exception as e:
        st.error(f"Erro na consulta: {e}")
        return pd.DataFrame()

# ============================================================================
# LAZY LOADING & AGGREGATION QUERIES
# ============================================================================

@st.cache_data(ttl=86400, show_spinner=False)
def load_table_lazy(table_name: str) -> pd.DataFrame:
    """Carrega tabela individual apenas quando solicitada"""
    return query_db(f"SELECT * FROM {table_name}")

@st.cache_data(ttl=86400, show_spinner=False)
def get_count(table: str) -> int:
    """Conta registros - super rapido com cache"""
    result = query_db(f"SELECT COUNT(*) as cnt FROM foodtest.{table}")
    return int(result['cnt'].iloc[0]) if not result.empty else 0

@st.cache_data(ttl=3600, show_spinner=False)
def get_aggregations():
    """Metricas agregadas para o dashboard - query unica otimizada"""
    return query_db("""
        SELECT
            (SELECT COUNT(*) FROM foodtest.produto) as total_produtos,
            (SELECT COUNT(*) FROM foodtest.usuario) as total_usuarios,
            (SELECT COUNT(*) FROM foodtest.sessao_pesquisa) as total_sessoes,
            (SELECT COUNT(*) FROM foodtest.campanha) as total_campanhas,
            (SELECT COUNT(*) FROM foodtest.empresa) as total_empresas,
            (SELECT COUNT(*) FROM foodtest.categoria_produto) as total_categorias,
            (SELECT COUNT(*) FROM foodtest.subcategoria_produto) as total_subcategorias,
            (SELECT COUNT(*) FROM foodtest.resposta_questionario_usuario) as total_questionarios,
            (SELECT COUNT(*) FROM foodtest.resposta_pergunta_pesquisa) as total_respostas,
            (SELECT COUNT(*) FROM foodtest.beneficio) as total_beneficios
    """)

# ============================================================================
# DATA LOADER (TODAS AS TABELAS)
# ============================================================================

def pj(v):
    if pd.isna(v) or v in('','""','nan','None'): return {}
    try:
        if isinstance(v,str): v=v.strip('"')
        return json.loads(v)
    except: return {}

# Mapeamento de tabelas do banco (schema foodtest)
TABLE_MAPPING = {
    'categoria': 'foodtest.categoria_produto',
    'subcategoria': 'foodtest.subcategoria_produto',
    'produto': 'foodtest.produto',
    'marca': 'foodtest.marca',
    'parceiro': 'foodtest.parceiro',
    'produto_parceiro': 'foodtest.produto_parceiro',
    'banner_home': 'foodtest.banner_home',
    'prod_recomendado': 'foodtest.pesquisa_produto_recomendado',
    'campanha': 'foodtest.campanha',
    'pesq_produto': 'foodtest.pesquisa_produto',
    'pesq_subcategoria': 'foodtest.pesquisa_subcategoria',
    'sessao': 'foodtest.sessao_pesquisa',
    'pergunta': 'foodtest.pergunta_pesquisa',
    'resp_pergunta': 'foodtest.resposta_pergunta_pesquisa',
    'resp_questionario': 'foodtest.resposta_questionario_usuario',
    'comentarios': 'foodtest.comentarios',
    'beneficio': 'foodtest.beneficio',
    'resgate': 'foodtest.resgate_beneficio',
    'pontos': 'foodtest.pontos_usuario',
    'empresa': 'foodtest.empresa',
    'usr_empresa': 'foodtest.usuario_empresa',
    'grupo_empresa': 'foodtest.grupo_usuario_empresa',
    'usuario': 'foodtest.usuario',
    'estado': 'foodtest.estado',
    'cidade': 'foodtest.cidade',
    'prod_nao_cadastrado': 'foodtest.produto_nao_cadastrado',
    'notificacoes': 'foodtest.notificacoes',
}

@st.cache_data(ttl=86400, show_spinner=False)
def load_all(dr=None):
    """Carrega todas as tabelas do PostgreSQL"""
    return {k: query_db(f"SELECT * FROM {table}") for k, table in TABLE_MAPPING.items()}

def enrich(raw):
    d = {k: v.copy() if len(v)>0 else pd.DataFrame() for k, v in raw.items()}
    if len(d['usuario'])>0 and 'nome' in d['usuario'].columns:
            d['usuario']=d['usuario'][~d['usuario']['nome'].str.lower().str.contains('teste|test account',na=False)]
    def mkd(df,k='id',v='nome'):
        return df.set_index(k)[v].to_dict() if len(df)>0 and k in df.columns and v in df.columns else {}
    di = {
        'categoria':mkd(d['categoria']),'subcategoria':mkd(d['subcategoria']),
        'produto':mkd(d['produto']),'usuario':mkd(d['usuario']),
        'pergunta':mkd(d['pergunta'],v='titulo'),'marca':mkd(d['marca']),
        'empresa':mkd(d['empresa'],v='nome_fantasia'),'beneficio':mkd(d['beneficio']),
        'cidade':mkd(d['cidade']),'estado':mkd(d['estado']),'parceiro':mkd(d['parceiro']),
    }
    dsc = d['subcategoria'].set_index('id')['id_categoria_produto'].to_dict() if len(d['subcategoria'])>0 and 'id_categoria_produto' in d['subcategoria'].columns else {}
    # pesquisa_subcategoria -> real subcategoria/categoria
    ps=d['pesq_subcategoria']
    dps_sc = ps.set_index('id')['id_subcategoria_produto'].to_dict() if len(ps)>0 and 'id_subcategoria_produto' in ps.columns else {}
    dps_cat = ps.set_index('id')['id_categoria_produto'].to_dict() if len(ps)>0 and 'id_categoria_produto' in ps.columns else {}
    # produto -> subcategoria/categoria
    dpr_sc = d['produto'].set_index('id')['id_subcategoria_produto'].to_dict() if len(d['produto'])>0 and 'id_subcategoria_produto' in d['produto'].columns else {}
    dpr_cat = d['produto'].set_index('id')['id_categoria_produto'].to_dict() if len(d['produto'])>0 and 'id_categoria_produto' in d['produto'].columns else {}
    idv = set(d['usuario']['id'].tolist()) if len(d['usuario'])>0 and 'id' in d['usuario'].columns else set()
    # resp_questionario
    rq=d['resp_questionario']
    if len(rq)>0:
        if 'id_usuario' in rq.columns and idv: rq=rq[rq['id_usuario'].isin(idv)]
        for c,dk in [('id_usuario','usuario'),('id_produto','produto')]:
            if c in rq.columns: rq[f'nome_{dk}']=rq[c].map(di.get(dk,{}))
        # Map subcategoria/categoria via pesquisa_subcategoria table first
        if 'id_pesquisa_subcategoria' in rq.columns:
            rq['id_subcategoria_real']=rq['id_pesquisa_subcategoria'].map(dps_sc)
            rq['id_categoria']=rq['id_pesquisa_subcategoria'].map(dps_cat)
        else:
            rq['id_subcategoria_real']=np.nan; rq['id_categoria']=np.nan
        # Fill missing from produto for product-based questionnaires
        if 'id_produto' in rq.columns:
            mask=rq['id_subcategoria_real'].isna()
            rq.loc[mask,'id_subcategoria_real']=rq.loc[mask,'id_produto'].map(dpr_sc)
            rq.loc[mask,'id_categoria']=rq.loc[mask,'id_produto'].map(dpr_cat)
        rq['nome_subcategoria']=rq['id_subcategoria_real'].map(di.get('subcategoria',{}))
        rq['nome_categoria']=rq['id_categoria'].map(di['categoria'])
        if 'pontos_ganhos' in rq.columns: rq['pontos_ganhos']=pd.to_numeric(rq['pontos_ganhos'],errors='coerce').fillna(0)
        if 'createdAt' in rq.columns:
            rq['createdAt']=pd.to_datetime(rq['createdAt'],errors='coerce')
            rq['data']=rq['createdAt'].dt.date; rq['hora']=rq['createdAt'].dt.hour; rq['dia_semana']=rq['createdAt'].dt.day_name()
    d['resp_questionario']=rq
    # resp_pergunta
    rp=d['resp_pergunta']
    if len(rp)>0:
        if 'id_usuario' in rp.columns and idv: rp=rp[rp['id_usuario'].isin(idv)]
        for c,dk in [('id_usuario','usuario'),('id_produto','produto')]:
            if c in rp.columns: rp[f'nome_{dk}']=rp[c].map(di.get(dk,{}))
        if 'id_pergunta_pesquisa' in rp.columns: rp['titulo_pergunta']=rp['id_pergunta_pesquisa'].map(di['pergunta'])
        # Add subcategoria/categoria names via produto
        if 'id_produto' in rp.columns:
            rp['nome_subcategoria']=rp['id_produto'].map(dpr_sc).map(di.get('subcategoria',{}))
            rp['nome_categoria']=rp['id_produto'].map(dpr_cat).map(di.get('categoria',{}))
        # Replace template masks in titulo_pergunta
        if 'titulo_pergunta' in rp.columns:
            for mask_key,col in [('{{nome_produto}}','nome_produto'),('{{nome_subcategoria}}','nome_subcategoria'),('{{nome_categoria}}','nome_categoria')]:
                if col in rp.columns:
                    mask=rp['titulo_pergunta'].astype(str).str.contains(mask_key.replace('{','\\{').replace('}','\\}'),na=False,regex=True)
                    if mask.any():
                        rp.loc[mask,'titulo_pergunta']=rp.loc[mask].apply(lambda r:str(r['titulo_pergunta']).replace(mask_key,str(r[col]) if pd.notna(r.get(col)) else ''),axis=1)
        if 'createdAt' in rp.columns: rp['createdAt']=pd.to_datetime(rp['createdAt'],errors='coerce')
    d['resp_pergunta']=rp
    # produto
    pr=d['produto']
    if len(pr)>0:
        for c,dk in [('id_categoria_produto','categoria'),('id_subcategoria_produto','subcategoria'),('id_marca','marca'),('id_empresa','empresa')]:
            if c in pr.columns: pr[f'nome_{dk}']=pr[c].map(di.get(dk,{}))
    d['produto']=pr
    # usuario
    us=d['usuario']
    if len(us)>0:
        if 'dados_pessoais' in us.columns:
            dp=us['dados_pessoais'].apply(pj)
            _gm={1:'Masculino',2:'Feminino',3:'Outro',4:'Prefiro não dizer',1.0:'Masculino',2.0:'Feminino',3.0:'Outro',4.0:'Prefiro não dizer','1':'Masculino','2':'Feminino','3':'Outro','4':'Prefiro não dizer'}
            _rm={1:'Até R$ 2.640',2:'R$ 2.641-5.280',3:'R$ 5.281-10.560',4:'Acima de R$ 10.560',1.0:'Até R$ 2.640',2.0:'R$ 2.641-5.280',3.0:'R$ 5.281-10.560',4.0:'Acima de R$ 10.560','1':'Até R$ 2.640','2':'R$ 2.641-5.280','3':'R$ 5.281-10.560','4':'Acima de R$ 10.560'}
            us['genero']=dp.apply(lambda x:_gm.get(x.get('opcao_genero'),x.get('opcao_genero')) if x.get('opcao_genero') is not None else None)
            us['ano_nascimento']=dp.apply(lambda x:x.get('ano_nascimento'))
            us['faixa_renda']=dp.apply(lambda x:_rm.get(x.get('opcao_faixa_renda_mensal'),x.get('opcao_faixa_renda_mensal')) if x.get('opcao_faixa_renda_mensal') is not None else None)
            a=datetime.now().year; us['idade']=us['ano_nascimento'].apply(lambda x:a-int(float(x)) if pd.notna(x) and str(x).replace('.','',1).replace('-','',1).isdigit() else None)
        if 'id_cidade' in us.columns:
            us['nome_cidade']=us['id_cidade'].map(di['cidade'])
            if len(d['cidade'])>0 and 'id_estado' in d['cidade'].columns:
                dce=d['cidade'].set_index('id')['id_estado'].to_dict()
                us['id_estado']=us['id_cidade'].map(dce); us['nome_estado']=us['id_estado'].map(di['estado'])
        if 'createdAt' in us.columns: us['createdAt']=pd.to_datetime(us['createdAt'],errors='coerce')
    d['usuario']=us
    # resgate
    rg=d['resgate']
    if len(rg)>0:
        if 'id_beneficio' in rg.columns: rg['nome_beneficio']=rg['id_beneficio'].map(di['beneficio'])
        if 'id_usuario' in rg.columns: rg['nome_usuario']=rg['id_usuario'].map(di['usuario'])
        if 'createdAt' in rg.columns: rg['createdAt']=pd.to_datetime(rg['createdAt'],errors='coerce')
    d['resgate']=rg
    # campanha
    ca=d['campanha']
    if len(ca)>0:
        for c in ['data_inicio','data_fim','createdAt']:
            if c in ca.columns: ca[c]=pd.to_datetime(ca[c],errors='coerce')
    d['campanha']=ca
    d['dicts']=di
    return d

# ============================================================================
# QUALITY ANALYSIS FUNCTIONS
# ============================================================================
def a_tempo(df):
    if len(df)==0 or 'createdAt' not in df.columns: return pd.DataFrame()
    df=df.sort_values(['id_usuario','createdAt']); df['seg']=df.groupby('id_usuario')['createdAt'].diff().dt.total_seconds()
    return df
def d_rapidas(dt,lim=2):
    if len(dt)==0 or 'seg' not in dt.columns: return pd.DataFrame()
    r=dt[dt['seg']<lim]
    if len(r)==0: return pd.DataFrame()
    a=r.groupby('id_usuario')['id'].count().rename('qr').to_frame()
    b=dt.groupby('id_usuario')['id'].count().rename('tt').to_frame()
    c=a.join(b); c['pct_r']=(c['qr']/c['tt']*100).round(2)
    return c.reset_index().sort_values('pct_r',ascending=False)
def d_repetitivos(df):
    if len(df)==0 or 'resposta' not in df.columns: return pd.DataFrame()
    d2=df.copy(); d2['rn']=pd.to_numeric(d2['resposta'].str.replace('"',''),errors='coerce'); d2=d2.dropna(subset=['rn'])
    if len(d2)==0: return pd.DataFrame()
    v=d2.groupby('id_usuario')['rn'].agg(['std','mean','count','nunique']).round(3)
    v.columns=['dp','media','total','unicos']
    return v.reset_index()
def d_extremas(df):
    if len(df)==0 or 'resposta' not in df.columns: return pd.DataFrame()
    d2=df.copy(); d2['rn']=pd.to_numeric(d2['resposta'].str.replace('"',''),errors='coerce'); d2=d2.dropna(subset=['rn'])
    d2['ext']=d2['rn'].isin([1,9]); e=d2.groupby('id_usuario').agg({'ext':['sum','count']})
    e.columns=['qe','tt']; e=e.reset_index(); e['pct_e']=(e['qe']/e['tt']*100).round(2)
    return e.sort_values('pct_e',ascending=False)
def d_volume(df):
    if len(df)==0 or 'createdAt' not in df.columns: return pd.DataFrame()
    d2=df.copy(); d2['dt']=d2['createdAt'].dt.date
    vd=d2.groupby(['id_usuario','dt']).size().reset_index(name='pd')
    vu=vd.groupby('id_usuario')['pd'].agg(['max','mean','sum']).round(2); vu.columns=['mx','md','tt']
    return vu.reset_index().sort_values('mx',ascending=False)
def c_score(dr,drp,de,dv,du):
    au=set()
    for df in [dr,drp,de,dv]:
        if len(df)>0 and 'id_usuario' in df.columns: au.update(df['id_usuario'].unique())
    if not au: return pd.DataFrame()
    s=pd.DataFrame({'id_usuario':list(au)})
    if len(dr)>0: s=s.merge(dr[['id_usuario','pct_r']],on='id_usuario',how='left')
    else: s['pct_r']=0
    if len(drp)>0: s=s.merge(drp[['id_usuario','dp']],on='id_usuario',how='left')
    else: s['dp']=1
    if len(de)>0: s=s.merge(de[['id_usuario','pct_e']],on='id_usuario',how='left')
    else: s['pct_e']=0
    if len(dv)>0: s=s.merge(dv[['id_usuario','mx']],on='id_usuario',how='left')
    else: s['mx']=1
    s=s.fillna(0)
    def nm(sr,iv=False):
        if sr.max()==sr.min(): return pd.Series([50]*len(sr))
        n=(sr-sr.min())/(sr.max()-sr.min())*100; return 100-n if iv else n
    s['sr']=nm(s['pct_r']); s['srp']=nm(s['dp'],iv=True); s['se']=nm(s['pct_e']); s['sv']=nm(s['mx'])
    s['score']=(100-(s['sr']*.35+s['srp']*.25+s['se']*.20+s['sv']*.20)).round(1)
    s['classif']=s['score'].apply(lambda x:'Muito Confiavel' if x>=80 else 'Confiavel' if x>=60 else 'Atencao' if x>=40 else 'Suspeito' if x>=20 else 'Muito Suspeito')
    s['nome_usuario']=s['id_usuario'].map(du)
    return s.sort_values('score')

# ============================================================================
# PG1: VISÃO GERAL
# ============================================================================
@st.fragment
def _overview_metrics(data):
    """Renderiza metricas do dashboard de forma isolada"""
    us,pr,rp,rq=data['usuario'],data['produto'],data['resp_pergunta'],data['resp_questionario']
    ca,em=data['campanha'],data['empresa']
    nu,nq,nr=len(us),len(rq),len(rp)
    pts=int(rq['pontos_ganhos'].sum()) if 'pontos_ganhos' in rq.columns and len(rq)>0 else 0
    # Row 1: Main KPIs
    c1,c2,c3,c4,c5=st.columns(5)
    with c1: st.markdown(mcard(f"{nu:,}","Total de Usuarios",c='#307FE2'),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{nq:,}","Questionarios Respondidos",c='#4ECDC4'),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{nr:,}","Total de Respostas",c='#45B7D1'),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{pts:,}","Pontos Distribuidos",c='#F7931E'),unsafe_allow_html=True)
    with c5: st.markdown(mcard(f"{len(pr):,}","Total de Produtos",c='#9B59B6'),unsafe_allow_html=True)
    # Row 2: Secondary KPIs
    ativos=rq['id_usuario'].nunique() if len(rq)>0 and 'id_usuario' in rq.columns else 0
    tx_conv=spct(ativos,nu) if nu>0 else 0
    med_resp=round(nr/ativos,1) if ativos>0 else 0
    c1,c2,c3,c4,c5,c6,c7=st.columns(7)
    with c1: st.markdown(mcard(f"{tx_conv}%","Taxa de Conversao",c='#14B8A6'),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{med_resp}","Media de Respostas",c='#307FE2'),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{tx_conv}%","Engajamento",c='#2ECC71'),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{len(data['categoria'])}","Categorias Ativas",c='#EC4899'),unsafe_allow_html=True)
    with c5: st.markdown(mcard(f"{len(data['subcategoria'])}","Subcategorias",c='#4ECDC4'),unsafe_allow_html=True)
    with c6: st.markdown(mcard(f"{len(em)}","Empresas",c='#2C3E50'),unsafe_allow_html=True)
    with c7: st.markdown(mcard(f"{len(ca)}","Campanhas",c='#FF6B6B'),unsafe_allow_html=True)

@st.fragment
def _overview_charts(data):
    """Renderiza graficos do dashboard de forma isolada"""
    us,pr,rq=data['usuario'],data['produto'],data['resp_questionario']
    # Charts Row 1: Tendencia + Genero
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Tendencia Mensal de Respostas</div>',unsafe_allow_html=True)
        if len(rq)>0 and 'createdAt' in rq.columns:
            rq_valid=rq[rq['createdAt'].notna()]
            if len(rq_valid)>0:
                mn=rq_valid.groupby(rq_valid['createdAt'].dt.to_period('M')).size().reset_index(name='qtd')
                mn.columns=['mes','qtd']; mn['mes']=mn['mes'].astype(str)
                mn=mn[mn['mes']!='NaT']
                if len(mn)>0:
                    fig=px.bar(mn,x='mes',y='qtd',color_discrete_sequence=[CL['primary']])
                    chart_layout(fig,350); fig.update_layout(xaxis_tickangle=45,xaxis_title="",yaxis_title="")
                    st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Distribuicao por Genero</div>',unsafe_allow_html=True)
        if 'genero' in us.columns:
            gc=us['genero'].dropna()
            gc=gc[gc.astype(str).str.strip()!='']
            if len(gc)>0:
                gv=gc.value_counts()
                fig=px.pie(values=gv.values.tolist(),names=gv.index.tolist(),color_discrete_sequence=['#307FE2','#FF6B6B','#4ECDC4','#F7931E'],hole=.45)
                chart_layout(fig,350); st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)

@st.fragment
def _overview_charts_extra(data):
    """Renderiza graficos extras do dashboard (rows 2-4) de forma isolada"""
    us,pr,rq=data['usuario'],data['produto'],data['resp_questionario']
    # Charts Row 2: Faixa Etaria + Top Categorias
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Faixa Etaria dos Testadores</div>',unsafe_allow_html=True)
        if 'idade' in us.columns:
            id_num=pd.to_numeric(us['idade'],errors='coerce')
            dv=us[id_num.notna()&(id_num>0)&(id_num<120)].copy()
            if len(dv)>0:
                dv['fx']=pd.cut(pd.to_numeric(dv['idade'],errors='coerce'),bins=[0,25,35,45,55,65,120],labels=['18-25','26-35','36-45','46-55','56-65','65+'])
                fc=dv['fx'].value_counts().sort_index()
                fc=fc[fc>0]
                if len(fc)>0:
                    fig=px.bar(x=fc.index.astype(str).tolist(),y=fc.values.tolist(),color_discrete_sequence=[CL['primary']])
                    chart_layout(fig,350); fig.update_layout(xaxis_title="",yaxis_title="")
                    st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Top 10 Categorias</div>',unsafe_allow_html=True)
        if len(rq)>0 and 'nome_categoria' in rq.columns and rq['nome_categoria'].notna().any():
            cc=rq['nome_categoria'].dropna().value_counts().head(10)
            cc=cc[cc.index.astype(str)!='nan']
            if len(cc)>0:
                fig=hbar(cc.values,cc.index,cs='Blues')
                chart_layout(fig,350); fig.update_layout(yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    # Charts Row 3: Subcategorias + Marcas
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Top 10 Subcategorias</div>',unsafe_allow_html=True)
        if len(rq)>0 and 'nome_subcategoria' in rq.columns:
            ts=rq['nome_subcategoria'].dropna().value_counts().head(10)
            ts=ts[ts.index.astype(str)!='nan']
            if len(ts)>0:
                fig=hbar(ts.values,ts.index,cs='Blues')
                chart_layout(fig,350); fig.update_layout(yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Top 10 Marcas</div>',unsafe_allow_html=True)
        if len(pr)>0 and 'nome_marca' in pr.columns:
            tm=pr['nome_marca'].dropna().value_counts().head(10)
            tm=tm[tm.index.astype(str)!='nan']
            if len(tm)>0:
                fig=hbar(tm.values,tm.index,cs='Greens')
                chart_layout(fig,350); fig.update_layout(yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    # Charts Row 4: Estado + Top Testadores
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Distribuicao por Estado</div>',unsafe_allow_html=True)
        if 'nome_estado' in us.columns:
            ec=us['nome_estado'].dropna().value_counts().head(10)
            ec=ec[ec.index.astype(str)!='nan']
            if len(ec)>0:
                fig=hbar(ec.values,ec.index,cs='Purples')
                chart_layout(fig,350); fig.update_layout(yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Top 10 Testadores</div>',unsafe_allow_html=True)
        if len(rq)>0 and 'nome_usuario' in rq.columns:
            tu=rq[rq['nome_usuario'].notna()].groupby('nome_usuario').size().sort_values(ascending=False).head(10)
            if len(tu)>0:
                fig=hbar(tu.values,tu.index,cs='Blues')
                chart_layout(fig,350); fig.update_layout(yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)

@st.fragment
def _overview_insights(data):
    """Renderiza insights estrategicos de forma isolada"""
    us,pr,rq=data['usuario'],data['produto'],data['resp_questionario']
    nu,nq=len(us),len(rq)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    st.markdown('<div class="chart-title" style="font-size:1.1rem;margin-bottom:12px">Insights Estrategicos</div>',unsafe_allow_html=True)
    ih=""
    if len(rq)>0 and 'createdAt' in rq.columns:
        wk=rq.groupby(rq['createdAt'].dt.to_period('W')).size()
        if len(wk)>=2:
            l,p=wk.iloc[-1],wk.iloc[-2]; ch=spct(l-p,p) if p>0 else 0
            ih+=ibox("Estrategico","Tendencia de Engajamento",f"Ultima semana: {l} questionarios ({'↑' if ch>0 else '↓'} {abs(ch)}%). {'Momentum positivo - manter campanhas.' if ch>0 else 'Queda detectada - acao de reengajamento recomendada.'}")
    if nu>0 and len(rq)>0 and 'id_usuario' in rq.columns:
        tx=spct(rq['id_usuario'].nunique(),nu)
        ih+=ibox("Tatico","Taxa de Ativacao",f"{tx}% dos {nu:,} testadores responderam questionarios. {'Base engajada.' if tx>30 else 'Bonificacao para primeiros acessos pode elevar a base ativa.'}")
    if len(pr)>0 and nq>0 and 'id_produto' in rq.columns:
        av=rq['id_produto'].nunique(); cob=spct(av,len(pr))
        ih+=ibox("Operacional","Cobertura de Produtos",f"{av}/{len(pr)} produtos avaliados ({cob}%). {'Excelente cobertura.' if cob>60 else 'Criar pesquisas para produtos sem avaliacao.'}")
    if ih: st.markdown(ih,unsafe_allow_html=True)

def pg_overview(data):
    st.markdown(section_header("Dashboard Geral","Visao consolidada da plataforma Foodtest"),unsafe_allow_html=True)
    # Metricas (renderiza como fragmento isolado)
    _overview_metrics(data)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    # Graficos (renderiza como fragmento isolado)
    _overview_charts(data)
    _overview_charts_extra(data)
    _overview_insights(data)

# ============================================================================
# PG2: RESPOSTAS
# ============================================================================
def pg_respostas(data):
    st.markdown(section_header("Analise de Respostas","Detalhamento completo das respostas coletadas"),unsafe_allow_html=True)
    rp,rq=data['resp_pergunta'],data['resp_questionario']
    if len(rp)==0: st.warning("Sem dados."); return
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(mcard(f"{len(rp):,}","Total Respostas"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{len(rq):,}","Questionários",c=CL['accent1']),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{rp['id_usuario'].nunique():,}" if 'id_usuario' in rp.columns else "0","Usuários",c=CL['accent2']),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{rp['id_produto'].nunique():,}" if 'id_produto' in rp.columns else "0","Produtos",c=CL['purple']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    # Survey reference data
    se_df,pg_q,pesq_p,pesq_s=data['sessao'],data['pergunta'],data['pesq_produto'],data['pesq_subcategoria']
    di=data['dicts']
    def _qa(rs,kp=""):
        if len(rs)==0 or 'resposta' not in rs.columns: st.info("Sem respostas."); return
        cl=rs['resposta'].astype(str).str.replace('"','').str.strip(); nm=pd.to_numeric(cl,errors='coerce')
        if nm.notna().sum()>len(rs)*.5:
            ca,cb=st.columns(2)
            with ca:
                fig=px.histogram(x=nm.dropna(),nbins=9,color_discrete_sequence=[CL['primary']]); fig.update_layout(height=300)
                st.plotly_chart(fig,use_container_width=True,key=f"qa_h_{kp}")
            with cb: st.dataframe(pd.DataFrame({'Métrica':['Média','Mediana','DP','Mín','Máx'],'Valor':[f"{nm.mean():.2f}",f"{nm.median():.2f}",f"{nm.std():.2f}",f"{nm.min():.0f}",f"{nm.max():.0f}"]}),hide_index=True)
        else:
            rc=cl.value_counts().head(15); fig=hbar(rc.values,rc.index,cs='Blues')
            fig.update_layout(height=min(400,max(200,len(rc)*30)),coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True,key=f"qa_b_{kp}")
    def _radar(resps,color=CL['primary'],kp=""):
        if len(resps)==0 or 'titulo_pergunta' not in resps.columns: return
        pergs=resps.groupby('titulo_pergunta').apply(lambda x: pd.to_numeric(x['resposta'].str.replace('"',''),errors='coerce').mean()).dropna()
        if len(pergs)>=3:
            st.markdown('<div class="chart-title">Perfil Sensorial</div>',unsafe_allow_html=True)
            fig=go.Figure(go.Scatterpolar(r=pergs.values,theta=pergs.index.tolist(),fill='toself',line_color=color))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,9])),height=400,showlegend=False)
            st.plotly_chart(fig,use_container_width=True,key=f"radar_{kp}")
    def _detail_questions(resps,kp=""):
        if len(resps)==0 or 'titulo_pergunta' not in resps.columns: return
        st.markdown('<div class="chart-title">Detalhamento por Pergunta</div>',unsafe_allow_html=True)
        q_c=resps.groupby('titulo_pergunta').size().sort_values(ascending=False)
        for i,qtit in enumerate(q_c.index):
            qr=resps[resps['titulo_pergunta']==qtit]
            with st.expander(f"{qtit} ({len(qr)} respostas)"):
                _qa(qr,kp=f"{kp}_{i}")
    t1,t2,t3,t4,t5,t6=st.tabs(["Pergunta","Questionario","Produto","Subcategoria","Usuario","Explorar"])
    with t1:
        if 'titulo_pergunta' in rp.columns:
            pst=rp.groupby('titulo_pergunta').agg({'id':'count','id_usuario':'nunique'}).rename(columns={'id':'resp','id_usuario':'usr'}).sort_values('resp',ascending=False)
            b=st.text_input("Buscar:",key="bp")
            pf=[p for p in pst.index if b.lower() in str(p).lower()] if b else pst.index[:20].tolist()
            if pf:
                sel=st.selectbox("Selecione:",pf,key="sp")
                if sel:
                    rs=rp[rp['titulo_pergunta']==sel]; st.metric("Respostas",f"{len(rs):,}")
                    _qa(rs,kp="t1")
    with t2:
        surveys=[]
        if len(pesq_p)>0:
            for _,r in pesq_p.iterrows():
                pn=di['produto'].get(r.get('id_produto'),'')
                tit=r.get('titulo',f"Pesquisa #{r['id']}")
                lbl=f"[Produto] {tit}{' - '+pn if pn else ''}"
                surveys.append(('produto',r['id'],lbl))
        if len(pesq_s)>0:
            for _,r in pesq_s.iterrows():
                sn=di['subcategoria'].get(r.get('id_subcategoria_produto'),'')
                tit=r.get('titulo',f"Pesquisa #{r['id']}")
                lbl=f"[Subcategoria] {tit}{' - '+sn if sn else ''}"
                surveys.append(('subcategoria',r['id'],lbl))
        if surveys:
            labels=[s[2] for s in surveys]
            bq=st.text_input("Buscar questionario:",key="bq")
            fl=[l for l in labels if bq.lower() in l.lower()] if bq else labels
            if fl:
                sel=st.selectbox("Selecione o questionário:",fl,key="sq")
                idx=labels.index(sel); stype,sid,_=surveys[idx]
                # Determine product/subcategory names for template mask replacement
                ctx_prod,ctx_sub='',''
                if stype=='produto':
                    sv_row=pesq_p[pesq_p['id']==sid]
                    if len(sv_row)>0: ctx_prod=di['produto'].get(sv_row.iloc[0].get('id_produto'),'') or ''
                elif stype=='subcategoria':
                    sv_row=pesq_s[pesq_s['id']==sid]
                    if len(sv_row)>0: ctx_sub=di['subcategoria'].get(sv_row.iloc[0].get('id_subcategoria_produto'),'') or ''
                filt='id_pesquisa_produto' if stype=='produto' else 'id_pesquisa_subcategoria'
                sess=se_df[se_df[filt]==sid] if filt in se_df.columns else pd.DataFrame()
                if len(sess)>0:
                    sids=sess['id'].tolist()
                    qs=pg_q[pg_q['id_sessao_pesquisa'].isin(sids)] if 'id_sessao_pesquisa' in pg_q.columns else pd.DataFrame()
                    if len(qs)>0:
                        qids=qs['id'].tolist()
                        resps=rp[rp['id_pergunta_pesquisa'].isin(qids)] if 'id_pergunta_pesquisa' in rp.columns else pd.DataFrame()
                        ca,cb,cc=st.columns(3)
                        with ca: st.metric("Perguntas",f"{len(qs)}")
                        with cb: st.metric("Respostas",f"{len(resps):,}")
                        with cc: st.metric("Respondentes",f"{resps['id_usuario'].nunique():,}" if len(resps)>0 and 'id_usuario' in resps.columns else "0")
                        _radar(resps,kp="t2")
                        sort_col='ordem' if 'ordem' in qs.columns else 'id'
                        st.markdown('<div class="chart-title">Perguntas do Questionário</div>',unsafe_allow_html=True)
                        for qi,(_,q) in enumerate(qs.sort_values(sort_col).iterrows()):
                            qid=q['id']; qtit=q.get('titulo',f'Pergunta #{qid}')
                            qtit=str(qtit).replace('{{nome_produto}}',ctx_prod).replace('{{nome_subcategoria}}',ctx_sub)
                            qr=resps[resps['id_pergunta_pesquisa']==qid]
                            with st.expander(f"{qtit} ({len(qr)} respostas)"):
                                _qa(qr,kp=f"t2_{qi}")
                    else: st.info("Nenhuma pergunta encontrada para este questionário.")
                else: st.info("Nenhuma sessão encontrada para este questionário.")
        else: st.info("Nenhum questionário encontrado.")
    with t3:
        if 'nome_produto' in rp.columns:
            pp_c=rp.groupby('nome_produto').size().sort_values(ascending=False)
            sel_p=st.selectbox("Selecione o Produto:",pp_c.index.tolist(),key="sp_prod_cons")
            if sel_p:
                prod_r=rp[rp['nome_produto']==sel_p]
                ca,cb,cc=st.columns(3)
                with ca: st.metric("Respostas",f"{len(prod_r):,}")
                with cb: st.metric("Perguntas",f"{prod_r['titulo_pergunta'].nunique() if 'titulo_pergunta' in prod_r.columns else 0}")
                with cc: st.metric("Respondentes",f"{prod_r['id_usuario'].nunique() if 'id_usuario' in prod_r.columns else 0}")
                _radar(prod_r,kp="t3")
                _detail_questions(prod_r,kp="t3")
    with t4:
        if len(pesq_s)>0 and 'id_subcategoria_produto' in pesq_s.columns:
            sc_groups={}
            for _,r in pesq_s.iterrows():
                scid=r.get('id_subcategoria_produto')
                key=di['subcategoria'].get(scid,f'Subcategoria #{scid}') if pd.notna(scid) else 'Sem subcategoria'
                sc_groups.setdefault(key,[]).append(r['id'])
            sc_names=sorted(sc_groups.keys())
            sel_sc=st.selectbox("Selecione a Subcategoria:",sc_names,key="ssc_resp")
            if sel_sc:
                sv_ids=sc_groups[sel_sc]
                sess=se_df[se_df['id_pesquisa_subcategoria'].isin(sv_ids)] if 'id_pesquisa_subcategoria' in se_df.columns else pd.DataFrame()
                if len(sess)>0:
                    sids=sess['id'].tolist()
                    qs=pg_q[pg_q['id_sessao_pesquisa'].isin(sids)] if 'id_sessao_pesquisa' in pg_q.columns else pd.DataFrame()
                    if len(qs)>0:
                        qids=qs['id'].tolist()
                        resps=rp[rp['id_pergunta_pesquisa'].isin(qids)] if 'id_pergunta_pesquisa' in rp.columns else pd.DataFrame()
                        ca,cb,cc,cd=st.columns(4)
                        with ca: st.metric("Pesquisas",f"{len(sv_ids)}")
                        with cb: st.metric("Perguntas",f"{len(qs)}")
                        with cc: st.metric("Respostas",f"{len(resps):,}")
                        with cd: st.metric("Respondentes",f"{resps['id_usuario'].nunique():,}" if len(resps)>0 and 'id_usuario' in resps.columns else "0")
                        _radar(resps,CL['accent1'],kp="t4")
                        _detail_questions(resps,kp="t4")
                    else: st.info("Nenhuma pergunta encontrada.")
                else: st.info("Nenhuma sessão encontrada.")
        else: st.info("Sem pesquisas de subcategoria.")
    with t5:
        if 'id_usuario' in rp.columns:
            us_agg=rp.groupby('id_usuario').agg({'id':'count','id_produto':'nunique'}).rename(columns={'id':'resp','id_produto':'prod'})
            if 'nome_usuario' in rp.columns: us_agg=us_agg.join(rp.groupby('id_usuario')['nome_usuario'].first())
            us_agg=us_agg.sort_values('resp',ascending=False)
            fig=hbar(us_agg.head(15)['resp'].values,us_agg.head(15)['nome_usuario'].values if 'nome_usuario' in us_agg.columns else us_agg.head(15).index.astype(str),cs='Blues')
            fig.update_layout(height=450,coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True)
            # Drill-down por usuario
            st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
            st.markdown('<div class="chart-title">Drill-down por Usuario</div>',unsafe_allow_html=True)
            user_names=us_agg['nome_usuario'].dropna().tolist() if 'nome_usuario' in us_agg.columns else us_agg.index.astype(str).tolist()
            if user_names:
                sel_user=st.selectbox("Selecione o Usuario:",user_names,key="dd_user_resp")
                if sel_user:
                    user_resps=rp[rp['nome_usuario']==sel_user]
                    c1,c2,c3=st.columns(3)
                    with c1: st.metric("Respostas",f"{len(user_resps):,}")
                    with c2: st.metric("Produtos",f"{user_resps['id_produto'].nunique() if 'id_produto' in user_resps.columns else 0}")
                    with c3: st.metric("Perguntas",f"{user_resps['titulo_pergunta'].nunique() if 'titulo_pergunta' in user_resps.columns else 0}")
                    uid=user_resps['id_usuario'].iloc[0] if len(user_resps)>0 else None
                    if uid is not None:
                        qu=rq[rq['id_usuario']==uid] if 'id_usuario' in rq.columns else pd.DataFrame()
                        if len(qu)>0:
                            st.markdown('<div class="chart-title">Questionarios Respondidos</div>',unsafe_allow_html=True)
                            qu_cols=[c for c in ['createdAt','nome_produto','nome_subcategoria','nome_categoria','pontos_ganhos'] if c in qu.columns]
                            if qu_cols:
                                qu_display=qu[qu_cols].sort_values('createdAt',ascending=False) if 'createdAt' in qu_cols else qu[qu_cols]
                                st.dataframe(qu_display,hide_index=True,use_container_width=True,height=min(400,max(150,len(qu_display)*35+40)))
                    st.markdown('<div class="chart-title">Ultimas Respostas</div>',unsafe_allow_html=True)
                    ur_cols=[c for c in ['createdAt','nome_produto','titulo_pergunta','resposta'] if c in user_resps.columns]
                    if ur_cols:
                        ur_display=user_resps[ur_cols].sort_values('createdAt',ascending=False).head(50) if 'createdAt' in ur_cols else user_resps[ur_cols].head(50)
                        st.dataframe(ur_display,hide_index=True,use_container_width=True,height=min(500,max(150,len(ur_display)*35+40)))
    with t6:
        c1,c2,c3=st.columns(3)
        with c1: fp=st.selectbox("Produto:",['Todos']+(rp['nome_produto'].dropna().unique().tolist() if 'nome_produto' in rp.columns else []),key="fpe")
        with c2: fu=st.selectbox("Usuario:",['Todos']+(rp['nome_usuario'].dropna().unique().tolist()[:100] if 'nome_usuario' in rp.columns else []),key="fue")
        with c3: lm=st.slider("Máx:",10,500,100,key="le")
        df=rp.copy()
        if fp!='Todos' and 'nome_produto' in df.columns: df=df[df['nome_produto']==fp]
        if fu!='Todos' and 'nome_usuario' in df.columns: df=df[df['nome_usuario']==fu]
        if 'createdAt' in df.columns: df=df.sort_values('createdAt',ascending=False)
        cols=[c for c in ['createdAt','nome_usuario','nome_produto','titulo_pergunta','resposta'] if c in df.columns]
        st.markdown(f"**{min(lm,len(df)):,} de {len(df):,}**")
        if cols: st.dataframe(df[cols].head(lm),hide_index=True,use_container_width=True,height=500)

# ============================================================================
# PG3: QUALIDADE
# ============================================================================
def pg_qualidade(data):
    st.markdown(section_header("Qualidade dos Dados","Monitoramento de confiabilidade e anomalias"),unsafe_allow_html=True)
    rp,rq=data['resp_pergunta'],data['resp_questionario']; du=data['dicts']['usuario']
    if len(rp)==0: st.warning("Sem dados."); return
    with st.spinner("Calculando..."):
        dt=a_tempo(rp); dr=d_rapidas(dt); drp=d_repetitivos(rp); de=d_extremas(rp); dv=d_volume(rq)
        sc=c_score(dr,drp,de,dv,du)
    if len(sc)==0: st.info("Dados insuficientes."); return
    tot=len(sc); mc_=len(sc[sc['score']>=80]); co=len(sc[(sc['score']>=60)&(sc['score']<80)])
    at=len(sc[(sc['score']>=40)&(sc['score']<60)]); su=len(sc[sc['score']<40])
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(mcard(f"{tot}","Analisados"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{spct(mc_+co,tot)}%","Confiáveis",f"({mc_+co})"),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{at}","Atenção",dt='negative' if at>5 else 'positive'),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{su}","Suspeitos",dt='negative' if su>3 else 'positive'),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        fig=px.histogram(sc,x='score',nbins=20,color_discrete_sequence=[CL['primary']],title="Distribuição Scores")
        fig.add_vline(x=40,line_dash="dash",line_color=CL['danger']); fig.add_vline(x=60,line_dash="dash",line_color=CL['warning']); fig.add_vline(x=80,line_dash="dash",line_color=CL['success'])
        fig.update_layout(height=400); st.plotly_chart(fig,use_container_width=True)
    with c2:
        cc=sc['classif'].value_counts()
        cm={'Muito Confiavel':CL['success'],'Confiavel':'#FF9500','Atencao':'#E67E22','Suspeito':CL['danger'],'Muito Suspeito':'#8E44AD'}
        fig=px.pie(values=cc.values.tolist(),names=cc.index.tolist(),color=cc.index.tolist(),color_discrete_map=cm,hole=.4)
        fig.update_layout(height=400); st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="chart-title">Top 10 Suspeitos</div>',unsafe_allow_html=True)
    top=sc.nsmallest(10,'score')
    fig=px.bar(top,x='score',y='nome_usuario',orientation='h',color_discrete_sequence=[CL['danger']])
    fig.update_layout(height=400); fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig,use_container_width=True)
    st.session_state['df_scores']=sc
    st.markdown(ibox("Estratégico","Saúde da Base",f"{spct(mc_+co,tot)}% confiáveis. {su} suspeitos ({spct(su,tot)}%). {'Base saudável.' if spct(mc_+co,tot)>80 else 'Recomenda-se limpeza.'}"),unsafe_allow_html=True)

# ============================================================================
# PG4: CONSULTA USUÁRIO
# ============================================================================
def pg_usuario(data):
    st.markdown(section_header("Consulta de Usuario","Perfil detalhado e historico individual"),unsafe_allow_html=True)
    us,rp,rq=data['usuario'],data['resp_pergunta'],data['resp_questionario']
    if len(us)==0: st.warning("Sem dados."); return
    ul=us[['id','nome']].copy(); ul['d']=ul['id'].astype(str)+" - "+ul['nome']
    sel=st.selectbox("Selecione:",ul['d'].tolist(),key="su")
    uid=int(sel.split(" - ")[0]); ui=us[us['id']==uid]
    if len(ui)==0: st.error("N/A"); return
    u=ui.iloc[0]
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(f'<div class="mc"><p class="ml">Nome</p><p style="font-size:1rem;font-weight:600;color:#2C3E50">{u["nome"]}</p></div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="mc"><p class="ml">Gênero</p><p style="font-size:1rem;font-weight:600;color:#2C3E50">{u.get("genero","N/A") if pd.notna(u.get("genero")) else "N/A"}</p></div>',unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="mc"><p class="ml">Idade</p><p style="font-size:1rem;font-weight:600;color:#2C3E50">{u.get("idade","N/A") if pd.notna(u.get("idade")) else "N/A"}</p></div>',unsafe_allow_html=True)
    with c4:
        loc=f'{u.get("nome_cidade","")}/{u.get("nome_estado","")}'.strip('/')
        st.markdown(f'<div class="mc"><p class="ml">Local</p><p style="font-size:.85rem;font-weight:600;color:#2C3E50">{loc or "N/A"}</p></div>',unsafe_allow_html=True)
    ru=rp[rp['id_usuario']==uid] if len(rp)>0 and 'id_usuario' in rp.columns else pd.DataFrame()
    qu=rq[rq['id_usuario']==uid] if len(rq)>0 and 'id_usuario' in rq.columns else pd.DataFrame()
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(mcard(f"{len(qu)}","Questionários"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{len(ru)}","Respostas",c=CL['accent1']),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{int(qu['pontos_ganhos'].sum()) if 'pontos_ganhos' in qu.columns and len(qu)>0 else 0}","Pontos",c=CL['orange']),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{qu['id_produto'].nunique() if len(qu)>0 and 'id_produto' in qu.columns else 0}","Produtos",c=CL['purple']),unsafe_allow_html=True)
    if 'df_scores' in st.session_state:
        sc=st.session_state['df_scores']; us_=sc[sc['id_usuario']==uid]
        if len(us_)>0:
            st.markdown('<div class="chart-title">Confiabilidade</div>',unsafe_allow_html=True)
            c1,c2=st.columns([1,2])
            with c1: st.plotly_chart(gauge(us_.iloc[0]['score'],"Score"),use_container_width=True); st.markdown(f"<h3 style='text-align:center'>{us_.iloc[0]['classif']}</h3>",unsafe_allow_html=True)
            with c2:
                cp=pd.DataFrame({'Comp':['Rapidez','Repetitividade','Extremismo','Volume'],'Score':[us_.iloc[0]['sr'],us_.iloc[0]['srp'],us_.iloc[0]['se'],us_.iloc[0]['sv']]})
                fig=px.bar(cp,x='Comp',y='Score',color='Score',color_continuous_scale='RdYlGn_r'); fig.update_layout(height=300,coloraxis_showscale=False)
                st.plotly_chart(fig,use_container_width=True)
    if len(ru)>0:
        st.markdown('<div class="chart-title">Ultimas 20 Respostas</div>',unsafe_allow_html=True)
        cols=[c for c in ['createdAt','nome_produto','titulo_pergunta','resposta'] if c in ru.columns]
        st.dataframe(ru[cols].sort_values('createdAt',ascending=False).head(20),hide_index=True,use_container_width=True)

# ============================================================================
# PG5: MAPEAMENTO
# ============================================================================
def pg_mapeamento(data):
    st.markdown(section_header("Mapeamento de Pesquisas","Relacao entre categorias, produtos e respostas"),unsafe_allow_html=True)
    rq=data['resp_questionario']
    if len(rq)==0: st.warning("Sem dados."); return
    t1,t2,t3,t4=st.tabs(["Categoria","Subcategoria","Produto","Temporal"])
    with t1:
        if 'nome_categoria' in rq.columns and rq['nome_categoria'].notna().any():
            cs=rq.groupby('nome_categoria').agg({'id':'count','id_usuario':'nunique','id_produto':'nunique','pontos_ganhos':'sum'}).rename(columns={'id':'quest','id_usuario':'usr','id_produto':'prod','pontos_ganhos':'pts'}).sort_values('quest',ascending=False)
            c1,c2=st.columns(2)
            with c1:
                fig=px.bar(cs.reset_index(),x='quest',y='nome_categoria',orientation='h',color='quest',color_continuous_scale='Blues')
                fig.update_layout(height=500,coloraxis_showscale=False); fig.update_yaxes(autorange="reversed"); st.plotly_chart(fig,use_container_width=True)
            with c2:
                fig=px.pie(values=cs['quest'].values.tolist(),names=cs.index.tolist(),color_discrete_sequence=PAL,hole=.4); fig.update_layout(height=500); st.plotly_chart(fig,use_container_width=True)
            st.dataframe(cs.reset_index(),hide_index=True,use_container_width=True)
    with t2:
        if 'nome_subcategoria' in rq.columns and 'nome_categoria' in rq.columns:
            ss=rq.groupby(['nome_categoria','nome_subcategoria']).size().reset_index(name='quest').dropna()
            if len(ss)>0:
                fig=px.treemap(ss,path=['nome_categoria','nome_subcategoria'],values='quest',color='quest',color_continuous_scale='Blues')
                fig.update_layout(height=600); st.plotly_chart(fig,use_container_width=True)
    with t3:
        if 'nome_produto' in rq.columns:
            pp=rq.groupby('nome_produto').size().sort_values(ascending=False).head(20)
            fig=hbar(pp.values,pp.index,cs='Greens')
            fig.update_layout(height=600,coloraxis_showscale=False); fig.update_yaxes(autorange="reversed"); st.plotly_chart(fig,use_container_width=True)
    with t4:
        if 'data' in rq.columns:
            dl=rq.groupby('data').size().reset_index(name='q'); dl['data']=pd.to_datetime(dl['data'])
            fig=px.line(dl,x='data',y='q',markers=True); fig.update_traces(line_color=CL['primary']); fig.update_layout(height=400)
            st.plotly_chart(fig,use_container_width=True)
        c1,c2=st.columns(2)
        with c1:
            if 'hora' in rq.columns:
                h=rq.groupby('hora').size().reset_index(name='q')
                fig=px.bar(h,x='hora',y='q',color='q',color_continuous_scale='Blues'); fig.update_layout(height=350,coloraxis_showscale=False)
                st.plotly_chart(fig,use_container_width=True)
        with c2:
            if 'dia_semana' in rq.columns:
                dn={'Monday':'Seg','Tuesday':'Ter','Wednesday':'Qua','Thursday':'Qui','Friday':'Sex','Saturday':'Sáb','Sunday':'Dom'}
                do=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
                w=rq.groupby('dia_semana').size().reset_index(name='q'); w['o']=w['dia_semana'].map({d:i for i,d in enumerate(do)})
                w=w.sort_values('o'); w['dp']=w['dia_semana'].map(dn)
                fig=px.bar(w,x='dp',y='q',color='q',color_continuous_scale='Greens'); fig.update_layout(height=350,coloraxis_showscale=False)
                st.plotly_chart(fig,use_container_width=True)

# ============================================================================
# PG6: DEMOGRÁFICA
# ============================================================================
def pg_demografica(data):
    st.markdown(section_header("Analise Demografica","Perfil dos testadores por genero, idade, renda e regiao"),unsafe_allow_html=True)
    us=data['usuario']
    if len(us)==0: st.warning("Sem dados."); return
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(mcard(f"{len(us):,}","Total"),unsafe_allow_html=True)
    with c2:
        cc=0
        if 'is_cadastro_completo' in us.columns:
            cv=us['is_cadastro_completo'].fillna(False)
            if cv.dtype=='object': cv=cv.astype(str).str.lower().map({'true':True,'false':False,'1':True,'0':False,'nan':False}).fillna(False)
            cc=int(cv.sum())
        st.markdown(mcard(f"{cc:,}","Cad. Completos",c=CL['success']),unsafe_allow_html=True)
    with c3:
        g=us['genero'].value_counts().index[0] if 'genero' in us.columns and len(us['genero'].dropna())>0 else 'N/A'
        st.markdown(mcard(g,"Gênero Pred.",c=CL['pink']),unsafe_allow_html=True)
    with c4:
        im=f"{us['idade'].dropna().mean():.0f}a" if 'idade' in us.columns and us['idade'].notna().any() else 'N/A'
        st.markdown(mcard(im,"Idade Média",c=CL['purple']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        if 'genero' in us.columns:
            st.markdown('<div class="chart-title">Distribuicao por Genero</div>',unsafe_allow_html=True)
            gc=us['genero'].value_counts()
            fig=px.pie(values=gc.values.tolist(),names=gc.index.tolist(),color_discrete_sequence=[CL['primary'],CL['secondary'],CL['accent1']],hole=.4)
            fig.update_layout(height=400); st.plotly_chart(fig,use_container_width=True)
    with c2:
        if 'idade' in us.columns:
            st.markdown('<div class="chart-title">Faixa Etaria</div>',unsafe_allow_html=True)
            dv=us[us['idade'].notna()&(us['idade']>0)].copy()
            if len(dv)>0:
                dv['fx']=pd.cut(dv['idade'].astype(float),bins=[0,25,35,45,55,65,100],labels=['18-25','26-35','36-45','46-55','56-65','65+'])
                fc=dv['fx'].value_counts().sort_index()
                fig=px.bar(x=fc.index.astype(str).tolist(),y=fc.values.tolist(),color=fc.values.tolist(),color_continuous_scale='Blues')
                fig.update_layout(height=400,coloraxis_showscale=False); st.plotly_chart(fig,use_container_width=True)
    if 'faixa_renda' in us.columns:
        st.markdown('<div class="chart-title">Faixa de Renda</div>',unsafe_allow_html=True)
        rc=us['faixa_renda'].value_counts()
        fig=px.bar(pd.DataFrame({'r':rc.index.tolist(),'q':rc.values.tolist()}),x='q',y='r',orientation='h',color='q',color_continuous_scale='Greens')
        fig.update_layout(height=400,coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig,use_container_width=True)
    if 'nome_estado' in us.columns:
        st.markdown('<div class="chart-title">Distribuicao Geografica</div>',unsafe_allow_html=True)
        ec=us['nome_estado'].value_counts().head(15)
        fig=hbar(ec.values,ec.index,cs='Purples')
        fig.update_layout(height=400,coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig,use_container_width=True)
    ih=""
    if 'genero' in us.columns and len(us['genero'].dropna())>0:
        gc=us['genero'].value_counts(); fem=gc.get('Feminino',0)
        ih+=ibox("Estratégico","Perfil",f"Base {spct(fem,len(us))}% feminina. {'Diversificar recrutamento.' if abs(spct(fem,len(us))-50)>20 else 'Base equilibrada.'}")
    if cc>0:
        ih+=ibox("Operacional","Cadastros",f"{spct(cc,len(us))}% completos. {'Meta atingida!' if spct(cc,len(us))>70 else 'Incentivar conclusão com pontos.'}")
    if ih: st.markdown(ih,unsafe_allow_html=True)

# ============================================================================
# PG7: CAMPANHAS
# ============================================================================
def pg_campanhas(data):
    st.markdown(section_header("Campanhas","Gestao e performance das campanhas ativas e encerradas"),unsafe_allow_html=True)
    ca=data['campanha']
    if len(ca)==0: st.warning("Sem dados de campanhas."); return
    n=len(ca)
    hoje=pd.Timestamp.now(tz='UTC')
    ativas=0; enc=0
    if 'data_fim' in ca.columns:
        ativas=len(ca[ca['data_fim']>=hoje]); enc=len(ca[ca['data_fim']<hoje])
    pts_t=0
    if 'pontuacao' in ca.columns: pts_t=int(pd.to_numeric(ca['pontuacao'],errors='coerce').fillna(0).sum())
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(mcard(f"{n}","Total Campanhas"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{ativas}","Ativas",c=CL['success']),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{enc}","Encerradas",c=CL['danger']),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{pts_t:,}","Pontos Totais",c=CL['orange']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    t1,t2=st.tabs(["Lista de Campanhas","Timeline"])
    with t1:
        disp=ca.copy()
        if 'data_fim' in disp.columns:
            disp['status']=disp['data_fim'].apply(lambda x:'Ativa' if pd.notna(x) and x>=hoje else 'Encerrada')
        cols=[c for c in ['id','nome','descricao','pontuacao','data_inicio','data_fim','status','createdAt'] if c in disp.columns]
        st.dataframe(disp[cols].sort_values('createdAt',ascending=False) if 'createdAt' in cols else disp[cols],hide_index=True,use_container_width=True)
    with t2:
        if 'data_inicio' in ca.columns and 'data_fim' in ca.columns:
            tl=ca.dropna(subset=['data_inicio','data_fim']).copy()
            if len(tl)>0 and 'nome' in tl.columns:
                fig=px.timeline(tl,x_start='data_inicio',x_end='data_fim',y='nome',
                    color='pontuacao' if 'pontuacao' in tl.columns else None,
                    color_continuous_scale='Blues')
                fig.update_layout(height=max(300,len(tl)*40),yaxis_title="")
                st.plotly_chart(fig,use_container_width=True)
            else: st.info("Dados insuficientes para timeline.")
        else: st.info("Colunas data_inicio/data_fim não encontradas.")
    # Insights
    ih=""
    if ativas>0: ih+=ibox("Operacional","Campanhas Ativas",f"{ativas} campanhas ativas no momento. Verificar engajamento e prazos de encerramento.")
    if 'pontuacao' in ca.columns:
        mp=pd.to_numeric(ca['pontuacao'],errors='coerce').mean()
        ih+=ibox("Tático","Pontuação Média",f"Média de {mp:.0f} pontos por campanha. {'Considerar aumentar incentivos.' if mp<50 else 'Nível de incentivo adequado.'}")
    if ih: st.markdown(ih,unsafe_allow_html=True)

# ============================================================================
# PG8: CATEGORIAS & SUBCATEGORIAS
# ============================================================================
def pg_categorias(data):
    st.markdown(section_header("Categorias & Subcategorias","Estrutura do catalogo de produtos"),unsafe_allow_html=True)
    cat,sub=data['categoria'],data['subcategoria']
    pr=data['produto']; rq=data['resp_questionario']
    nc,ns=len(cat),len(sub)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(mcard(f"{nc}","Categorias"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{ns}","Subcategorias",c=CL['accent1']),unsafe_allow_html=True)
    with c3:
        ratio=f"{ns/nc:.1f}" if nc>0 else "0"
        st.markdown(mcard(ratio,"Subcat/Cat",c=CL['teal']),unsafe_allow_html=True)
    with c4:
        np_=len(pr)
        st.markdown(mcard(f"{np_}","Produtos",c=CL['purple']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["Categorias","Subcategorias","Treemap"])
    with t1:
        if len(cat)>0:
            ct=cat.copy()
            # Contar subcategorias por categoria
            if len(sub)>0 and 'id_categoria_produto' in sub.columns:
                sc_cnt=sub.groupby('id_categoria_produto').size().reset_index(name='qtd_subcategorias')
                ct=ct.merge(sc_cnt,left_on='id',right_on='id_categoria_produto',how='left').fillna(0)
            # Contar produtos por categoria
            if len(pr)>0 and 'id_categoria_produto' in pr.columns:
                pr_cnt=pr.groupby('id_categoria_produto').size().reset_index(name='qtd_produtos')
                ct=ct.merge(pr_cnt,left_on='id',right_on='id_categoria_produto',how='left',suffixes=('','_p')).fillna(0)
            cols=[c for c in ['id','nome','qtd_subcategorias','qtd_produtos','createdAt'] if c in ct.columns]
            st.dataframe(ct[cols].sort_values('nome') if 'nome' in cols else ct[cols],hide_index=True,use_container_width=True)
            # Gráfico
            if 'qtd_produtos' in ct.columns:
                top=ct.nlargest(15,'qtd_produtos')
                fig=px.bar(top,x='qtd_produtos',y='nome',orientation='h',color='qtd_produtos',color_continuous_scale='Blues')
                fig.update_layout(height=450,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
    with t2:
        if len(sub)>0:
            sc=sub.copy()
            if len(cat)>0:
                cat_d=cat.set_index('id')['nome'].to_dict() if 'id' in cat.columns and 'nome' in cat.columns else {}
                if 'id_categoria_produto' in sc.columns: sc['nome_categoria']=sc['id_categoria_produto'].map(cat_d)
            # Contar produtos por subcategoria
            if len(pr)>0 and 'id_subcategoria_produto' in pr.columns:
                sp_cnt=pr.groupby('id_subcategoria_produto').size().reset_index(name='qtd_produtos')
                sc=sc.merge(sp_cnt,left_on='id',right_on='id_subcategoria_produto',how='left').fillna(0)
            cols=[c for c in ['id','nome','nome_categoria','qtd_produtos','createdAt'] if c in sc.columns]
            # Filtro por categoria
            if 'nome_categoria' in sc.columns:
                cats=['Todas']+sorted(sc['nome_categoria'].dropna().unique().tolist())
                fc=st.selectbox("Filtrar por categoria:",cats,key="fc_sub")
                if fc!='Todas': sc=sc[sc['nome_categoria']==fc]
            st.dataframe(sc[cols].sort_values('nome') if 'nome' in cols else sc[cols],hide_index=True,use_container_width=True)
    with t3:
        if len(sub)>0 and len(pr)>0 and 'id_categoria_produto' in pr.columns and 'id_subcategoria_produto' in pr.columns:
            tm=pr.copy()
            if 'nome_categoria' in tm.columns and 'nome_subcategoria' in tm.columns:
                tg=tm.groupby(['nome_categoria','nome_subcategoria']).size().reset_index(name='qtd').dropna()
                if len(tg)>0:
                    fig=px.treemap(tg,path=['nome_categoria','nome_subcategoria'],values='qtd',color='qtd',color_continuous_scale='Blues',title="Distribuição de Produtos")
                    fig.update_layout(height=600); st.plotly_chart(fig,use_container_width=True)
        elif len(rq)>0 and 'nome_categoria' in rq.columns and 'nome_subcategoria' in rq.columns:
            tg=rq.groupby(['nome_categoria','nome_subcategoria']).size().reset_index(name='qtd').dropna()
            if len(tg)>0:
                fig=px.treemap(tg,path=['nome_categoria','nome_subcategoria'],values='qtd',color='qtd',color_continuous_scale='Blues',title="Distribuição de Respostas")
                fig.update_layout(height=600); st.plotly_chart(fig,use_container_width=True)
    # Insights
    ih=""
    if nc>0 and ns>0:
        avg=ns/nc
        ih+=ibox("Estratégico","Estrutura do Catálogo",f"{nc} categorias com média de {avg:.1f} subcategorias cada. {'Estrutura granular adequada.' if avg>=3 else 'Considerar criar mais subcategorias para melhor segmentação.'}")
    if len(pr)>0 and 'id_categoria_produto' in pr.columns:
        vazia=nc-pr['id_categoria_produto'].nunique()
        if vazia>0: ih+=ibox("Operacional","Categorias Vazias",f"{vazia} categorias sem produtos cadastrados. Priorizar cadastro ou remover categorias obsoletas.")
    if ih: st.markdown(ih,unsafe_allow_html=True)

# ============================================================================
# PG9: PRODUTOS
# ============================================================================
def pg_produtos(data):
    st.markdown(section_header("Produtos","Catalogo completo e analise de produtos"),unsafe_allow_html=True)
    pr=data['produto']; rq=data['resp_questionario']; rp=data['resp_pergunta']
    if len(pr)==0: st.warning("Sem dados de produtos."); return
    np_=len(pr)
    nm_=pr['id_marca'].nunique() if 'id_marca' in pr.columns else 0
    ne_=pr['id_empresa'].nunique() if 'id_empresa' in pr.columns else 0
    avaliados=rq['id_produto'].nunique() if len(rq)>0 and 'id_produto' in rq.columns else 0
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(mcard(f"{np_}","Total Produtos"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{nm_}","Marcas",c=CL['accent1']),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{ne_}","Empresas",c=CL['teal']),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{avaliados}","Avaliados",f"{spct(avaliados,np_)}%",c=CL['success']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["Catalogo","Analise","Detalhe"])
    with t1:
        df=pr.copy()
        # Filtros
        c1,c2,c3=st.columns(3)
        with c1:
            if 'nome_categoria' in df.columns:
                cats=['Todas']+sorted(df['nome_categoria'].dropna().unique().tolist())
                fc=st.selectbox("Categoria:",cats,key="fp_cat")
                if fc!='Todas': df=df[df['nome_categoria']==fc]
        with c2:
            if 'nome_marca' in df.columns:
                marcas=['Todas']+sorted(df['nome_marca'].dropna().unique().tolist())
                fm=st.selectbox("Marca:",marcas,key="fp_mar")
                if fm!='Todas': df=df[df['nome_marca']==fm]
        with c3:
            if 'nome_empresa' in df.columns:
                emps=['Todas']+sorted(df['nome_empresa'].dropna().unique().tolist())
                fe=st.selectbox("Empresa:",emps,key="fp_emp")
                if fe!='Todas': df=df[df['nome_empresa']==fe]
        cols=[c for c in ['id','nome','nome_categoria','nome_subcategoria','nome_marca','nome_empresa','createdAt'] if c in df.columns]
        st.markdown(f"**{len(df)} produtos**")
        st.dataframe(df[cols],hide_index=True,use_container_width=True,height=500)
    with t2:
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<div class="chart-title">Por Categoria</div>',unsafe_allow_html=True)
            if 'nome_categoria' in pr.columns:
                pc=pr['nome_categoria'].value_counts().head(15)
                fig=hbar(pc.values,pc.index,cs='Blues')
                fig.update_layout(height=450,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        with c2:
            st.markdown('<div class="chart-title">Por Marca</div>',unsafe_allow_html=True)
            if 'nome_marca' in pr.columns:
                pm=pr['nome_marca'].value_counts().head(15)
                fig=hbar(pm.values,pm.index,cs='Greens')
                fig.update_layout(height=450,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        if 'nome_empresa' in pr.columns:
            st.markdown('<div class="chart-title">Por Empresa</div>',unsafe_allow_html=True)
            pe=pr['nome_empresa'].value_counts().head(10)
            fig=px.pie(values=pe.values.tolist(),names=pe.index.tolist(),color_discrete_sequence=PAL,hole=.4)
            fig.update_layout(height=400); st.plotly_chart(fig,use_container_width=True)
    with t3:
        if 'nome' in pr.columns:
            sel=st.selectbox("Selecione produto:",sorted(pr['nome'].dropna().unique().tolist()),key="sp_det")
            pi=pr[pr['nome']==sel]
            if len(pi)>0:
                p=pi.iloc[0]
                c1,c2,c3,c4=st.columns(4)
                with c1: st.markdown(f'<div class="mc"><p class="ml">Categoria</p><p style="font-weight:600">{p.get("nome_categoria","N/A")}</p></div>',unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="mc"><p class="ml">Subcategoria</p><p style="font-weight:600">{p.get("nome_subcategoria","N/A")}</p></div>',unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="mc"><p class="ml">Marca</p><p style="font-weight:600">{p.get("nome_marca","N/A")}</p></div>',unsafe_allow_html=True)
                with c4: st.markdown(f'<div class="mc"><p class="ml">Empresa</p><p style="font-weight:600">{p.get("nome_empresa","N/A")}</p></div>',unsafe_allow_html=True)
                # Respostas deste produto
                pid=p.get('id')
                if pid and len(rp)>0 and 'id_produto' in rp.columns:
                    rpr=rp[rp['id_produto']==pid]
                    st.markdown(f'<div class="chart-title">{len(rpr)} respostas para este produto</div>',unsafe_allow_html=True)
                    if len(rpr)>0 and 'titulo_pergunta' in rpr.columns and 'resposta' in rpr.columns:
                        # Perfil sensorial
                        pergs=rpr.groupby('titulo_pergunta').apply(lambda x: pd.to_numeric(x['resposta'].str.replace('"',''),errors='coerce').mean()).dropna()
                        if len(pergs)>=3:
                            st.markdown('<div class="chart-title">Perfil Sensorial</div>',unsafe_allow_html=True)
                            fig=go.Figure(go.Scatterpolar(r=pergs.values,theta=pergs.index.tolist(),fill='toself',line_color=CL['primary']))
                            fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,9])),height=400,showlegend=False)
                            st.plotly_chart(fig,use_container_width=True)
    # Insights
    ih=""
    if avaliados>0:
        cob=spct(avaliados,np_)
        ih+=ibox("Estratégico","Cobertura de Avaliação",f"{avaliados}/{np_} produtos avaliados ({cob}%). {'Excelente cobertura!' if cob>60 else 'Oportunidade: criar pesquisas para produtos sem avaliação.'}")
    if 'nome_marca' in pr.columns:
        top_m=pr['nome_marca'].value_counts().index[0] if len(pr['nome_marca'].dropna())>0 else 'N/A'
        ih+=ibox("Tático","Marca Dominante",f"'{top_m}' é a marca com mais produtos cadastrados ({pr['nome_marca'].value_counts().iloc[0]}). Diversificar portfólio de marcas pode ampliar escopo de pesquisa.")
    if ih: st.markdown(ih,unsafe_allow_html=True)

# ============================================================================
# PG10: MARCAS
# ============================================================================
def pg_marcas(data):
    st.markdown(section_header("Marcas","Analise de marcas e distribuicao por produtos"),unsafe_allow_html=True)
    ma=data['marca']; pr=data['produto']
    if len(ma)==0: st.warning("Sem dados de marcas."); return
    nm=len(ma)
    c1,c2,c3=st.columns(3)
    with c1: st.markdown(mcard(f"{nm}","Total Marcas"),unsafe_allow_html=True)
    with c2:
        com_prod=pr['id_marca'].nunique() if len(pr)>0 and 'id_marca' in pr.columns else 0
        st.markdown(mcard(f"{com_prod}","Com Produtos",c=CL['success']),unsafe_allow_html=True)
    with c3:
        sem=nm-com_prod
        st.markdown(mcard(f"{sem}","Sem Produtos",c=CL['warning']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    t1,t2=st.tabs(["Lista","Analise"])
    with t1:
        df=ma.copy()
        if len(pr)>0 and 'id_marca' in pr.columns:
            pcnt=pr.groupby('id_marca').size().reset_index(name='qtd_produtos')
            df=df.merge(pcnt,left_on='id',right_on='id_marca',how='left',suffixes=('','_p')).fillna(0)
        cols=[c for c in ['id','nome','qtd_produtos','createdAt'] if c in df.columns]
        if 'qtd_produtos' in df.columns: df=df.sort_values('qtd_produtos',ascending=False)
        st.dataframe(df[cols],hide_index=True,use_container_width=True)
    with t2:
        if len(pr)>0 and 'nome_marca' in pr.columns:
            mc_=pr['nome_marca'].value_counts().head(20)
            fig=hbar(mc_.values,mc_.index,cs='Blues',title="Top 20 Marcas por Nº de Produtos")
            fig.update_layout(height=500,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True)
            # Por empresa
            if 'nome_empresa' in pr.columns:
                st.markdown('<div class="chart-title">Marcas por Empresa</div>',unsafe_allow_html=True)
                me=pr.groupby(['nome_empresa','nome_marca']).size().reset_index(name='qtd').sort_values('qtd',ascending=False).head(30)
                fig=px.bar(me,x='qtd',y='nome_marca',color='nome_empresa',orientation='h',color_discrete_sequence=PAL)
                fig.update_layout(height=500,yaxis_title=""); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)

# ============================================================================
# PG11: PARCEIROS
# ============================================================================
def pg_parceiros(data):
    st.markdown(section_header("Parceiros","Rede de parceiros e vinculos de produtos"),unsafe_allow_html=True)
    pa=data['parceiro']; pp=data['produto_parceiro']; pr=data['produto']
    if len(pa)==0: st.warning("Sem dados de parceiros."); return
    np_=len(pa)
    c1,c2,c3=st.columns(3)
    with c1: st.markdown(mcard(f"{np_}","Total Parceiros"),unsafe_allow_html=True)
    with c2:
        nl=len(pp) if len(pp)>0 else 0
        st.markdown(mcard(f"{nl}","Links Produto-Parceiro",c=CL['accent1']),unsafe_allow_html=True)
    with c3:
        prod_vinc=pp['id_produto'].nunique() if len(pp)>0 and 'id_produto' in pp.columns else 0
        st.markdown(mcard(f"{prod_vinc}","Produtos Vinculados",c=CL['purple']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    t1,t2=st.tabs(["Lista","Vinculos"])
    with t1:
        cols=[c for c in ['id','nome','url','createdAt'] if c in pa.columns]
        st.dataframe(pa[cols],hide_index=True,use_container_width=True)
    with t2:
        if len(pp)>0:
            vn=pp.copy()
            if 'id_parceiro' in vn.columns:
                pd_=data['dicts'].get('parceiro',{})
                vn['nome_parceiro']=vn['id_parceiro'].map(pd_)
            if 'id_produto' in vn.columns:
                prd=data['dicts'].get('produto',{})
                vn['nome_produto']=vn['id_produto'].map(prd)
            cols=[c for c in ['id','nome_parceiro','nome_produto','url','preco','createdAt'] if c in vn.columns]
            st.dataframe(vn[cols],hide_index=True,use_container_width=True)
            # Gráfico parceiros com mais produtos
            if 'nome_parceiro' in vn.columns:
                pc=vn['nome_parceiro'].value_counts()
                fig=hbar(pc.values,pc.index,cs='Greens',title="Produtos por Parceiro")
                fig.update_layout(height=400,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        else: st.info("Sem vínculos produto-parceiro cadastrados.")
    ih=ibox("Operacional","Rede de Parceiros",f"{np_} parceiros ativos com {nl} vínculos de produtos. {'Rede bem estruturada.' if nl>np_*2 else 'Ampliar vínculos com parceiros existentes.'}")
    st.markdown(ih,unsafe_allow_html=True)

# ============================================================================
# PG12: GESTÃO DE PESQUISAS
# ============================================================================
def pg_pesquisas(data):
    st.markdown(section_header("Gestao de Pesquisas","Instrumentos de coleta, sessoes e perguntas"),unsafe_allow_html=True)
    pp=data['pesq_produto']; ps=data['pesq_subcategoria']; se=data['sessao']; pg_=data['pergunta']
    rq=data['resp_questionario']
    npp=len(pp); nps=len(ps); nse=len(se); npg=len(pg_)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(mcard(f"{npp}","Pesq. Produto"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{nps}","Pesq. Subcategoria",c=CL['accent1']),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{nse}","Sessões",c=CL['teal']),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{npg}","Perguntas",c=CL['purple']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    t1,t2,t3,t4=st.tabs(["Por Produto","Por Subcategoria","Sessoes","Perguntas"])
    with t1:
        if len(pp)>0:
            df=pp.copy()
            if 'id_produto' in df.columns: df['nome_produto']=df['id_produto'].map(data['dicts'].get('produto',{}))
            cols=[c for c in ['id','nome_produto','titulo','descricao','ativa','createdAt'] if c in df.columns]
            if 'ativa' in df.columns:
                ac=df['ativa'].astype(str).str.lower().isin(['true','1','t']).sum()
                st.markdown(f"**{ac} ativas** de {len(df)} pesquisas de produto")
            st.dataframe(df[cols],hide_index=True,use_container_width=True)
        else: st.info("Sem pesquisas de produto.")
    with t2:
        if len(ps)>0:
            df=ps.copy()
            if 'id_subcategoria_produto' in df.columns: df['nome_subcategoria']=df['id_subcategoria_produto'].map(data['dicts'].get('subcategoria',{}))
            cols=[c for c in ['id','nome_subcategoria','titulo','descricao','ativa','createdAt'] if c in df.columns]
            st.dataframe(df[cols],hide_index=True,use_container_width=True)
        else: st.info("Sem pesquisas de subcategoria.")
    with t3:
        if len(se)>0:
            df=se.copy()
            cols=[c for c in ['id','titulo','descricao','ordem','createdAt'] if c in df.columns]
            st.dataframe(df[cols],hide_index=True,use_container_width=True)
            if 'id_pesquisa_produto' in se.columns:
                sc=se.groupby('id_pesquisa_produto').size().reset_index(name='qtd_sessoes')
                st.markdown('<div class="chart-title">Sessoes por Pesquisa</div>',unsafe_allow_html=True)
                fig=px.bar(sc.head(20),x='id_pesquisa_produto',y='qtd_sessoes',color='qtd_sessoes',color_continuous_scale='Blues')
                fig.update_layout(height=350,coloraxis_showscale=False); st.plotly_chart(fig,use_container_width=True)
        else: st.info("Sem sessões.")
    with t4:
        if len(pg_)>0:
            df=pg_.copy()
            cols=[c for c in ['id','titulo','tipo','obrigatoria','ordem','createdAt'] if c in df.columns]
            st.dataframe(df[cols],hide_index=True,use_container_width=True)
            # Distribuição por tipo
            if 'tipo' in df.columns:
                c1,c2=st.columns(2)
                with c1:
                    tc=df['tipo'].value_counts()
                    fig=px.pie(values=tc.values.tolist(),names=tc.index.tolist(),color_discrete_sequence=PAL,hole=.4,title="Tipos de Pergunta")
                    fig.update_layout(height=350); st.plotly_chart(fig,use_container_width=True)
                with c2:
                    ob=df['obrigatoria'].astype(str).str.lower().isin(['true','1','t']).sum() if 'obrigatoria' in df.columns else 0
                    st.markdown(mcard(f"{ob}/{len(df)}","Obrigatórias",f"{spct(ob,len(df))}%",c=CL['orange']),unsafe_allow_html=True)
                    if 'id_sessao_pesquisa' in df.columns:
                        ps_=df.groupby('id_sessao_pesquisa').size().reset_index(name='qtd')
                        st.markdown(f"**Média: {ps_['qtd'].mean():.1f} perguntas/sessão**")
        else: st.info("Sem perguntas.")
    # Insights
    ih=""
    if npp+nps>0:
        ih+=ibox("Estratégico","Cobertura de Pesquisas",f"{npp} pesquisas de produto + {nps} de subcategoria = {npp+nps} instrumentos de coleta. {npg} perguntas cadastradas em {nse} sessões.")
    if len(rq)>0 and len(pp)>0 and 'id_pesquisa_produto' in pp.columns:
        ih+=ibox("Tático","Engajamento",f"{len(rq):,} questionários respondidos. Média de {len(rq)/max(npp,1):.0f} respostas por pesquisa de produto.")
    if ih: st.markdown(ih,unsafe_allow_html=True)

# ============================================================================
# PG13: BENEFÍCIOS & RESGATES
# ============================================================================
def pg_beneficios(data):
    st.markdown(section_header("Beneficios & Resgates","Programa de recompensas e economia de pontos"),unsafe_allow_html=True)
    bn=data['beneficio']; rg=data['resgate']; pt=data['pontos']
    nb=len(bn); nr=len(rg)
    pts_total=0
    if len(pt)>0 and 'pontos' in pt.columns: pts_total=int(pd.to_numeric(pt['pontos'],errors='coerce').fillna(0).sum())
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(mcard(f"{nb}","Benefícios"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{nr}","Resgates",c=CL['accent1']),unsafe_allow_html=True)
    with c3:
        usr_r=rg['id_usuario'].nunique() if len(rg)>0 and 'id_usuario' in rg.columns else 0
        st.markdown(mcard(f"{usr_r}","Usuários Resgataram",c=CL['teal']),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{pts_total:,}","Pontos Distribuídos",c=CL['orange']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["Catalogo","Resgates","Dashboard"])
    with t1:
        if len(bn)>0:
            cols=[c for c in ['id','nome','descricao','pontos_necessarios','quantidade','ativo','createdAt'] if c in bn.columns]
            df=bn.copy()
            if 'ativo' in df.columns:
                ac=df['ativo'].astype(str).str.lower().isin(['true','1','t']).sum()
                st.markdown(f"**{ac} ativos** de {nb} benefícios")
            st.dataframe(df[cols],hide_index=True,use_container_width=True)
            if 'pontos_necessarios' in bn.columns:
                pn=pd.to_numeric(bn['pontos_necessarios'],errors='coerce').dropna()
                if len(pn)>0:
                    st.markdown(f"**Pontos necessários:** Mín {pn.min():.0f} | Méd {pn.mean():.0f} | Máx {pn.max():.0f}")
        else: st.info("Sem benefícios cadastrados.")
    with t2:
        if len(rg)>0:
            c1,c2=st.columns(2)
            with c1:
                if 'nome_beneficio' in rg.columns:
                    st.markdown('<div class="chart-title">Top Beneficios Resgatados</div>',unsafe_allow_html=True)
                    bc=rg['nome_beneficio'].value_counts().head(10)
                    fig=hbar(bc.values,bc.index,cs='Blues')
                    fig.update_layout(height=400,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                    st.plotly_chart(fig,use_container_width=True)
            with c2:
                if 'nome_usuario' in rg.columns:
                    st.markdown('<div class="chart-title">Top Usuarios que Resgataram</div>',unsafe_allow_html=True)
                    uc=rg['nome_usuario'].value_counts().head(10)
                    fig=hbar(uc.values,uc.index,cs='Greens')
                    fig.update_layout(height=400,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                    st.plotly_chart(fig,use_container_width=True)
            # Tabela
            cols=[c for c in ['id','nome_usuario','nome_beneficio','status','createdAt'] if c in rg.columns]
            if 'createdAt' in rg.columns:
                st.dataframe(rg[cols].sort_values('createdAt',ascending=False).head(100),hide_index=True,use_container_width=True)
            else: st.dataframe(rg[cols].head(100),hide_index=True,use_container_width=True)
        else: st.info("Sem resgates registrados.")
    with t3:
        if len(rg)>0 and 'createdAt' in rg.columns:
            st.markdown('<div class="chart-title">Evolucao de Resgates</div>',unsafe_allow_html=True)
            ev=rg.groupby(rg['createdAt'].dt.date).size().reset_index(name='qtd'); ev.columns=['data','qtd']
            ev['data']=pd.to_datetime(ev['data'])
            fig=px.area(ev,x='data',y='qtd',color_discrete_sequence=[CL['primary']])
            fig.update_layout(height=350); st.plotly_chart(fig,use_container_width=True)
            # Por mês
            ev_m=rg.groupby(rg['createdAt'].dt.to_period('M')).size().reset_index(name='qtd')
            ev_m.columns=['mes','qtd']; ev_m['mes']=ev_m['mes'].astype(str)
            fig=px.bar(ev_m,x='mes',y='qtd',color='qtd',color_continuous_scale='Blues',title="Resgates por Mês")
            fig.update_layout(height=350,coloraxis_showscale=False); st.plotly_chart(fig,use_container_width=True)
        if len(pt)>0:
            st.markdown('<div class="chart-title">Distribuicao de Pontos</div>',unsafe_allow_html=True)
            if 'pontos' in pt.columns:
                pv=pd.to_numeric(pt['pontos'],errors='coerce').dropna()
                fig=px.histogram(x=pv,nbins=30,color_discrete_sequence=[CL['orange']],title="Distribuição de Pontos por Transação")
                fig.update_layout(height=350); st.plotly_chart(fig,use_container_width=True)
    # Insights
    ih=""
    if nr>0 and len(data['usuario'])>0:
        tx=spct(usr_r,len(data['usuario']))
        ih+=ibox("Estratégico","Taxa de Resgate",f"{tx}% dos testadores já resgataram benefícios ({usr_r} de {len(data['usuario']):,}). {'Boa adesão!' if tx>20 else 'Oportunidade: divulgar mais os benefícios para aumentar engajamento.'}")
    if nr>0 and 'nome_beneficio' in rg.columns:
        top=rg['nome_beneficio'].value_counts().index[0]
        ih+=ibox("Tático","Benefício Preferido",f"'{top}' é o mais resgatado ({rg['nome_beneficio'].value_counts().iloc[0]}x). Considerar ampliar estoque/variações deste tipo.")
    if pts_total>0:
        ih+=ibox("Operacional","Economia de Pontos",f"{pts_total:,} pontos distribuídos na plataforma. Monitorar inflação de pontos vs benefícios disponíveis.")
    if ih: st.markdown(ih,unsafe_allow_html=True)

# ============================================================================
# PG14: EMPRESAS
# ============================================================================
def pg_empresas(data):
    st.markdown(section_header("Empresas","Base empresarial e vinculos de produtos"),unsafe_allow_html=True)
    em=data['empresa']; ue=data['usr_empresa']; ge=data['grupo_empresa']; pr=data['produto']
    ne=len(em)
    if ne==0: st.warning("Sem dados de empresas."); return
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(mcard(f"{ne}","Total Empresas"),unsafe_allow_html=True)
    with c2:
        nu=len(ue) if len(ue)>0 else 0
        st.markdown(mcard(f"{nu}","Vínculos Usr-Empresa",c=CL['accent1']),unsafe_allow_html=True)
    with c3:
        ng=len(ge) if len(ge)>0 else 0
        st.markdown(mcard(f"{ng}","Grupos",c=CL['teal']),unsafe_allow_html=True)
    with c4:
        np_=pr['id_empresa'].nunique() if len(pr)>0 and 'id_empresa' in pr.columns else 0
        st.markdown(mcard(f"{np_}","Com Produtos",c=CL['purple']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["Lista","Analise","Usuarios"])
    with t1:
        df=em.copy()
        # Contar produtos por empresa
        if len(pr)>0 and 'id_empresa' in pr.columns:
            pc=pr.groupby('id_empresa').size().reset_index(name='qtd_produtos')
            df=df.merge(pc,left_on='id',right_on='id_empresa',how='left',suffixes=('','_p')).fillna(0)
        # Contar usuários por empresa
        if len(ue)>0 and 'id_empresa' in ue.columns:
            uc=ue.groupby('id_empresa').size().reset_index(name='qtd_usuarios')
            df=df.merge(uc,left_on='id',right_on='id_empresa',how='left',suffixes=('','_u')).fillna(0)
        cols=[c for c in ['id','nome_fantasia','razao_social','cnpj','nome_cidade','qtd_produtos','qtd_usuarios','createdAt'] if c in df.columns]
        st.dataframe(df[cols],hide_index=True,use_container_width=True)
    with t2:
        c1,c2=st.columns(2)
        with c1:
            if len(pr)>0 and 'nome_empresa' in pr.columns:
                st.markdown('<div class="chart-title">Produtos por Empresa</div>',unsafe_allow_html=True)
                ec=pr['nome_empresa'].value_counts().head(15)
                fig=hbar(ec.values,ec.index,cs='Blues')
                fig.update_layout(height=450,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        with c2:
            if len(pr)>0 and 'nome_empresa' in pr.columns and 'nome_categoria' in pr.columns:
                st.markdown('<div class="chart-title">Categorias por Empresa</div>',unsafe_allow_html=True)
                ec2=pr.groupby(['nome_empresa','nome_categoria']).size().reset_index(name='qtd')
                top_e=pr['nome_empresa'].value_counts().head(8).index
                ec2=ec2[ec2['nome_empresa'].isin(top_e)]
                if len(ec2)>0:
                    fig=px.bar(ec2,x='qtd',y='nome_empresa',color='nome_categoria',orientation='h',color_discrete_sequence=PAL)
                    fig.update_layout(height=400,yaxis_title=""); fig.update_yaxes(autorange="reversed")
                    st.plotly_chart(fig,use_container_width=True)
    with t3:
        if len(ue)>0:
            df=ue.copy()
            if 'id_empresa' in df.columns: df['nome_empresa']=df['id_empresa'].map(data['dicts'].get('empresa',{}))
            if 'id_usuario' in df.columns: df['nome_usuario']=df['id_usuario'].map(data['dicts'].get('usuario',{}))
            cols=[c for c in ['id','nome_empresa','nome_usuario','papel','createdAt'] if c in df.columns]
            # Filtro
            if 'nome_empresa' in df.columns:
                emps=['Todas']+sorted(df['nome_empresa'].dropna().unique().tolist())
                fe=st.selectbox("Filtrar empresa:",emps,key="fe_ue")
                if fe!='Todas': df=df[df['nome_empresa']==fe]
            st.dataframe(df[cols],hide_index=True,use_container_width=True)
        else: st.info("Sem vínculos usuário-empresa.")
    # Insights
    ih=""
    sem_prod=ne-np_
    if sem_prod>0: ih+=ibox("Operacional","Empresas sem Produtos",f"{sem_prod} empresas cadastradas sem produtos vinculados. Verificar se há cadastros pendentes ou empresas inativas.")
    if ne>0: ih+=ibox("Estratégico","Base Empresarial",f"{ne} empresas na plataforma. {'Boa diversidade.' if ne>10 else 'Expandir base de clientes corporativos.'}")
    if ih: st.markdown(ih,unsafe_allow_html=True)

# ============================================================================
# PG15: BANNERS & RECOMENDADOS
# ============================================================================
def pg_banners(data):
    st.markdown(section_header("Banners & Recomendados","Gestao de banners da home e produtos em destaque"),unsafe_allow_html=True)
    bh=data['banner_home']; pr=data['prod_recomendado']
    nb=len(bh); nrec=len(pr)
    c1,c2=st.columns(2)
    with c1: st.markdown(mcard(f"{nb}","Banners Home"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{nrec}","Prod. Recomendados",c=CL['accent1']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    t1,t2=st.tabs(["Banners","Recomendados"])
    with t1:
        if len(bh)>0:
            cols=[c for c in ['id','titulo','descricao','url_imagem','ativo','ordem','createdAt'] if c in bh.columns]
            df=bh.copy()
            if 'ativo' in df.columns:
                ac=df['ativo'].astype(str).str.lower().isin(['true','1','t']).sum()
                st.markdown(f"**{ac} ativos** de {nb} banners")
            st.dataframe(df[cols],hide_index=True,use_container_width=True)
        else: st.info("Sem banners cadastrados.")
    with t2:
        if len(pr)>0:
            df=pr.copy()
            if 'id_produto' in df.columns: df['nome_produto']=df['id_produto'].map(data['dicts'].get('produto',{}))
            cols=[c for c in ['id','nome_produto','ordem','ativo','createdAt'] if c in df.columns]
            st.dataframe(df[cols],hide_index=True,use_container_width=True)
            if 'nome_produto' in df.columns:
                fig=px.bar(df['nome_produto'].value_counts().head(15),orientation='h',color_discrete_sequence=[CL['primary']])
                fig.update_layout(height=350,yaxis_title="",showlegend=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        else: st.info("Sem produtos recomendados.")

# ============================================================================
# PG16: GESTÃO DE TESTADORES
# ============================================================================
def pg_testadores(data):
    st.markdown(section_header("Gestao de Testadores","Base completa, geografia, evolucao e cohorts"),unsafe_allow_html=True)
    us=data['usuario']; rq=data['resp_questionario']; rg=data['resgate']
    if len(us)==0: st.warning("Sem dados."); return
    nu=len(us)
    # Cadastro completo
    cc=0
    if 'is_cadastro_completo' in us.columns:
        cv=us['is_cadastro_completo'].fillna(False)
        if cv.dtype=='object': cv=cv.astype(str).str.lower().map({'true':True,'false':False,'1':True,'0':False,'nan':False}).fillna(False)
        cc=int(cv.sum())
    # Ativos (responderam algo)
    ativos=rq['id_usuario'].nunique() if len(rq)>0 and 'id_usuario' in rq.columns else 0
    # Com resgate
    resg=rg['id_usuario'].nunique() if len(rg)>0 and 'id_usuario' in rg.columns else 0
    c1,c2,c3,c4,c5=st.columns(5)
    with c1: st.markdown(mcard(f"{nu:,}","Total"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{cc:,}","Cad. Completos",f"{spct(cc,nu)}%",c=CL['success']),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{ativos:,}","Ativos",f"{spct(ativos,nu)}%",c=CL['accent1']),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{nu-ativos:,}","Inativos",c=CL['warning']),unsafe_allow_html=True)
    with c5: st.markdown(mcard(f"{resg:,}","Resgataram",f"{spct(resg,nu)}%",c=CL['orange']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    t1,t2,t3,t4=st.tabs(["Base","Geografia","Evolucao","Cohorts"])
    with t1:
        df=us.copy()
        c1,c2,c3=st.columns(3)
        with c1:
            if 'genero' in df.columns:
                gens=['Todos']+df['genero'].dropna().unique().tolist()
                fg=st.selectbox("Gênero:",gens,key="ft_gen")
                if fg!='Todos': df=df[df['genero']==fg]
        with c2:
            if 'nome_estado' in df.columns:
                ests=['Todos']+sorted(df['nome_estado'].dropna().unique().tolist())
                fe=st.selectbox("Estado:",ests,key="ft_est")
                if fe!='Todos': df=df[df['nome_estado']==fe]
        with c3:
            fc=st.selectbox("Cadastro:",['Todos','Completo','Incompleto'],key="ft_cad")
            if fc=='Completo' and 'is_cadastro_completo' in df.columns:
                df=df[df['is_cadastro_completo'].astype(str).str.lower().isin(['true','1','t'])]
            elif fc=='Incompleto' and 'is_cadastro_completo' in df.columns:
                df=df[~df['is_cadastro_completo'].astype(str).str.lower().isin(['true','1','t'])]
        cols=[c for c in ['id','nome','email','genero','idade','nome_cidade','nome_estado','is_cadastro_completo','createdAt'] if c in df.columns]
        st.markdown(f"**{len(df):,} testadores**")
        st.dataframe(df[cols].head(500),hide_index=True,use_container_width=True,height=500)
    with t2:
        c1,c2=st.columns(2)
        with c1:
            if 'nome_estado' in us.columns:
                st.markdown('<div class="chart-title">Por Estado</div>',unsafe_allow_html=True)
                ec=us['nome_estado'].value_counts().head(15)
                fig=hbar(ec.values,ec.index,cs='Blues')
                fig.update_layout(height=450,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        with c2:
            if 'nome_cidade' in us.columns:
                st.markdown('<div class="chart-title">Top 15 Cidades</div>',unsafe_allow_html=True)
                cc_=us['nome_cidade'].value_counts().head(15)
                fig=hbar(cc_.values,cc_.index,cs='Greens')
                fig.update_layout(height=450,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        # Mapa de calor estado x gênero
        if 'nome_estado' in us.columns and 'genero' in us.columns:
            st.markdown('<div class="chart-title">Heatmap Estado x Genero</div>',unsafe_allow_html=True)
            hm=us.groupby(['nome_estado','genero']).size().reset_index(name='qtd')
            hm_p=hm.pivot_table(index='nome_estado',columns='genero',values='qtd',fill_value=0)
            top_est=us['nome_estado'].value_counts().head(15).index
            hm_p=hm_p[hm_p.index.isin(top_est)]
            if len(hm_p)>0:
                fig=px.imshow(hm_p,color_continuous_scale='Blues',aspect='auto')
                fig.update_layout(height=400); st.plotly_chart(fig,use_container_width=True)
    with t3:
        if 'createdAt' in us.columns:
            st.markdown('<div class="chart-title">Cadastros ao Longo do Tempo</div>',unsafe_allow_html=True)
            ev=us.groupby(us['createdAt'].dt.to_period('M')).size().reset_index(name='novos')
            ev.columns=['mes','novos']; ev['mes']=ev['mes'].astype(str); ev['acum']=ev['novos'].cumsum()
            c1,c2=st.columns(2)
            with c1:
                fig=px.bar(ev,x='mes',y='novos',color='novos',color_continuous_scale='Blues',title="Novos Cadastros/Mês")
                fig.update_layout(height=350,coloraxis_showscale=False,xaxis_tickangle=45); st.plotly_chart(fig,use_container_width=True)
            with c2:
                fig=px.area(ev,x='mes',y='acum',color_discrete_sequence=[CL['success']],title="Acumulado")
                fig.update_layout(height=350,xaxis_tickangle=45); st.plotly_chart(fig,use_container_width=True)
    with t4:
        if len(rq)>0 and 'id_usuario' in rq.columns:
            st.markdown('<div class="chart-title">Cohorts de Engajamento</div>',unsafe_allow_html=True)
            uc=rq.groupby('id_usuario').size().reset_index(name='qtd')
            uc['cohort']=pd.cut(uc['qtd'],bins=[0,1,5,10,25,50,1000],labels=['1','2-5','6-10','11-25','26-50','50+'])
            cc_=uc['cohort'].value_counts().sort_index()
            fig=px.bar(x=cc_.index.astype(str).tolist(),y=cc_.values.tolist(),color=cc_.values.tolist(),color_continuous_scale='Blues',
                labels={'x':'Questionários Respondidos','y':'Nº Testadores'},title="Segmentação por Atividade")
            fig.update_layout(height=400,coloraxis_showscale=False); st.plotly_chart(fig,use_container_width=True)
            # Métricas por cohort
            st.dataframe(pd.DataFrame({'Cohort':cc_.index.astype(str),'Testadores':cc_.values.tolist(),'%':[(spct(v,len(uc))) for v in cc_.values]}),hide_index=True)
    # Insights
    ih=""
    ih+=ibox("Estratégico","Saúde da Base",f"{nu:,} testadores. {spct(ativos,nu)}% ativos, {spct(cc,nu)}% com cadastro completo. {'Base engajada.' if spct(ativos,nu)>30 else 'Foco em ativação: campanhas de primeiro acesso.'}")
    if 'nome_estado' in us.columns:
        top_e=us['nome_estado'].value_counts()
        if len(top_e)>0:
            conc=spct(top_e.iloc[0],nu)
            ih+=ibox("Tático","Concentração Geográfica",f"{top_e.index[0]} concentra {conc}% da base. {'Diversificar recrutamento regional.' if conc>40 else 'Boa distribuição geográfica.'}")
    ih+=ibox("Operacional","Cadastros Incompletos",f"{nu-cc:,} testadores com cadastro incompleto ({spct(nu-cc,nu)}%). Campanha de incentivo pode converter estes perfis.")
    st.markdown(ih,unsafe_allow_html=True)

# ============================================================================
# PG17: CENTRAL DE INSIGHTS
# ============================================================================
def pg_insights(data):
    st.markdown(section_header("Central de Insights","Visao consolidada de insights estrategicos, taticos e operacionais"),unsafe_allow_html=True)
    us=data['usuario']; pr=data['produto']; rq=data['resp_questionario']; rp=data['resp_pergunta']
    rg=data['resgate']; ca=data['campanha']; em=data['empresa']; bn=data['beneficio']
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    nu=len(us); np_=len(pr); nq=len(rq); nr=len(rp); ne=len(em)
    # Score geral
    scores=[]
    # Ativação
    if nu>0 and nq>0 and 'id_usuario' in rq.columns:
        tx_at=spct(rq['id_usuario'].nunique(),nu); scores.append(min(tx_at*2,100))
    # Cadastro completo
    cc=0
    if 'is_cadastro_completo' in us.columns:
        cv=us['is_cadastro_completo'].fillna(False)
        if cv.dtype=='object': cv=cv.astype(str).str.lower().map({'true':True,'false':False,'1':True,'0':False,'nan':False}).fillna(False)
        cc=int(cv.sum()); scores.append(spct(cc,nu) if nu>0 else 0)
    # Cobertura produtos
    if np_>0 and nq>0 and 'id_produto' in rq.columns:
        cob=spct(rq['id_produto'].nunique(),np_); scores.append(cob)
    score_geral=np.mean(scores) if scores else 0
    c1,c2,c3=st.columns([1,1,2])
    with c1: st.plotly_chart(gauge(score_geral,"Score Geral",100),use_container_width=True)
    with c2:
        st.markdown(mcard(f"{nu:,}","Testadores"),unsafe_allow_html=True)
        st.markdown(mcard(f"{np_}","Produtos",c=CL['purple']),unsafe_allow_html=True)
        st.markdown(mcard(f"{nq:,}","Questionários",c=CL['accent1']),unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="chart-title">Indicadores-Chave</div>',unsafe_allow_html=True)
        kpis=[]
        if nu>0 and nq>0 and 'id_usuario' in rq.columns: kpis.append(f"• Taxa de ativação: **{spct(rq['id_usuario'].nunique(),nu)}%**")
        if nu>0: kpis.append(f"• Cadastros completos: **{spct(cc,nu)}%**")
        if np_>0 and nq>0 and 'id_produto' in rq.columns: kpis.append(f"• Cobertura de produtos: **{spct(rq['id_produto'].nunique(),np_)}%**")
        if len(rg)>0 and 'id_usuario' in rg.columns: kpis.append(f"• Taxa de resgate: **{spct(rg['id_usuario'].nunique(),nu)}%**")
        kpis.append(f"• Empresas: **{ne}** | Campanhas: **{len(ca)}**")
        st.markdown("\n".join(kpis))
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    # Todos os insights
    st.markdown('<div class="chart-title" style="font-size:1.1rem">Insights Estrategicos</div>',unsafe_allow_html=True)
    ih=""
    # 1. Engajamento
    if nq>0 and 'createdAt' in rq.columns:
        wk=rq.groupby(rq['createdAt'].dt.to_period('W')).size()
        if len(wk)>=2:
            l,p=wk.iloc[-1],wk.iloc[-2]; ch=spct(l-p,p) if p>0 else 0
            ih+=ibox("Estratégico","Tendência de Engajamento",f"Última semana: {l} questionários ({'↑' if ch>0 else '↓'} {abs(ch)}% vs anterior). {'Momentum positivo.' if ch>0 else 'Queda — reengajamento necessário.'}")
    # 2. Base
    if nu>0:
        ih+=ibox("Estratégico","Saúde da Base de Testadores",f"{nu:,} testadores | {spct(cc,nu)}% cadastro completo | {spct(rq['id_usuario'].nunique() if len(rq)>0 and 'id_usuario' in rq.columns else 0,nu)}% ativos. {'Base saudável.' if spct(cc,nu)>60 else 'Priorizar completude de cadastros.'}")
    # 3. Produtos
    if np_>0 and nq>0 and 'id_produto' in rq.columns:
        av=rq['id_produto'].nunique(); cob=spct(av,np_)
        ih+=ibox("Estratégico","Cobertura de Avaliação",f"{av}/{np_} produtos avaliados ({cob}%). {'Excelente!' if cob>60 else 'Criar pesquisas para produtos sem avaliação.'}")
    # 4. Demográfico
    if 'genero' in us.columns and len(us['genero'].dropna())>0:
        gc=us['genero'].value_counts(); fem=gc.get('Feminino',0)
        ih+=ibox("Estratégico","Perfil Demográfico",f"Base {spct(fem,nu)}% feminina. {'Equilibrada.' if abs(spct(fem,nu)-50)<20 else 'Diversificar recrutamento.'}")
    if ih: st.markdown(ih,unsafe_allow_html=True)
    st.markdown('<div class="chart-title" style="font-size:1.1rem">Insights Taticos</div>',unsafe_allow_html=True)
    ih=""
    # 5. Benefícios
    if len(rg)>0 and 'id_usuario' in rg.columns:
        tx=spct(rg['id_usuario'].nunique(),nu)
        ih+=ibox("Tático","Programa de Benefícios",f"{tx}% dos testadores resgataram. {'Boa adesão.' if tx>20 else 'Ampliar divulgação do programa.'}")
    # 6. Campanhas
    if len(ca)>0 and 'data_fim' in ca.columns:
        hoje=pd.Timestamp.now(tz='UTC'); at_c=len(ca[ca['data_fim']>=hoje])
        ih+=ibox("Tático","Campanhas",f"{at_c} campanhas ativas de {len(ca)} total. {'Pipeline ativo.' if at_c>0 else 'Criar novas campanhas para manter engajamento.'}")
    # 7. Geografia
    if 'nome_estado' in us.columns:
        top_e=us['nome_estado'].value_counts()
        if len(top_e)>0:
            conc=spct(top_e.iloc[0],nu)
            ih+=ibox("Tático","Concentração Geográfica",f"{top_e.index[0]} = {conc}% da base. {top_e.head(3).index.tolist()} são os top 3 estados.")
    if ih: st.markdown(ih,unsafe_allow_html=True)
    st.markdown('<div class="chart-title" style="font-size:1.1rem">Insights Operacionais</div>',unsafe_allow_html=True)
    ih=""
    # 8. Cadastro
    inc=nu-cc
    if inc>0: ih+=ibox("Operacional","Cadastros Incompletos",f"{inc:,} testadores ({spct(inc,nu)}%) com cadastro incompleto. Campanha de incentivo pode converter.")
    # 9. Empresas
    if ne>0 and len(pr)>0 and 'id_empresa' in pr.columns:
        emp_prod=pr['id_empresa'].nunique(); sem=ne-emp_prod
        if sem>0: ih+=ibox("Operacional","Empresas sem Produtos",f"{sem} empresas sem produtos. Verificar cadastros pendentes.")
    # 10. Produtos não cadastrados
    pnc=data['prod_nao_cadastrado']
    if len(pnc)>0: ih+=ibox("Operacional","Produtos Não Cadastrados",f"{len(pnc)} produtos reportados como não cadastrados. Oportunidade de expandir catálogo.")
    # 11. Notificações
    nt=data['notificacoes']
    if len(nt)>0: ih+=ibox("Operacional","Notificações",f"{len(nt)} notificações enviadas no sistema. Verificar efetividade de entrega.")
    if ih: st.markdown(ih,unsafe_allow_html=True)
    # Resumo final
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    st.markdown('<div class="chart-title" style="font-size:1.1rem">Resumo Executivo</div>',unsafe_allow_html=True)
    st.markdown(f"""
A plataforma Foodtest conta com **{nu:,} testadores**, **{np_} produtos** cadastrados em **{len(data['categoria'])} categorias**,
atendendo **{ne} empresas**. O score geral da plataforma é **{score_geral:.0f}/100**.

**Prioridades recomendadas:**
1. {'[OK]' if spct(cc,nu)>70 else '[!]'} Completude de cadastros ({spct(cc,nu)}%)
2. {'[OK]' if nq>0 and spct(rq['id_usuario'].nunique(),nu)>30 else '[!]'} Taxa de ativacao ({spct(rq['id_usuario'].nunique(),nu) if nq>0 and 'id_usuario' in rq.columns else 0}%)
3. {'[OK]' if np_>0 and nq>0 and 'id_produto' in rq.columns and spct(rq['id_produto'].nunique(),np_)>50 else '[!]'} Cobertura de produtos ({spct(rq['id_produto'].nunique(),np_) if np_>0 and nq>0 and 'id_produto' in rq.columns else 0}%)
""")

# ============================================================================
# HELPERS - ANALISES AVANCADAS
# ============================================================================
def _nresp(rp):
    """Extrai respostas numericas convertendo string->float"""
    if len(rp)==0 or 'resposta' not in rp.columns: return pd.DataFrame()
    df=rp.copy(); df['valor']=pd.to_numeric(df['resposta'].astype(str).str.replace('"','').str.strip(),errors='coerce')
    return df.dropna(subset=['valor'])

def _dstats(s):
    """Estatisticas descritivas completas de uma Series numerica"""
    s=s.dropna()
    if len(s)==0: return {}
    d={'N':f"{len(s):,}",'Media':f"{s.mean():.3f}",'Mediana':f"{s.median():.3f}",
       'Moda':f"{s.mode().iloc[0]:.3f}" if not s.mode().empty else "N/A",
       'Desvio Padrao':f"{s.std():.3f}",'Variancia':f"{s.var():.3f}",
       'Minimo':f"{s.min():.3f}",'Maximo':f"{s.max():.3f}",
       'Amplitude':f"{s.max()-s.min():.3f}",
       'Q1 (25%)':f"{s.quantile(.25):.3f}",'Q3 (75%)':f"{s.quantile(.75):.3f}",
       'IQR':f"{s.quantile(.75)-s.quantile(.25):.3f}",
       'Assimetria (Skew)':f"{s.skew():.3f}",'Curtose (Kurt)':f"{s.kurtosis():.3f}",
       'Coef. Variacao (%)':f"{s.std()/s.mean()*100:.1f}" if s.mean()!=0 else "N/A",
       'Erro Padrao':f"{s.sem():.3f}"}
    if HAS_SCIPY and len(s)>1:
        ci=scipy_stats.t.interval(0.95,len(s)-1,loc=s.mean(),scale=scipy_stats.sem(s))
        d['IC 95% Inferior']=f"{ci[0]:.3f}"; d['IC 95% Superior']=f"{ci[1]:.3f}"
    return d

# ============================================================================
# PG18: ANALISE ESTATISTICA AVANCADA
# ============================================================================
def pg_estatistica(data):
    st.markdown(section_header("Analise Estatistica","Testes estatisticos, distribuicoes, correlacoes e deteccao de anomalias"),unsafe_allow_html=True)
    rp=data['resp_pergunta']; rq=data['resp_questionario']
    if len(rp)==0: st.warning("Sem dados de respostas."); return
    rn=_nresp(rp)
    if len(rn)==0: st.warning("Sem respostas numericas para analise."); return
    # KPIs gerais
    c1,c2,c3,c4,c5=st.columns(5)
    with c1: st.markdown(mcard(f"{len(rn):,}","Respostas Numericas"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{rn['valor'].mean():.2f}","Media Geral",c=CL['accent1']),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{rn['valor'].median():.2f}","Mediana",c=CL['teal']),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{rn['valor'].std():.2f}","Desvio Padrao",c=CL['orange']),unsafe_allow_html=True)
    with c5:
        cv=rn['valor'].std()/rn['valor'].mean()*100 if rn['valor'].mean()!=0 else 0
        st.markdown(mcard(f"{cv:.1f}%","Coef. Variacao",c=CL['purple']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    t1,t2,t3,t4,t5=st.tabs(["Descritiva Completa","Normalidade","Correlacoes","Comparacao de Grupos","Outliers"])
    # --- TAB 1: DESCRITIVA ---
    with t1:
        c1,c2=st.columns(2)
        with c1: opcao=st.selectbox("Analisar:",["Geral (todas respostas)","Por Pergunta","Por Produto"],key="ed_op")
        df_a=rn['valor']
        if opcao=="Por Pergunta" and 'titulo_pergunta' in rn.columns:
            with c2: sel=st.selectbox("Pergunta:",sorted(rn['titulo_pergunta'].dropna().unique().tolist()),key="ed_perg")
            df_a=rn[rn['titulo_pergunta']==sel]['valor']
        elif opcao=="Por Produto" and 'nome_produto' in rn.columns:
            with c2: sel=st.selectbox("Produto:",sorted(rn['nome_produto'].dropna().unique().tolist()),key="ed_prod")
            df_a=rn[rn['nome_produto']==sel]['valor']
        if len(df_a)>0:
            c1,c2=st.columns([1,1])
            with c1:
                st.markdown('<div class="chart-title">Estatisticas Descritivas Completas</div>',unsafe_allow_html=True)
                sd=_dstats(df_a)
                st.dataframe(pd.DataFrame({'Metrica':list(sd.keys()),'Valor':list(sd.values())}),hide_index=True,use_container_width=True)
            with c2:
                fig=make_subplots(rows=2,cols=1,row_heights=[.7,.3],shared_xaxes=True,vertical_spacing=0.05)
                fig.add_trace(go.Histogram(x=df_a,nbinsx=20,marker_color=CL['primary'],opacity=.7,name='Distribuicao'),row=1,col=1)
                fig.add_trace(go.Box(x=df_a,marker_color=CL['primary'],name='Box Plot',boxpoints='outliers'),row=2,col=1)
                fig.update_layout(height=500,showlegend=False,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF')
                st.plotly_chart(fig,use_container_width=True,key="ed_hb")
            # Interpretacao automatica
            sk=df_a.skew(); kt=df_a.kurtosis()
            sim='aprox. simetrica' if abs(sk)<0.5 else ('positiva (cauda direita)' if sk>0 else 'negativa (cauda esquerda)')
            ktp='mesocurtica (normal)' if abs(kt)<1 else ('leptocurtica (pico acentuado)' if kt>0 else 'platicurtica (achatada)')
            st.markdown(ibox("Operacional","Interpretacao Automatica",f"Assimetria {sim} (skew={sk:.2f}). Curtose {ktp} (kurt={kt:.2f}). CV={cv:.1f}% indica {'baixa' if cv<15 else 'moderada' if cv<30 else 'alta'} dispersao relativa."),unsafe_allow_html=True)
    # --- TAB 2: NORMALIDADE ---
    with t2:
        if not HAS_SCIPY: st.warning("Instale scipy para testes de normalidade: pip install scipy"); return
        st.markdown('<div class="chart-title">Teste de Normalidade (Shapiro-Wilk)</div>',unsafe_allow_html=True)
        opts_n=["Todas respostas"]
        if 'titulo_pergunta' in rn.columns: opts_n+=sorted(rn['titulo_pergunta'].dropna().unique().tolist())
        sel_n=st.selectbox("Dados para teste:",opts_n,key="norm_s")
        vals=rn['valor'] if sel_n=="Todas respostas" else rn[rn['titulo_pergunta']==sel_n]['valor']
        if len(vals)>=3:
            smp=vals.sample(min(5000,len(vals)),random_state=42)
            try: sw_s,sw_p=scipy_stats.shapiro(smp[:5000]); ok=sw_p>0.05
            except: sw_s,sw_p,ok=0,0,False
            c1,c2,c3=st.columns(3)
            with c1: st.markdown(mcard(f"{sw_s:.4f}","Estatistica W"),unsafe_allow_html=True)
            with c2: st.markdown(mcard(f"{sw_p:.6f}","p-valor",c=CL['success'] if ok else CL['danger']),unsafe_allow_html=True)
            with c3: st.markdown(mcard("Normal" if ok else "Nao-Normal","Resultado (alfa=0.05)",c=CL['success'] if ok else CL['warning']),unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                # QQ-Plot
                st.markdown('<div class="chart-title">QQ-Plot</div>',unsafe_allow_html=True)
                qq=scipy_stats.probplot(smp)
                fig=go.Figure()
                fig.add_trace(go.Scatter(x=qq[0][0],y=qq[0][1],mode='markers',marker=dict(color=CL['primary'],size=3),name='Dados'))
                sl_,ic_=qq[1][0],qq[1][1]; xl=[qq[0][0].min(),qq[0][0].max()]
                fig.add_trace(go.Scatter(x=xl,y=[sl_*x+ic_ for x in xl],mode='lines',line=dict(color=CL['danger'],dash='dash'),name='Normal Teorica'))
                fig.update_layout(height=400,xaxis_title="Quantis Teoricos",yaxis_title="Quantis Observados",paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF')
                st.plotly_chart(fig,use_container_width=True,key="qq_plt")
            with c2:
                # Histograma vs curva normal
                st.markdown('<div class="chart-title">Distribuicao vs Normal Teorica</div>',unsafe_allow_html=True)
                fig=go.Figure()
                fig.add_trace(go.Histogram(x=smp,nbinsx=30,histnorm='probability density',marker_color=CL['primary'],opacity=.7,name='Dados'))
                xr=np.linspace(smp.min(),smp.max(),100)
                fig.add_trace(go.Scatter(x=xr,y=scipy_stats.norm.pdf(xr,smp.mean(),smp.std()),mode='lines',line=dict(color=CL['danger'],width=2),name='Normal'))
                fig.update_layout(height=400,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF')
                st.plotly_chart(fig,use_container_width=True,key="hist_norm")
            st.markdown(ibox("Estrategico","Resultado do Teste",f"{'Dados seguem distribuicao normal (p={sw_p:.4f} > 0.05). Testes parametricos (t-Student, ANOVA) sao aplicaveis.' if ok else f'Dados NAO seguem distribuicao normal (p={sw_p:.6f} < 0.05). Recomenda-se testes nao-parametricos (Mann-Whitney, Kruskal-Wallis).'}"),unsafe_allow_html=True)
        else: st.info("Minimo 3 observacoes para teste de normalidade.")
    # --- TAB 3: CORRELACOES ---
    with t3:
        st.markdown('<div class="chart-title">Matriz de Correlacao entre Perguntas</div>',unsafe_allow_html=True)
        if 'titulo_pergunta' in rn.columns and 'id_usuario' in rn.columns:
            top_p=rn['titulo_pergunta'].value_counts().head(12).index.tolist()
            pv=rn[rn['titulo_pergunta'].isin(top_p)].pivot_table(index='id_usuario',columns='titulo_pergunta',values='valor',aggfunc='mean')
            if pv.shape[1]>=2:
                met=st.radio("Metodo:",["Pearson","Spearman"],horizontal=True,key="corr_m")
                cr=pv.corr(method=met.lower())
                # Heatmap de correlacao
                fig=px.imshow(cr,text_auto='.2f',color_continuous_scale='RdBu_r',zmin=-1,zmax=1,aspect='auto')
                fig.update_layout(height=max(400,len(cr)*40),paper_bgcolor='#FFFFFF')
                st.plotly_chart(fig,use_container_width=True,key="corr_hm")
                # Top pares correlacionados
                st.markdown('<div class="chart-title">Top Pares Correlacionados</div>',unsafe_allow_html=True)
                pairs=[]
                for i in range(len(cr.columns)):
                    for j in range(i+1,len(cr.columns)):
                        r=cr.iloc[i,j]
                        pairs.append({'Variavel 1':cr.columns[i][:40],'Variavel 2':cr.columns[j][:40],'Correlacao':round(r,4),
                            'Forca':'Forte' if abs(r)>.7 else 'Moderada' if abs(r)>.4 else 'Fraca','Direcao':'Positiva' if r>0 else 'Negativa'})
                pf=pd.DataFrame(pairs).sort_values('Correlacao',key=lambda x:x.abs(),ascending=False)
                st.dataframe(pf.head(15),hide_index=True,use_container_width=True)
                # Scatter do top par
                if len(pf)>0:
                    tp=pf.iloc[0]
                    v1_name=tp['Variavel 1']; v2_name=tp['Variavel 2']
                    if v1_name in pv.columns and v2_name in pv.columns:
                        fig=px.scatter(pv.dropna(subset=[v1_name,v2_name]),x=v1_name,y=v2_name,trendline='ols',
                            color_discrete_sequence=[CL['primary']],title=f"Dispersao: {v1_name[:25]} vs {v2_name[:25]}")
                        fig.update_layout(height=400,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF')
                        st.plotly_chart(fig,use_container_width=True,key="corr_sc")
                # Insight
                fortes=[p for p in pairs if abs(p['Correlacao'])>.7]
                st.markdown(ibox("Estrategico","Analise de Correlacao",f"{len(fortes)} pares com correlacao forte (|r|>0.7) de {len(pairs)} pares analisados. {'Perguntas fortemente correlacionadas podem indicar redundancia no questionario.' if len(fortes)>2 else 'Perguntas com correlacoes variadas indicam boa diversidade no instrumento.'}"),unsafe_allow_html=True)
            else: st.info("Minimo 2 perguntas com respostas numericas para analise de correlacao.")
        else: st.info("Dados insuficientes para correlacao.")
    # --- TAB 4: COMPARACAO DE GRUPOS ---
    with t4:
        st.markdown('<div class="chart-title">Comparacao Estatistica entre Grupos</div>',unsafe_allow_html=True)
        gp=st.selectbox("Agrupar por:",["Produto","Pergunta"],key="gp4")
        col='nome_produto' if gp=="Produto" else 'titulo_pergunta'
        if col in rn.columns and rn[col].notna().any():
            tg=rn[col].value_counts().head(10).index.tolist()
            dg=rn[rn[col].isin(tg)]
            if len(tg)>=2:
                # Violin plot comparativo
                fig=px.violin(dg,x=col,y='valor',box=True,points='outliers',color=col,color_discrete_sequence=PAL)
                fig.update_layout(height=500,xaxis_title="",yaxis_title="Valor",showlegend=False,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',xaxis_tickangle=45)
                st.plotly_chart(fig,use_container_width=True,key="viol_g4")
                # ANOVA
                if HAS_SCIPY:
                    grps=[g['valor'].values for _,g in dg.groupby(col) if len(g)>1]
                    if len(grps)>=2:
                        try:
                            f_s,p_v=scipy_stats.f_oneway(*grps)
                            c1,c2,c3=st.columns(3)
                            with c1: st.markdown(mcard(f"{f_s:.4f}","F (ANOVA)"),unsafe_allow_html=True)
                            with c2: st.markdown(mcard(f"{p_v:.6f}","p-valor",c=CL['success'] if p_v>.05 else CL['danger']),unsafe_allow_html=True)
                            with c3: st.markdown(mcard("Sim" if p_v<.05 else "Nao","Diferenca Significativa?",c=CL['danger'] if p_v<.05 else CL['success']),unsafe_allow_html=True)
                            st.markdown(ibox("Estrategico","Resultado ANOVA",f"{'Diferenca SIGNIFICATIVA entre grupos (F={f_s:.2f}, p={p_v:.6f}). Pelo menos dois grupos possuem medias estatisticamente diferentes.' if p_v<.05 else f'SEM diferenca significativa entre grupos (F={f_s:.2f}, p={p_v:.4f}). As medias sao estatisticamente similares.'}"),unsafe_allow_html=True)
                        except: st.info("Dados insuficientes para ANOVA.")
                # Tabela de estatisticas por grupo
                st.markdown('<div class="chart-title">Estatisticas por Grupo</div>',unsafe_allow_html=True)
                gs=dg.groupby(col)['valor'].agg(['count','mean','median','std','min','max']).round(3)
                gs.columns=['N','Media','Mediana','DP','Min','Max']
                gs['CV (%)']=((gs['DP']/gs['Media'])*100).round(1)
                st.dataframe(gs.sort_values('Media',ascending=False),use_container_width=True)
            else: st.info("Minimo 2 grupos para comparacao.")
        else: st.info("Coluna de agrupamento nao encontrada.")
    # --- TAB 5: OUTLIERS ---
    with t5:
        st.markdown('<div class="chart-title">Deteccao de Outliers</div>',unsafe_allow_html=True)
        mt_o=st.radio("Metodo:",["IQR (Interquartil)","Z-Score"],horizontal=True,key="out_m")
        vals=rn['valor']
        if mt_o=="IQR (Interquartil)":
            Q1,Q3=vals.quantile(.25),vals.quantile(.75); IQR_=Q3-Q1
            lo,hi=Q1-1.5*IQR_,Q3+1.5*IQR_
            outs=rn[(vals<lo)|(vals>hi)]; norms=rn[(vals>=lo)&(vals<=hi)]
            c1,c2,c3,c4=st.columns(4)
            with c1: st.markdown(mcard(f"{len(outs):,}","Outliers Detectados",c=CL['danger']),unsafe_allow_html=True)
            with c2: st.markdown(mcard(f"{spct(len(outs),len(rn))}%","Percentual"),unsafe_allow_html=True)
            with c3: st.markdown(mcard(f"{lo:.2f}","Limite Inferior",c=CL['teal']),unsafe_allow_html=True)
            with c4: st.markdown(mcard(f"{hi:.2f}","Limite Superior",c=CL['teal']),unsafe_allow_html=True)
        else:
            zs=scipy_stats.zscore(vals) if HAS_SCIPY else (vals-vals.mean())/vals.std()
            outs=rn[np.abs(zs)>3]; norms=rn[np.abs(zs)<=3]
            c1,c2,c3=st.columns(3)
            with c1: st.markdown(mcard(f"{len(outs):,}","Outliers (|Z|>3)",c=CL['danger']),unsafe_allow_html=True)
            with c2: st.markdown(mcard(f"{spct(len(outs),len(rn))}%","Percentual"),unsafe_allow_html=True)
            with c3: st.markdown(mcard(f"{len(norms):,}","Dentro do Esperado",c=CL['success']),unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            fig=px.box(rn,y='valor',points='outliers',color_discrete_sequence=[CL['primary']])
            fig.update_layout(height=400,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',yaxis_title="Valor")
            st.plotly_chart(fig,use_container_width=True,key="out_box")
        with c2:
            fig=go.Figure()
            fig.add_trace(go.Histogram(x=norms['valor'],marker_color=CL['primary'],opacity=.7,name='Normal'))
            if len(outs)>0: fig.add_trace(go.Histogram(x=outs['valor'],marker_color=CL['danger'],opacity=.7,name='Outliers'))
            fig.update_layout(height=400,barmode='overlay',paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',legend=dict(font=dict(color='#202124')))
            st.plotly_chart(fig,use_container_width=True,key="out_hist")
        if len(outs)>0 and 'nome_usuario' in outs.columns:
            st.markdown('<div class="chart-title">Usuarios com Mais Outliers</div>',unsafe_allow_html=True)
            ou=outs['nome_usuario'].value_counts().head(10)
            fig=hbar(ou.values,ou.index,cs='Reds')
            fig.update_layout(height=350,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True,key="out_usr")
        st.markdown(ibox("Tatico","Analise de Outliers",f"{len(outs):,} outliers detectados ({spct(len(outs),len(rn))}% das respostas). {'Volume baixo - dados consistentes.' if spct(len(outs),len(rn))<5 else 'Volume significativo - investigar respostas anomalas e possivel impacto nas medias.'}"),unsafe_allow_html=True)

# ============================================================================
# PG19: ANALISE EXPLORATORIA (EDA)
# ============================================================================
def pg_eda(data):
    st.markdown(section_header("Analise Exploratoria (EDA)","Visualizacoes avancadas e exploracoes multidimensionais dos dados"),unsafe_allow_html=True)
    rp=data['resp_pergunta']; rq=data['resp_questionario']; pr=data['produto']
    us=data['usuario']; cat=data['categoria']; sub=data['subcategoria']
    rn=_nresp(rp)
    if len(rn)==0: st.warning("Sem respostas numericas."); return
    # KPIs
    n_pergs=rn['titulo_pergunta'].nunique() if 'titulo_pergunta' in rn.columns else 0
    n_prods=rn['nome_produto'].nunique() if 'nome_produto' in rn.columns else 0
    n_usrs=rn['id_usuario'].nunique() if 'id_usuario' in rn.columns else 0
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(mcard(f"{len(rn):,}","Respostas Analisadas"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{n_pergs}","Perguntas",c=CL['accent1']),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{n_prods}","Produtos",c=CL['teal']),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{n_usrs:,}","Avaliadores",c=CL['purple']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    t1,t2,t3,t4=st.tabs(["Distribuicoes","Hierarquias","Multivariada","Perfil Comparativo"])
    # --- TAB 1: DISTRIBUICOES ---
    with t1:
        st.markdown('<div class="chart-title">Distribuicao de Respostas por Pergunta</div>',unsafe_allow_html=True)
        if 'titulo_pergunta' in rn.columns:
            # Boxplot com jitter por pergunta (top 8)
            top_pergs=rn['titulo_pergunta'].value_counts().head(8).index.tolist()
            df_bp=rn[rn['titulo_pergunta'].isin(top_pergs)]
            fig=px.box(df_bp,x='titulo_pergunta',y='valor',points='all',color='titulo_pergunta',color_discrete_sequence=PAL)
            fig.update_layout(height=500,xaxis_title="",yaxis_title="Valor",showlegend=False,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',xaxis_tickangle=45)
            fig.update_traces(marker=dict(size=2,opacity=0.3),jitter=0.3)
            st.plotly_chart(fig,use_container_width=True,key="eda_box")
        # Violin por produto (top 6)
        if 'nome_produto' in rn.columns:
            st.markdown('<div class="chart-title">Violin Plot por Produto (Top 6)</div>',unsafe_allow_html=True)
            top_prods=rn['nome_produto'].value_counts().head(6).index.tolist()
            df_vp=rn[rn['nome_produto'].isin(top_prods)]
            fig=px.violin(df_vp,x='nome_produto',y='valor',box=True,points='outliers',color='nome_produto',color_discrete_sequence=PAL)
            fig.update_layout(height=450,xaxis_title="",showlegend=False,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',xaxis_tickangle=45)
            st.plotly_chart(fig,use_container_width=True,key="eda_violin")
        # Histograma comparativo
        st.markdown('<div class="chart-title">Distribuicao Comparativa de Notas</div>',unsafe_allow_html=True)
        fig=go.Figure()
        fig.add_trace(go.Histogram(x=rn['valor'],nbinsx=9,marker_color=CL['primary'],opacity=.8,name='Todas'))
        fig.update_layout(height=350,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',xaxis_title="Nota",yaxis_title="Frequencia",bargap=0.05)
        st.plotly_chart(fig,use_container_width=True,key="eda_hist")
    # --- TAB 2: HIERARQUIAS ---
    with t2:
        # Sunburst hierarquico
        st.markdown('<div class="chart-title">Sunburst: Categoria > Subcategoria > Produto</div>',unsafe_allow_html=True)
        if len(rq)>0 and 'nome_categoria' in rq.columns and 'nome_subcategoria' in rq.columns:
            sb_data=rq.dropna(subset=['nome_categoria','nome_subcategoria'])
            if 'nome_produto' in sb_data.columns:
                sb_g=sb_data.groupby(['nome_categoria','nome_subcategoria','nome_produto']).size().reset_index(name='qtd')
                sb_g=sb_g[sb_g['qtd']>0]
                if len(sb_g)>0:
                    fig=px.sunburst(sb_g,path=['nome_categoria','nome_subcategoria','nome_produto'],values='qtd',
                        color='qtd',color_continuous_scale='Blues')
                    fig.update_layout(height=600,paper_bgcolor='#FFFFFF')
                    st.plotly_chart(fig,use_container_width=True,key="eda_sun")
            else:
                sb_g=sb_data.groupby(['nome_categoria','nome_subcategoria']).size().reset_index(name='qtd')
                if len(sb_g)>0:
                    fig=px.sunburst(sb_g,path=['nome_categoria','nome_subcategoria'],values='qtd',
                        color='qtd',color_continuous_scale='Blues')
                    fig.update_layout(height=600,paper_bgcolor='#FFFFFF')
                    st.plotly_chart(fig,use_container_width=True,key="eda_sun2")
        # Treemap detalhado de respostas
        if len(rq)>0 and 'nome_categoria' in rq.columns:
            st.markdown('<div class="chart-title">Treemap de Volume por Hierarquia</div>',unsafe_allow_html=True)
            cols_tm=['nome_categoria']
            if 'nome_subcategoria' in rq.columns: cols_tm.append('nome_subcategoria')
            tm_g=rq.dropna(subset=cols_tm).groupby(cols_tm).size().reset_index(name='questionarios')
            if len(tm_g)>0:
                fig=px.treemap(tm_g,path=cols_tm,values='questionarios',color='questionarios',color_continuous_scale='Greens')
                fig.update_layout(height=500,paper_bgcolor='#FFFFFF')
                st.plotly_chart(fig,use_container_width=True,key="eda_tm")
    # --- TAB 3: MULTIVARIADA ---
    with t3:
        if 'titulo_pergunta' in rn.columns and 'id_usuario' in rn.columns:
            # Parallel coordinates
            st.markdown('<div class="chart-title">Coordenadas Paralelas (Perfil Multidimensional)</div>',unsafe_allow_html=True)
            top_pc=rn['titulo_pergunta'].value_counts().head(6).index.tolist()
            pv_pc=rn[rn['titulo_pergunta'].isin(top_pc)].pivot_table(index='id_usuario',columns='titulo_pergunta',values='valor',aggfunc='mean').dropna()
            if len(pv_pc)>=10 and pv_pc.shape[1]>=3:
                pv_pc['media_geral']=pv_pc.mean(axis=1)
                # Amostra para performance
                smp_pc=pv_pc.sample(min(500,len(pv_pc)),random_state=42)
                dims=[dict(label=c[:20],values=smp_pc[c]) for c in smp_pc.columns if c!='media_geral']
                fig=go.Figure(go.Parcoords(line=dict(color=smp_pc['media_geral'],colorscale='Bluered',showscale=True,cmin=1,cmax=9),dimensions=dims))
                fig.update_layout(height=500,paper_bgcolor='#FFFFFF',font=dict(size=10))
                st.plotly_chart(fig,use_container_width=True,key="eda_pc")
                st.markdown(ibox("Estrategico","Coordenadas Paralelas","Cada linha representa um avaliador. A cor indica a media geral (azul=baixa, vermelho=alta). Padroes visuais revelam perfis de avaliacao consistentes ou discrepantes."),unsafe_allow_html=True)
            else: st.info("Dados insuficientes para coordenadas paralelas (min. 10 usuarios, 3 perguntas).")
            # Scatter Matrix
            st.markdown('<div class="chart-title">Matriz de Dispersao (Scatter Matrix)</div>',unsafe_allow_html=True)
            top_sm=rn['titulo_pergunta'].value_counts().head(4).index.tolist()
            pv_sm=rn[rn['titulo_pergunta'].isin(top_sm)].pivot_table(index='id_usuario',columns='titulo_pergunta',values='valor',aggfunc='mean').dropna()
            if pv_sm.shape[1]>=2:
                smp_sm=pv_sm.sample(min(300,len(pv_sm)),random_state=42)
                fig=px.scatter_matrix(smp_sm,dimensions=smp_sm.columns.tolist(),color_discrete_sequence=[CL['primary']])
                fig.update_layout(height=600,paper_bgcolor='#FFFFFF'); fig.update_traces(diagonal_visible=True,marker=dict(size=3,opacity=0.4))
                st.plotly_chart(fig,use_container_width=True,key="eda_sm")
        else: st.info("Dados insuficientes para analise multivariada.")
    # --- TAB 4: PERFIL COMPARATIVO ---
    with t4:
        st.markdown('<div class="chart-title">Radar Comparativo de Produtos</div>',unsafe_allow_html=True)
        if 'nome_produto' in rn.columns and 'titulo_pergunta' in rn.columns:
            prods_disp=rn.groupby('nome_produto').filter(lambda x: x['titulo_pergunta'].nunique()>=3)['nome_produto'].unique().tolist()
            if len(prods_disp)>=2:
                prods_sel=st.multiselect("Selecione produtos para comparar (2-5):",sorted(prods_disp),default=sorted(prods_disp)[:min(3,len(prods_disp))],key="eda_radar_sel",max_selections=5)
                if len(prods_sel)>=2:
                    fig=go.Figure()
                    for i,prd in enumerate(prods_sel):
                        rpr=rn[rn['nome_produto']==prd]
                        pergs=rpr.groupby('titulo_pergunta')['valor'].mean().sort_index()
                        if len(pergs)>=3:
                            fig.add_trace(go.Scatterpolar(r=pergs.values.tolist()+[pergs.values[0]],
                                theta=pergs.index.tolist()+[pergs.index[0]],
                                fill='toself',name=prd[:30],line_color=PAL[i%len(PAL)],opacity=0.6))
                    fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,9])),height=500,
                        showlegend=True,paper_bgcolor='#FFFFFF',legend=dict(font=dict(color='#202124')))
                    st.plotly_chart(fig,use_container_width=True,key="eda_radar")
                    # Tabela comparativa
                    st.markdown('<div class="chart-title">Tabela Comparativa</div>',unsafe_allow_html=True)
                    comp_data=[]
                    for prd in prods_sel:
                        rpr=rn[rn['nome_produto']==prd]
                        comp_data.append({'Produto':prd[:35],'N':len(rpr),'Media':round(rpr['valor'].mean(),2),
                            'Mediana':round(rpr['valor'].median(),2),'DP':round(rpr['valor'].std(),2),
                            'Min':round(rpr['valor'].min(),2),'Max':round(rpr['valor'].max(),2)})
                    st.dataframe(pd.DataFrame(comp_data),hide_index=True,use_container_width=True)
                else: st.info("Selecione pelo menos 2 produtos.")
            else: st.info("Menos de 2 produtos com perfil sensorial completo.")
        else: st.info("Dados de produto/pergunta nao disponiveis.")

# ============================================================================
# PG20: PERFORMANCE DE PRODUTOS
# ============================================================================
def pg_performance(data):
    st.markdown(section_header("Performance de Produtos","Ranking, benchmarks e analise de consistencia dos produtos avaliados"),unsafe_allow_html=True)
    rp=data['resp_pergunta']; rq=data['resp_questionario']; pr=data['produto']
    rn=_nresp(rp)
    if len(rn)==0 or 'nome_produto' not in rn.columns: st.warning("Sem dados suficientes."); return
    # Calcular metricas por produto
    prod_stats=rn.groupby('nome_produto')['valor'].agg(['count','mean','median','std']).round(3)
    prod_stats.columns=['avaliacoes','media','mediana','dp']
    prod_stats['cv']=(prod_stats['dp']/prod_stats['media']*100).round(1)
    prod_stats=prod_stats[prod_stats['avaliacoes']>=5].sort_values('media',ascending=False)  # min 5 avaliacoes
    if len(prod_stats)==0: st.warning("Nenhum produto com minimo de 5 avaliacoes."); return
    # KPIs
    c1,c2,c3,c4,c5=st.columns(5)
    with c1: st.markdown(mcard(f"{len(prod_stats)}","Produtos Avaliados"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{prod_stats['media'].mean():.2f}","Media Global",c=CL['accent1']),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{prod_stats['dp'].mean():.2f}","DP Medio",c=CL['orange']),unsafe_allow_html=True)
    with c4:
        best=prod_stats.index[0] if len(prod_stats)>0 else "N/A"
        st.markdown(mcard(f"{prod_stats['media'].max():.2f}","Melhor Nota",c=CL['success']),unsafe_allow_html=True)
    with c5:
        st.markdown(mcard(f"{prod_stats['media'].min():.2f}","Menor Nota",c=CL['danger']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["Ranking","Benchmark por Categoria","Consistencia"])
    # --- TAB 1: RANKING ---
    with t1:
        # Filtro
        n_show=st.slider("Exibir top:",5,min(50,len(prod_stats)),15,key="perf_n")
        top=prod_stats.head(n_show).reset_index()
        # Grafico de ranking com barras + IC
        fig=go.Figure()
        fig.add_trace(go.Bar(y=top['nome_produto'],x=top['media'],orientation='h',marker_color=CL['primary'],
            text=[f"{m:.2f} (n={n})" for m,n in zip(top['media'],top['avaliacoes'])],textposition='outside',name='Media'))
        # Erro padrao como barra de erro
        if HAS_SCIPY:
            erros=[]
            for prd in top['nome_produto']:
                vals=rn[rn['nome_produto']==prd]['valor']
                erros.append(scipy_stats.sem(vals) if len(vals)>1 else 0)
            fig.data[0].error_x=dict(type='data',array=erros,visible=True,color=CL['danger'])
        fig.update_layout(height=max(400,n_show*35),yaxis_title="",xaxis_title="Nota Media",paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF')
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig,use_container_width=True,key="perf_rank")
        # Tabela completa
        st.markdown('<div class="chart-title">Tabela Detalhada</div>',unsafe_allow_html=True)
        disp=prod_stats.reset_index()
        disp.columns=['Produto','Avaliacoes','Media','Mediana','DP','CV (%)']
        st.dataframe(disp,hide_index=True,use_container_width=True,height=400)
        # Insight
        if len(prod_stats)>=3:
            best_p=prod_stats.index[0]; worst_p=prod_stats.index[-1]
            diff=prod_stats['media'].max()-prod_stats['media'].min()
            st.markdown(ibox("Estrategico","Ranking de Produtos",f"Melhor: '{best_p[:30]}' (media {prod_stats['media'].max():.2f}). Pior: '{worst_p[:30]}' (media {prod_stats['media'].min():.2f}). Amplitude de {diff:.2f} pontos entre melhor e pior produto."),unsafe_allow_html=True)
    # --- TAB 2: BENCHMARK POR CATEGORIA ---
    with t2:
        if len(rq)>0 and 'nome_categoria' in rq.columns and 'id_produto' in rq.columns:
            # Mapear produto -> categoria
            prod_cat=rq[['id_produto','nome_categoria']].dropna().drop_duplicates()
            if 'id_produto' in rn.columns:
                rn_cat=rn.merge(prod_cat,on='id_produto',how='left',suffixes=('','_cat'))
                col_cat='nome_categoria' if 'nome_categoria' in rn_cat.columns else 'nome_categoria_cat'
                if col_cat in rn_cat.columns and rn_cat[col_cat].notna().any():
                    # Media por categoria
                    cat_stats=rn_cat.groupby(col_cat)['valor'].agg(['count','mean','std']).round(3)
                    cat_stats.columns=['N','Media','DP']
                    cat_stats=cat_stats[cat_stats['N']>=10].sort_values('Media',ascending=False)
                    if len(cat_stats)>0:
                        st.markdown('<div class="chart-title">Benchmark: Nota Media por Categoria</div>',unsafe_allow_html=True)
                        cs_r=cat_stats.reset_index()
                        fig=px.bar(cs_r,x='Media',y=col_cat,orientation='h',color='Media',
                            color_continuous_scale='RdYlGn',text='Media')
                        fig.update_layout(height=max(300,len(cat_stats)*40),yaxis_title="",paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',coloraxis_showscale=False)
                        fig.update_yaxes(autorange="reversed"); fig.update_traces(texttemplate='%{text:.2f}',textposition='outside')
                        st.plotly_chart(fig,use_container_width=True,key="perf_bench")
                        # Boxplot comparativo de categorias
                        st.markdown('<div class="chart-title">Distribuicao de Notas por Categoria</div>',unsafe_allow_html=True)
                        top_cats=cat_stats.head(8).index.tolist()
                        df_cb=rn_cat[rn_cat[col_cat].isin(top_cats)]
                        fig=px.box(df_cb,x=col_cat,y='valor',color=col_cat,color_discrete_sequence=PAL,points='outliers')
                        fig.update_layout(height=450,showlegend=False,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',xaxis_tickangle=45)
                        st.plotly_chart(fig,use_container_width=True,key="perf_catbox")
                        # Insight
                        best_c=cat_stats.index[0]; worst_c=cat_stats.index[-1]
                        st.markdown(ibox("Tatico","Benchmark por Categoria",f"Melhor categoria: '{best_c}' (media {cat_stats['Media'].max():.2f}). Pior: '{worst_c}' (media {cat_stats['Media'].min():.2f}). Categorias com notas baixas podem necessitar de reformulacao ou investigacao."),unsafe_allow_html=True)
                    else: st.info("Nenhuma categoria com minimo de 10 avaliacoes.")
                else: st.info("Informacao de categoria nao disponivel.")
            else: st.info("Coluna id_produto nao encontrada.")
        else: st.info("Dados de categoria nao disponiveis.")
    # --- TAB 3: CONSISTENCIA ---
    with t3:
        st.markdown('<div class="chart-title">Analise de Consistencia (Variabilidade entre Avaliadores)</div>',unsafe_allow_html=True)
        # Scatter: Media x DP por produto
        ps_r=prod_stats.reset_index()
        fig=px.scatter(ps_r,x='media',y='dp',size='avaliacoes',color='cv',
            color_continuous_scale='RdYlGn_r',hover_name='nome_produto',
            labels={'media':'Nota Media','dp':'Desvio Padrao','avaliacoes':'N Avaliacoes','cv':'CV (%)'},
            title="Media vs Desvio Padrao por Produto")
        fig.update_layout(height=500,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF')
        st.plotly_chart(fig,use_container_width=True,key="perf_cons")
        # Produtos mais e menos consistentes
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<div class="chart-title">Mais Consistentes (Menor CV)</div>',unsafe_allow_html=True)
            cons=prod_stats.nsmallest(10,'cv').reset_index()
            fig=px.bar(cons,x='cv',y='nome_produto',orientation='h',color='cv',color_continuous_scale='Greens_r',text='cv')
            fig.update_layout(height=350,yaxis_title="",coloraxis_showscale=False,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF')
            fig.update_yaxes(autorange="reversed"); fig.update_traces(texttemplate='%{text:.1f}%',textposition='outside')
            st.plotly_chart(fig,use_container_width=True,key="perf_cons_best")
        with c2:
            st.markdown('<div class="chart-title">Menos Consistentes (Maior CV)</div>',unsafe_allow_html=True)
            incons=prod_stats.nlargest(10,'cv').reset_index()
            fig=px.bar(incons,x='cv',y='nome_produto',orientation='h',color='cv',color_continuous_scale='Reds',text='cv')
            fig.update_layout(height=350,yaxis_title="",coloraxis_showscale=False,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF')
            fig.update_yaxes(autorange="reversed"); fig.update_traces(texttemplate='%{text:.1f}%',textposition='outside')
            st.plotly_chart(fig,use_container_width=True,key="perf_cons_worst")
        # Insight
        avg_cv=prod_stats['cv'].mean()
        st.markdown(ibox("Operacional","Consistencia",f"CV medio: {avg_cv:.1f}%. {'Boa consistencia geral entre avaliadores.' if avg_cv<25 else 'Alta variabilidade sugere divergencia nas percepcoes sensoriais ou necessidade de calibracao dos avaliadores.'}"),unsafe_allow_html=True)

# ============================================================================
# PG21: ENGAJAMENTO E GAMIFICACAO
# ============================================================================
def pg_engajamento(data):
    st.markdown(section_header("Engajamento e Gamificacao","Funil de conversao, retencao, NPS e economia de pontos"),unsafe_allow_html=True)
    us=data['usuario']; rq=data['resp_questionario']; rp=data['resp_pergunta']
    rg=data['resgate']; pt=data['pontos']; bn=data['beneficio']
    nu=len(us)
    if nu==0: st.warning("Sem dados de usuarios."); return
    # Calculos base
    cc=0
    if 'is_cadastro_completo' in us.columns:
        cv_=us['is_cadastro_completo'].fillna(False)
        if cv_.dtype=='object': cv_=cv_.astype(str).str.lower().map({'true':True,'false':False,'1':True,'0':False,'nan':False}).fillna(False)
        cc=int(cv_.sum())
    ativos=rq['id_usuario'].nunique() if len(rq)>0 and 'id_usuario' in rq.columns else 0
    resgataram=rg['id_usuario'].nunique() if len(rg)>0 and 'id_usuario' in rg.columns else 0
    pts_total=int(pd.to_numeric(pt['pontos'],errors='coerce').fillna(0).sum()) if len(pt)>0 and 'pontos' in pt.columns else 0
    # KPIs
    c1,c2,c3,c4,c5=st.columns(5)
    with c1: st.markdown(mcard(f"{nu:,}","Cadastrados"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{cc:,}","Cad. Completo",f"{spct(cc,nu)}%",c=CL['success']),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{ativos:,}","Ativos",f"{spct(ativos,nu)}%",c=CL['accent1']),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{resgataram:,}","Resgataram",f"{spct(resgataram,nu)}%",c=CL['orange']),unsafe_allow_html=True)
    with c5: st.markdown(mcard(f"{pts_total:,}","Pontos Totais",c=CL['purple']),unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    t1,t2,t3,t4=st.tabs(["Funil de Conversao","Retencao e Cohorts","NPS","Economia de Pontos"])
    # --- TAB 1: FUNIL ---
    with t1:
        st.markdown('<div class="chart-title">Funil de Engajamento</div>',unsafe_allow_html=True)
        # Calcular etapas do funil
        usr_5plus=0
        if len(rq)>0 and 'id_usuario' in rq.columns:
            uc=rq.groupby('id_usuario').size()
            usr_5plus=int((uc>=5).sum())
        etapas=['Cadastrados','Cadastro Completo','Responderam 1+','Responderam 5+','Resgataram Beneficio']
        valores=[nu,cc,ativos,usr_5plus,resgataram]
        # Funnel chart
        fig=go.Figure(go.Funnel(y=etapas,x=valores,textinfo="value+percent initial",
            marker=dict(color=[CL['primary'],CL['accent1'],CL['teal'],CL['orange'],CL['success']]),
            connector=dict(line=dict(color='#E8EAED',width=2))))
        fig.update_layout(height=450,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',font=dict(family='Inter',color='#202124'))
        st.plotly_chart(fig,use_container_width=True,key="eng_funnel")
        # Taxas de conversao entre etapas
        st.markdown('<div class="chart-title">Taxas de Conversao entre Etapas</div>',unsafe_allow_html=True)
        conv_data=[]
        for i in range(1,len(etapas)):
            prev=valores[i-1]; curr=valores[i]
            taxa=spct(curr,prev) if prev>0 else 0
            conv_data.append({'De':etapas[i-1],'Para':etapas[i],'Convertidos':curr,'Taxa':f"{taxa}%"})
        st.dataframe(pd.DataFrame(conv_data),hide_index=True,use_container_width=True)
        # Insight funil
        gargalo_idx=0; min_taxa=100
        for i in range(1,len(valores)):
            t_=spct(valores[i],valores[i-1]) if valores[i-1]>0 else 0
            if t_<min_taxa: min_taxa=t_; gargalo_idx=i
        st.markdown(ibox("Estrategico","Gargalo do Funil",f"Maior queda: {etapas[gargalo_idx-1]} -> {etapas[gargalo_idx]} (taxa {min_taxa}%). Foco em acoes para melhorar esta conversao."),unsafe_allow_html=True)
    # --- TAB 2: RETENCAO E COHORTS ---
    with t2:
        if len(rq)>0 and 'id_usuario' in rq.columns and 'createdAt' in rq.columns:
            st.markdown('<div class="chart-title">Retencao: Usuarios que Voltam a Avaliar</div>',unsafe_allow_html=True)
            # Usuarios por numero de questionarios
            uc=rq.groupby('id_usuario').size().reset_index(name='qtd')
            uc['cohort']=pd.cut(uc['qtd'],bins=[0,1,3,5,10,25,50,1000],labels=['1','2-3','4-5','6-10','11-25','26-50','50+'])
            cc_=uc['cohort'].value_counts().sort_index()
            fig=px.bar(x=cc_.index.astype(str).tolist(),y=cc_.values.tolist(),color=cc_.values.tolist(),
                color_continuous_scale='Blues',labels={'x':'Questionarios Respondidos','y':'Usuarios'})
            fig.update_layout(height=400,coloraxis_showscale=False,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF')
            st.plotly_chart(fig,use_container_width=True,key="eng_cohort")
            # Retencao mensal
            st.markdown('<div class="chart-title">Atividade Mensal de Usuarios</div>',unsafe_allow_html=True)
            rq_m=rq.copy(); rq_m['mes']=rq_m['createdAt'].dt.to_period('M')
            usr_mes=rq_m.groupby('mes')['id_usuario'].nunique().reset_index(name='usuarios_ativos')
            usr_mes['mes']=usr_mes['mes'].astype(str)
            fig=px.area(usr_mes,x='mes',y='usuarios_ativos',color_discrete_sequence=[CL['primary']],
                labels={'mes':'Mes','usuarios_ativos':'Usuarios Ativos'})
            fig.update_layout(height=350,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',xaxis_tickangle=45)
            st.plotly_chart(fig,use_container_width=True,key="eng_ret_mes")
            # Heatmap dia da semana x hora
            if 'hora' in rq.columns and 'dia_semana' in rq.columns:
                st.markdown('<div class="chart-title">Heatmap: Horario de Atividade</div>',unsafe_allow_html=True)
                hm=rq.groupby(['dia_semana','hora']).size().reset_index(name='qtd')
                do_map={'Monday':0,'Tuesday':1,'Wednesday':2,'Thursday':3,'Friday':4,'Saturday':5,'Sunday':6}
                dn_map={'Monday':'Seg','Tuesday':'Ter','Wednesday':'Qua','Thursday':'Qui','Friday':'Sex','Saturday':'Sab','Sunday':'Dom'}
                hm['ordem']=hm['dia_semana'].map(do_map); hm['dia']=hm['dia_semana'].map(dn_map)
                hm_pv=hm.pivot_table(index='dia',columns='hora',values='qtd',fill_value=0)
                # Reordenar dias
                dias_ordem=['Seg','Ter','Qua','Qui','Sex','Sab','Dom']
                hm_pv=hm_pv.reindex([d for d in dias_ordem if d in hm_pv.index])
                fig=px.imshow(hm_pv,color_continuous_scale='Blues',aspect='auto',labels=dict(x='Hora',y='Dia',color='Respostas'))
                fig.update_layout(height=300,paper_bgcolor='#FFFFFF')
                st.plotly_chart(fig,use_container_width=True,key="eng_heatmap")
            # Metricas de retencao
            retorno=int((uc['qtd']>1).sum()); tx_ret=spct(retorno,len(uc))
            power_users=int((uc['qtd']>=10).sum())
            st.markdown(ibox("Tatico","Retencao",f"{tx_ret}% dos usuarios voltaram para 2+ avaliacoes. {power_users} power users (10+ avaliacoes). {'Boa retencao!' if tx_ret>40 else 'Melhorar retencao com notificacoes e incentivos.'}"),unsafe_allow_html=True)
        else: st.info("Dados de questionarios insuficientes para analise de retencao.")
    # --- TAB 3: NPS ---
    with t3:
        st.markdown('<div class="chart-title">Net Promoter Score (NPS)</div>',unsafe_allow_html=True)
        rn_nps=_nresp(rp)
        if len(rn_nps)>0:
            vals=rn_nps['valor']
            # Escala 1-9: Promotores 8-9, Neutros 6-7, Detratores 1-5
            promotores=int((vals>=8).sum()); neutros=int(((vals>=6)&(vals<8)).sum()); detratores=int((vals<6).sum())
            total_nps=promotores+neutros+detratores
            pct_p=spct(promotores,total_nps); pct_d=spct(detratores,total_nps)
            nps_score=round(pct_p-pct_d,1)
            c1,c2,c3,c4=st.columns(4)
            with c1:
                nps_color=CL['success'] if nps_score>50 else CL['orange'] if nps_score>0 else CL['danger']
                st.markdown(mcard(f"{nps_score}","NPS Score",c=nps_color),unsafe_allow_html=True)
            with c2: st.markdown(mcard(f"{pct_p}%","Promotores (8-9)",f"{promotores:,}",c=CL['success']),unsafe_allow_html=True)
            with c3: st.markdown(mcard(f"{spct(neutros,total_nps)}%","Neutros (6-7)",f"{neutros:,}",c=CL['warning']),unsafe_allow_html=True)
            with c4: st.markdown(mcard(f"{pct_d}%","Detratores (1-5)",f"{detratores:,}",c=CL['danger']),unsafe_allow_html=True)
            # Gauge NPS
            c1,c2=st.columns([1,1])
            with c1:
                fig=go.Figure(go.Indicator(mode="gauge+number+delta",value=nps_score,
                    title={'text':'NPS Score','font':{'size':14,'family':'Poppins','color':'#202124'}},
                    number={'font':{'family':'JetBrains Mono','size':36,'color':'#202124'}},
                    delta={'reference':0,'increasing':{'color':CL['success']},'decreasing':{'color':CL['danger']}},
                    gauge={'axis':{'range':[-100,100]},'bar':{'color':CL['primary']},
                        'steps':[{'range':[-100,0],'color':'#FEECEB'},{'range':[0,50],'color':'#FFF3E0'},{'range':[50,100],'color':'#E8F5E9'}],
                        'threshold':{'line':{'color':CL['danger'],'width':3},'thickness':.75,'value':0}}))
                fig.update_layout(height=280,margin=dict(l=20,r=20,t=50,b=20),paper_bgcolor='#FFFFFF')
                st.plotly_chart(fig,use_container_width=True,key="nps_gauge")
            with c2:
                # Distribuicao NPS
                fig=px.pie(values=[promotores,neutros,detratores],names=['Promotores','Neutros','Detratores'],
                    color_discrete_map={'Promotores':CL['success'],'Neutros':CL['warning'],'Detratores':CL['danger']},hole=.4)
                fig.update_layout(height=280,paper_bgcolor='#FFFFFF')
                st.plotly_chart(fig,use_container_width=True,key="nps_pie")
            # NPS por produto
            if 'nome_produto' in rn_nps.columns:
                st.markdown('<div class="chart-title">NPS por Produto (Top 15)</div>',unsafe_allow_html=True)
                nps_prod=[]
                for prd,grp in rn_nps.groupby('nome_produto'):
                    if len(grp)>=10:
                        v=grp['valor']; p_=spct(int((v>=8).sum()),len(v)); d_=spct(int((v<6).sum()),len(v))
                        nps_prod.append({'Produto':prd,'NPS':round(p_-d_,1),'N':len(v),'Media':round(v.mean(),2)})
                if nps_prod:
                    nps_df=pd.DataFrame(nps_prod).sort_values('NPS',ascending=False).head(15)
                    fig=px.bar(nps_df,x='NPS',y='Produto',orientation='h',color='NPS',
                        color_continuous_scale='RdYlGn',text='NPS')
                    fig.update_layout(height=max(300,len(nps_df)*30),yaxis_title="",paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',coloraxis_showscale=False)
                    fig.update_yaxes(autorange="reversed"); fig.update_traces(texttemplate='%{text:.1f}',textposition='outside')
                    st.plotly_chart(fig,use_container_width=True,key="nps_prod")
            zona='Excelente' if nps_score>75 else 'Muito Bom' if nps_score>50 else 'Bom' if nps_score>0 else 'Critico'
            st.markdown(ibox("Estrategico","Net Promoter Score",f"NPS = {nps_score} (Zona {zona}). {pct_p}% promotores vs {pct_d}% detratores. {'Manter o padrao de qualidade.' if nps_score>50 else 'Investir em melhorias para converter neutros em promotores.'}"),unsafe_allow_html=True)
        else: st.info("Dados insuficientes para calculo de NPS.")
    # --- TAB 4: ECONOMIA DE PONTOS ---
    with t4:
        st.markdown('<div class="chart-title">Economia de Pontos da Plataforma</div>',unsafe_allow_html=True)
        # Pontos distribuidos vs resgatados
        pts_dist=pts_total
        pts_resg=0
        if len(rg)>0 and len(bn)>0 and 'id_beneficio' in rg.columns and 'pontos_necessarios' in bn.columns:
            bn_pts=bn.set_index('id')['pontos_necessarios'].to_dict()
            rg_pts=rg['id_beneficio'].map(bn_pts)
            pts_resg=int(pd.to_numeric(rg_pts,errors='coerce').fillna(0).sum())
        pts_saldo=pts_dist-pts_resg
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(mcard(f"{pts_dist:,}","Pontos Distribuidos",c=CL['primary']),unsafe_allow_html=True)
        with c2: st.markdown(mcard(f"{pts_resg:,}","Pontos Resgatados",c=CL['orange']),unsafe_allow_html=True)
        with c3:
            tx_uso=spct(pts_resg,pts_dist) if pts_dist>0 else 0
            st.markdown(mcard(f"{tx_uso}%","Taxa de Uso",c=CL['teal']),unsafe_allow_html=True)
        with c4: st.markdown(mcard(f"{pts_saldo:,}","Saldo Circulante",c=CL['purple']),unsafe_allow_html=True)
        # Gauge de utilizacao
        c1,c2=st.columns(2)
        with c1:
            fig=go.Figure(go.Indicator(mode="gauge+number",value=tx_uso,
                title={'text':'Taxa de Utilizacao de Pontos (%)','font':{'size':13,'family':'Poppins','color':'#202124'}},
                number={'suffix':'%','font':{'family':'JetBrains Mono','size':32,'color':'#202124'}},
                gauge={'axis':{'range':[0,100]},'bar':{'color':CL['primary']},
                    'steps':[{'range':[0,30],'color':'#FEECEB'},{'range':[30,60],'color':'#FFF3E0'},{'range':[60,100],'color':'#E8F5E9'}]}))
            fig.update_layout(height=280,margin=dict(l=20,r=20,t=50,b=20),paper_bgcolor='#FFFFFF')
            st.plotly_chart(fig,use_container_width=True,key="pts_gauge")
        with c2:
            # Distribuicao de pontos por usuario
            if len(pt)>0 and 'id_usuario' in pt.columns and 'pontos' in pt.columns:
                usr_pts=pt.groupby('id_usuario')['pontos'].apply(lambda x: pd.to_numeric(x,errors='coerce').sum()).dropna()
                fig=px.histogram(x=usr_pts.values,nbins=30,color_discrete_sequence=[CL['primary']],
                    labels={'x':'Pontos Acumulados','y':'Usuarios'})
                fig.update_layout(height=280,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',title='Distribuicao de Pontos por Usuario')
                st.plotly_chart(fig,use_container_width=True,key="pts_hist")
        # Sankey: Fluxo de pontos
        if pts_dist>0:
            st.markdown('<div class="chart-title">Fluxo de Pontos (Sankey)</div>',unsafe_allow_html=True)
            labels=['Pontos Distribuidos','Em Circulacao','Resgatados']
            fig=go.Figure(go.Sankey(
                node=dict(pad=15,thickness=20,line=dict(color='#E8EAED',width=0.5),
                    label=labels,color=[CL['primary'],CL['teal'],CL['orange']]),
                link=dict(source=[0,0],target=[1,2],value=[pts_saldo,pts_resg],
                    color=['rgba(0,180,216,0.3)','rgba(255,149,0,0.3)'])))
            fig.update_layout(height=300,paper_bgcolor='#FFFFFF',font=dict(family='Inter',size=12,color='#202124'))
            st.plotly_chart(fig,use_container_width=True,key="pts_sankey")
        # Insight
        st.markdown(ibox("Estrategico","Economia de Pontos",f"{'Taxa de uso saudavel ({tx_uso}%). Pontos estao sendo consumidos adequadamente.' if tx_uso>30 else f'Baixa taxa de uso ({tx_uso}%). Usuarios acumulam pontos sem resgatar. Considerar: melhorar catalogo de beneficios, criar campanhas de resgate, notificar sobre saldo disponivel.'}"),unsafe_allow_html=True)

# ============================================================================
# PLACEHOLDER
# ============================================================================
def pg_placeholder(nome):
    st.markdown(f'<h2 class="sh">{nome}</h2>',unsafe_allow_html=True)
    st.info(f"Modulo **{nome}** sera implementado na proxima atualizacao. Os dados ja estao sendo carregados.")

# ============================================================================
# MAIN
# ============================================================================
def main():
    # Placeholder para loading screen (usa st.empty para controle de ciclo de vida)
    _loading_placeholder = st.empty()

    # Mostra loading screen APENAS se dados ainda nao carregaram
    if not st.session_state.get('loaded', False):
        _loading_placeholder.markdown(LOADING_SCREEN_HTML, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("""<div style="text-align:center;padding:20px 16px 12px">
            <div style="background:#0052CC;border-radius:10px;padding:12px 20px;margin:0 auto 8px;width:fit-content;box-shadow:0 2px 8px rgba(0,82,204,.25)">
            <span style="color:white;font-size:1.3rem;font-weight:700;font-family:'Poppins',sans-serif;letter-spacing:2px">FT</span></div>
            <div style="font-family:'Poppins',sans-serif;font-size:.72rem;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:#5E6368;margin-top:4px">Foodtest Analytics</div></div>""",unsafe_allow_html=True)
        st.markdown('<div style="height:1px;background:#E8EAED;margin:4px 16px 16px"></div>',unsafe_allow_html=True)
        if st.button("Recarregar Dados",use_container_width=True): st.session_state['loaded']=False; st.cache_data.clear(); st.cache_resource.clear()
        st.markdown('<p class="nav-section">Visao Geral</p>',unsafe_allow_html=True)
        page=st.radio("Navegacao",options=[
            "Dashboard Geral","Central de Insights",
            "--- ANALISE ---",
            "Respostas","Qualidade dos Dados",
            "Mapeamento de Pesquisas","Analise Demografica",
            "--- GESTAO ---",
            "Campanhas","Categorias e Subcategorias","Produtos","Marcas",
            "Parceiros","Gestao de Pesquisas","Beneficios e Resgates",
            "Empresas","Banners e Recomendados","Gestao de Testadores",
            "--- USUARIO ---",
            "Consulta Usuario",
            "--- ANALYTICS AVANCADO ---",
            "Analise Estatistica","Analise Exploratoria (EDA)",
            "Performance de Produtos","Engajamento e Gamificacao"
        ],label_visibility="collapsed",key="nav")
        # Handle section dividers
        if page and page.startswith("---"):
            st.session_state['nav'] = "Dashboard Geral"
            page = "Dashboard Geral"
        # Inject CSS to style section dividers as headers
        st.markdown("""<style>
        section[data-testid="stSidebar"] .stRadio label:has(div p:only-child) {cursor:default}
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:nth-child(3),
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:nth-child(8),
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:nth-child(19),
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:nth-child(21)
        {font-size:.62rem!important;font-weight:700!important;text-transform:uppercase;letter-spacing:1.2px;color:#9AA0A6!important;padding:16px 16px 6px!important;pointer-events:none;opacity:1;background:none!important;border:none!important}
        </style>""",unsafe_allow_html=True)
        st.markdown('<div style="height:1px;background:#E8EAED;margin:12px 16px"></div>',unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;font-size:.68rem;color:#9AA0A6;padding:8px 0;font-family:Inter,sans-serif">suporte@foodtest.com.br<br><span style="font-weight:600">v3.1-perf</span></div>',unsafe_allow_html=True)

    # Load data with progress bar
    if 'data' not in st.session_state or not st.session_state.get('loaded', False):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Step 1: Connection check
            status_text.text("Conectando ao banco de dados...")
            progress_bar.progress(0.05)
            get_db_engine()

            # Step 2: Load all tables
            status_text.text("Carregando tabelas...")
            progress_bar.progress(0.10)
            raw = load_all()
            progress_bar.progress(0.70)

            # Step 3: Enrich data
            status_text.text("Enriquecendo dados...")
            progress_bar.progress(0.85)
            data = enrich(raw)

            # Step 4: Finalize
            status_text.text("Finalizando...")
            progress_bar.progress(0.95)

            st.session_state['data'] = data
            st.session_state['loaded'] = True

            total = sum(len(df) for df in data.values() if isinstance(df, pd.DataFrame))
            progress_bar.progress(1.0)

            # Limpa os indicadores de progresso e loading screen
            progress_bar.empty()
            status_text.empty()
            _loading_placeholder.empty()

            if total == 0:
                st.warning("Nenhum dado encontrado.")
                return
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            _loading_placeholder.empty()
            st.error(f"Erro: {e}")
            return
    else:
        # Dados ja carregados - remove loading screen imediatamente
        _loading_placeholder.empty()

    data = st.session_state.get('data', {})

    # Header bar
    st.markdown(header_bar(), unsafe_allow_html=True)

    # Route
    R = {
        "Dashboard Geral": pg_overview, "Respostas": pg_respostas,
        "Qualidade dos Dados": pg_qualidade,
        "Consulta Usuario": pg_usuario, "Mapeamento de Pesquisas": pg_mapeamento,
        "Analise Demografica": pg_demografica,
        "Campanhas": pg_campanhas, "Categorias e Subcategorias": pg_categorias,
        "Produtos": pg_produtos, "Marcas": pg_marcas, "Parceiros": pg_parceiros,
        "Gestao de Pesquisas": pg_pesquisas, "Beneficios e Resgates": pg_beneficios,
        "Empresas": pg_empresas, "Banners e Recomendados": pg_banners,
        "Gestao de Testadores": pg_testadores, "Central de Insights": pg_insights,
        "Analise Estatistica": pg_estatistica, "Analise Exploratoria (EDA)": pg_eda,
        "Performance de Produtos": pg_performance, "Engajamento e Gamificacao": pg_engajamento,
    }
    fn = R.get(page)
    if fn:
        fn(data)
    else:
        pg_placeholder(page)

if __name__ == "__main__":
    main()