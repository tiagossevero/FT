"""
🍽️ FOODTEST - Dashboard Completo de Analytics v2.0
Plataforma de Análise Sensorial, Gestão e Inteligência de Dados
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

# ============================================================================
# CONFIG
# ============================================================================
CL = {
    'primary':'#307FE2','secondary':'#FF6B6B','accent1':'#4ECDC4','accent2':'#45B7D1',
    'success':'#2ECC71','warning':'#F1C40F','danger':'#E74C3C','purple':'#9B59B6',
    'dark':'#2C3E50','orange':'#F7931E','teal':'#14B8A6','pink':'#EC4899',
}
PAL = ['#307FE2','#FF6B6B','#4ECDC4','#45B7D1','#96CEB4','#FFEAA7','#DDA0DD','#98D8C8','#F39C12','#9B59B6','#1ABC9C','#E74C3C','#3498DB','#2ECC71','#E67E22']
CARD_COLORS = ['#307FE2','#4ECDC4','#45B7D1','#F7931E','#9B59B6','#14B8A6','#2ECC71','#EC4899','#E74C3C','#FF6B6B']
st.set_page_config(page_title="Foodtest Analytics", page_icon="🍽️", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
:root,html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"]{
--bg:#ffffff!important;--card:#ffffff!important;--text:#1a1a2e!important;--muted:#6b7280!important;
--border:#e5e7eb!important;--sidebar-bg:#ffffff!important;--primary:#307FE2!important;
--primary-color:#307FE2!important;--background-color:#ffffff!important;
--secondary-background-color:#f8f9fa!important;--text-color:#1a1a2e!important;
--font:'Inter',sans-serif!important;
color-scheme:light!important;
}
html,body,.main,.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stBottomBlockContainer"],
[data-testid="stMainBlockContainer"],
.block-container,
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"]{background:#ffffff!important;background-color:#ffffff!important;color:#1a1a2e!important}
.stApp{font-family:'Inter',sans-serif!important}
h1,h2,h3,h4{font-family:'Inter',sans-serif!important;font-weight:700!important;color:#1a1a2e!important}
p,span,label,li,td,th{color:#1a1a2e!important}
section[data-testid="stSidebar"],
section[data-testid="stSidebar"]>div,
section[data-testid="stSidebar"]>div>div,
section[data-testid="stSidebar"]>div>div>div{background:#ffffff!important;background-color:#ffffff!important}
section[data-testid="stSidebar"]{border-right:1px solid #e5e7eb!important}
section[data-testid="stSidebar"] *{color:#1a1a2e!important}
section[data-testid="stSidebar"] .stRadio label{padding:6px 12px;border-radius:8px;transition:background .2s;font-size:.85rem!important}
section[data-testid="stSidebar"] .stRadio label:hover{background:rgba(48,127,226,.15)}
section[data-testid="stSidebar"] .stRadio label[data-checked="true"]{background:rgba(48,127,226,.15);color:#307FE2!important;font-weight:600}
section[data-testid="stSidebar"] .stTextInput input{background:#f9fafb!important;border:1px solid #e5e7eb!important;color:#1a1a2e!important}
section[data-testid="stSidebar"] .stButton button{background:linear-gradient(135deg,#307FE2,#4ECDC4)!important;color:#fff!important;border:none!important;border-radius:8px!important}
.mc{background:#ffffff;border-radius:12px;padding:18px 20px;box-shadow:0 1px 3px rgba(0,0,0,.06);border-left:4px solid #307FE2;transition:box-shadow .2s}
.mc:hover{box-shadow:0 4px 12px rgba(0,0,0,.1)}
.mv{font-family:'Inter';font-size:1.75rem;font-weight:700;color:#1a1a2e!important;margin:0;line-height:1.2}
.ml{font-size:.75rem;color:#6b7280!important;text-transform:uppercase;letter-spacing:.5px;margin-top:4px;font-weight:500}
.md{font-size:.75rem;padding:2px 8px;border-radius:6px;display:inline-block;margin-top:4px;font-weight:600}
.dp{background:rgba(46,204,113,.12);color:#2ECC71!important}.dn{background:rgba(231,76,60,.12);color:#E74C3C!important}
.sh{color:#1a1a2e!important;font-size:1.3rem;font-weight:700;margin:1.2rem 0 .8rem;font-family:'Inter';background:none!important;-webkit-text-fill-color:#1a1a2e!important}
.sh-sub{color:#6b7280!important;font-size:.9rem;font-weight:400;margin-top:-8px;margin-bottom:16px}
.chart-card{background:#ffffff!important;border-radius:12px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,.06);margin-bottom:16px}
.chart-title{font-size:.95rem;font-weight:600;color:#1a1a2e!important;margin-bottom:12px}
.ib{background:#f8f9fa!important;border-radius:12px;padding:18px;color:#1a1a2e!important;margin:10px 0;border:1px solid #e5e7eb}
.ib h4{color:#307FE2!important;margin-bottom:6px;font-size:.9rem;font-weight:600}.ib p{color:#4b5563!important;font-size:.85rem;line-height:1.6}
.it{display:inline-block;padding:3px 10px;border-radius:6px;font-size:.65rem;font-weight:700;text-transform:uppercase;margin-bottom:8px;letter-spacing:.5px}
.ts{background:rgba(139,92,246,.12);color:#7c3aed!important}.tt{background:rgba(59,130,246,.12);color:#2563eb!important}.to{background:rgba(16,185,129,.12);color:#059669!important}
.stSelectbox div[data-baseweb="select"]>div,
.stMultiSelect div[data-baseweb="select"]>div{background:#f9fafb!important;color:#1a1a2e!important;border-color:#e5e7eb!important}
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input{background:#f9fafb!important;color:#1a1a2e!important;border-color:#e5e7eb!important}
[data-testid="stExpander"]{background:#ffffff!important;border:1px solid #e5e7eb!important;border-radius:8px!important}
[data-testid="stExpander"] summary span{color:#1a1a2e!important}
[data-testid="stDataFrame"]{background:#ffffff!important}
[data-testid="stMetric"]{background:#ffffff!important}
[data-testid="stMetricValue"]{color:#1a1a2e!important}
[data-testid="stMetricLabel"]{color:#6b7280!important}
[data-testid="stMarkdownContainer"]{color:#1a1a2e!important}
[data-testid="stMarkdownContainer"] p{color:#1a1a2e!important}
div[data-baseweb="popover"] ul{background:#ffffff!important}
div[data-baseweb="menu"] li{color:#1a1a2e!important}
div[data-baseweb="menu"] li:hover{background:#f0f2f5!important}
[data-baseweb="select"] [data-baseweb="tag"]{background:#e8f0fe!important;color:#307FE2!important}
[data-baseweb="input"]{background:#f9fafb!important;color:#1a1a2e!important}
[data-baseweb="base-input"]{background:#f9fafb!important}
.stAlert{background:#f8f9fa!important;color:#1a1a2e!important}
.stDataFrame table{background:#ffffff!important;color:#1a1a2e!important}
.stDataFrame th{background:#f8f9fa!important;color:#1a1a2e!important}
.stDataFrame td{background:#ffffff!important;color:#1a1a2e!important}
#MainMenu{visibility:hidden}footer{visibility:hidden}
.stTabs [data-baseweb="tab-list"]{gap:6px;border-bottom:2px solid #e5e7eb}
.stTabs [data-baseweb="tab"]{background:transparent;border-radius:8px 8px 0 0;padding:10px 20px;border:none;font-weight:500;color:#6b7280}
.stTabs [aria-selected="true"]{background:#ffffff!important;color:#307FE2!important;border-bottom:2px solid #307FE2!important;font-weight:600}
.divider{height:1px;background:#e5e7eb;margin:20px 0}
.page-header{margin-bottom:24px}
.page-header h2{margin-bottom:2px!important}
</style>""", unsafe_allow_html=True)

# ============================================================================
# UI COMPONENTS
# ============================================================================
def mcard(v, l, d=None, dt='positive', c=None):
    bc = c if c else CL['primary']
    dh = f'<span class="md {"dp" if dt=="positive" else "dn"}">{d}</span>' if d else ""
    return f'<div class="mc" style="border-left:4px solid {bc}"><p class="mv">{v}</p><p class="ml">{l}</p>{dh}</div>'

def gauge(v, t, mx=100):
    fig = go.Figure(go.Indicator(mode="gauge+number",value=v,title={'text':t,'font':{'size':14,'family':'Inter'}},
        gauge={'axis':{'range':[0,mx]},'bar':{'color':CL['primary']},
        'steps':[{'range':[0,40],'color':'#fee2e2'},{'range':[40,60],'color':'#fef3c7'},{'range':[60,80],'color':'#d1fae5'},{'range':[80,100],'color':'#a7f3d0'}],
        'threshold':{'line':{'color':'red','width':4},'thickness':.75,'value':60}}))
    fig.update_layout(height=220,margin=dict(l=20,r=20,t=40,b=20),paper_bgcolor='#ffffff',font_family='Inter',font_color='#1a1a2e')
    return fig

def ibox(tag, title, text):
    tc = {'Estratégico':'ts','Tático':'tt','Operacional':'to'}.get(tag,'tt')
    return f'<div class="ib"><span class="it {tc}">{tag}</span><h4>{title}</h4><p>{text}</p></div>'

def spct(p, t): return round(p/t*100,1) if t>0 else 0

def hbar(xv, yv, cs='Blues', **kw):
    df=pd.DataFrame({'v':list(xv),'n':list(yv)})
    return px.bar(df,x='v',y='n',orientation='h',color='v',color_continuous_scale=cs,**kw)

def chart_layout(fig, h=400):
    fig.update_layout(height=h,paper_bgcolor='#ffffff',plot_bgcolor='#ffffff',
        font_family='Inter',font_color='#374151',margin=dict(l=10,r=10,t=40,b=10),
        xaxis=dict(gridcolor='#f0f0f0',zerolinecolor='#e5e7eb'),
        yaxis=dict(gridcolor='#f0f0f0',zerolinecolor='#e5e7eb'))
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
        fig.update_layout(paper_bgcolor='#ffffff',plot_bgcolor='#ffffff')
        add_labels(fig)
    except: pass
    return _st_plotly(fig,**kw)
st.plotly_chart=_plotly_white

def section_header(title, subtitle=None):
    h = f'<div class="page-header"><h2 class="sh">{title}</h2>'
    if subtitle: h += f'<p class="sh-sub">{subtitle}</p>'
    h += '</div>'
    return h

# ============================================================================
# DATA LOADER (TODAS AS TABELAS)
# ============================================================================
@st.cache_data(ttl=3600)
def find_f(pat, d="."):
    f = glob.glob(os.path.join(d, f"{pat}[0-9]*.txt"))
    return max(f, key=os.path.getmtime) if f else None

@st.cache_data(ttl=3600)
def load_t(fp):
    if fp is None: return pd.DataFrame()
    try:
        with open(fp,'r',encoding='utf-8') as f: lines=f.readlines()
        fl = [l for l in lines if l.strip().replace('|','').replace('-','').strip()!='']
        df = pd.read_csv(StringIO(''.join(fl)),sep='|',skipinitialspace=True,dtype=str,quoting=csv.QUOTE_NONE)
        df = df.loc[:,~df.columns.str.contains('^Unnamed')]; df.columns=df.columns.str.strip()
        df = df.loc[:, df.columns != '']
        for c in df.columns:
            df[c]=df[c].astype(str).str.strip()
            df[c]=df[c].str.replace('\\"','"',regex=False)
            m=df[c].str.match(r'^".*"$',na=False); df.loc[m,c]=df.loc[m,c].str[1:-1]
        for c in [c for c in df.columns if c.startswith('id') or c=='id']:
            df[c]=pd.to_numeric(df[c].str.replace('.','',regex=False),errors='coerce')
        return df
    except: return pd.DataFrame()

def pj(v):
    if pd.isna(v) or v in('','""','nan','None'): return {}
    try:
        if isinstance(v,str): v=v.strip('"')
        return json.loads(v)
    except: return {}

@st.cache_data(ttl=3600)
def load_all(dr):
    P = {
        'categoria':'categoria_produto_','subcategoria':'subcategoria_produto_',
        'produto':'produto_','marca':'marca_','parceiro':'parceiro_',
        'produto_parceiro':'produto_parceiro_','banner_home':'banner_home_',
        'prod_recomendado':'pesquisa_produto_recomendado_','campanha':'campanha_',
        'pesq_produto':'pesquisa_produto_','pesq_subcategoria':'pesquisa_subcategoria_',
        'sessao':'sessao_pesquisa_','pergunta':'pergunta_pesquisa_',
        'resp_pergunta':'resposta_pergunta_pesquisa_',
        'resp_questionario':'resposta_questionario_usuario_',
        'comentarios':'comentarios_','beneficio':'beneficio_',
        'resgate':'resgate_beneficio_','pontos':'pontos_usuario_',
        'empresa':'empresa_','usr_empresa':'usuario_empresa_',
        'grupo_empresa':'grupo_usuario_empresa_','usuario':'usuario_',
        'estado':'estado_','cidade':'cidade_',
        'prod_nao_cadastrado':'produto_nao_cadastrado_','notificacoes':'notificacoes_',
    }
    return {k: load_t(find_f(v, dr)) for k, v in P.items()}

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
            _gm={1:'Masculino',2:'Feminino',3:'Outro',4:'Prefiro não dizer',1.0:'Masculino',2.0:'Feminino',3.0:'Outro',4.0:'Prefiro não dizer'}
            _rm={1:'Até R$ 2.640',2:'R$ 2.641-5.280',3:'R$ 5.281-10.560',4:'Acima de R$ 10.560',1.0:'Até R$ 2.640',2.0:'R$ 2.641-5.280',3.0:'R$ 5.281-10.560',4.0:'Acima de R$ 10.560'}
            us['genero']=dp.apply(lambda x:_gm.get(x.get('opcao_genero'),x.get('opcao_genero')))
            us['ano_nascimento']=dp.apply(lambda x:x.get('ano_nascimento'))
            us['faixa_renda']=dp.apply(lambda x:_rm.get(x.get('opcao_faixa_renda_mensal'),x.get('opcao_faixa_renda_mensal')))
            a=datetime.now().year; us['idade']=us['ano_nascimento'].apply(lambda x:a-int(x) if pd.notna(x) and str(x).isdigit() else None)
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
    s['classif']=s['score'].apply(lambda x:'🟢 Muito Confiável' if x>=80 else '🟡 Confiável' if x>=60 else '🟠 Atenção' if x>=40 else '🔴 Suspeito' if x>=20 else '⛔ Muito Suspeito')
    s['nome_usuario']=s['id_usuario'].map(du)
    return s.sort_values('score')

# ============================================================================
# PG1: VISÃO GERAL
# ============================================================================
def pg_overview(data):
    st.markdown(section_header("Dashboard Geral","Visao consolidada da plataforma Foodtest"),unsafe_allow_html=True)
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
    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)
    # Charts Row 1: Tendencia + Genero
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Tendencia Mensal de Respostas</div>',unsafe_allow_html=True)
        if len(rq)>0 and 'createdAt' in rq.columns:
            mn=rq.groupby(rq['createdAt'].dt.to_period('M')).size().reset_index(name='qtd')
            mn.columns=['mes','qtd']; mn['mes']=mn['mes'].astype(str)
            fig=px.bar(mn,x='mes',y='qtd',color_discrete_sequence=[CL['primary']])
            chart_layout(fig,350); fig.update_layout(xaxis_tickangle=45,xaxis_title="",yaxis_title="")
            st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Distribuicao por Genero</div>',unsafe_allow_html=True)
        if 'genero' in us.columns and len(us['genero'].dropna())>0:
            gc=us['genero'].value_counts()
            fig=px.pie(values=gc.values.tolist(),names=gc.index.tolist(),color_discrete_sequence=['#307FE2','#FF6B6B','#4ECDC4','#F7931E'],hole=.45)
            chart_layout(fig,350); st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    # Charts Row 2: Faixa Etaria + Top Categorias
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Faixa Etaria dos Testadores</div>',unsafe_allow_html=True)
        if 'idade' in us.columns and us['idade'].notna().any():
            dv=us[us['idade'].notna()&(us['idade']>0)].copy()
            if len(dv)>0:
                dv['fx']=pd.cut(dv['idade'].astype(float),bins=[0,25,35,45,55,65,100],labels=['18-25','26-35','36-45','46-55','56-65','65+'])
                fc=dv['fx'].value_counts().sort_index()
                fig=px.bar(x=fc.index.astype(str).tolist(),y=fc.values.tolist(),color_discrete_sequence=[CL['primary']])
                chart_layout(fig,350); fig.update_layout(xaxis_title="",yaxis_title="")
                st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Top 10 Categorias</div>',unsafe_allow_html=True)
        if len(rq)>0 and 'nome_categoria' in rq.columns and rq['nome_categoria'].notna().any():
            cc=rq['nome_categoria'].value_counts().head(10)
            fig=hbar(cc.values,cc.index,cs='Blues')
            chart_layout(fig,350); fig.update_layout(yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    # Charts Row 3: Subcategorias + Marcas
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Top 10 Subcategorias</div>',unsafe_allow_html=True)
        if len(rq)>0 and 'nome_subcategoria' in rq.columns:
            ts=rq['nome_subcategoria'].value_counts().head(10)
            fig=hbar(ts.values,ts.index,cs='Blues')
            chart_layout(fig,350); fig.update_layout(yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Top 10 Marcas</div>',unsafe_allow_html=True)
        if len(pr)>0 and 'nome_marca' in pr.columns:
            tm=pr['nome_marca'].value_counts().head(10)
            fig=hbar(tm.values,tm.index,cs='Greens')
            chart_layout(fig,350); fig.update_layout(yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    # Charts Row 4: Estado + Top Testadores
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Distribuicao por Estado</div>',unsafe_allow_html=True)
        if 'nome_estado' in us.columns:
            ec=us['nome_estado'].value_counts().head(10)
            fig=hbar(ec.values,ec.index,cs='Purples')
            chart_layout(fig,350); fig.update_layout(yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Top 10 Testadores</div>',unsafe_allow_html=True)
        if len(rq)>0 and 'nome_usuario' in rq.columns:
            tu=rq.groupby('nome_usuario').size().sort_values(ascending=False).head(10)
            fig=hbar(tu.values,tu.index,cs='Blues')
            chart_layout(fig,350); fig.update_layout(yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    # Insights
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
    t1,t2,t3,t4=st.tabs(["📋 Pergunta","📦 Produto","👤 Usuário","🔍 Explorar"])
    with t1:
        if 'titulo_pergunta' in rp.columns:
            ps=rp.groupby('titulo_pergunta').agg({'id':'count','id_usuario':'nunique'}).rename(columns={'id':'resp','id_usuario':'usr'}).sort_values('resp',ascending=False)
            b=st.text_input("🔍 Buscar:",key="bp")
            pf=[p for p in ps.index if b.lower() in str(p).lower()] if b else ps.index[:20].tolist()
            if pf:
                sel=st.selectbox("Selecione:",pf,key="sp")
                if sel:
                    rs=rp[rp['titulo_pergunta']==sel]; st.metric("Respostas",f"{len(rs):,}")
                    if 'resposta' in rs.columns:
                        cl=rs['resposta'].astype(str).str.replace('"','').str.strip(); nm=pd.to_numeric(cl,errors='coerce')
                        if nm.notna().sum()>len(rs)*.5:
                            c1,c2=st.columns(2)
                            with c1:
                                fig=px.histogram(x=nm.dropna(),nbins=9,color_discrete_sequence=[CL['primary']]); fig.update_layout(height=350)
                                st.plotly_chart(fig,use_container_width=True)
                            with c2: st.dataframe(pd.DataFrame({'Métrica':['Média','Mediana','DP','Mín','Máx'],'Valor':[f"{nm.mean():.2f}",f"{nm.median():.2f}",f"{nm.std():.2f}",f"{nm.min():.0f}",f"{nm.max():.0f}"]}),hide_index=True)
                        else:
                            rc=cl.value_counts().head(15)
                            fig=hbar(rc.values,rc.index,cs='Blues')
                            fig.update_layout(height=400,coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                            st.plotly_chart(fig,use_container_width=True)
    with t2:
        if 'nome_produto' in rp.columns:
            pp=rp.groupby('nome_produto').size().sort_values(ascending=False).head(20)
            fig=hbar(pp.values,pp.index,cs='Greens')
            fig.update_layout(height=500,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True)
    with t3:
        if 'id_usuario' in rp.columns:
            us=rp.groupby('id_usuario').agg({'id':'count','id_produto':'nunique'}).rename(columns={'id':'resp','id_produto':'prod'})
            if 'nome_usuario' in rp.columns: us=us.join(rp.groupby('id_usuario')['nome_usuario'].first())
            us=us.sort_values('resp',ascending=False)
            fig=hbar(us.head(15)['resp'].values,us.head(15)['nome_usuario'].values if 'nome_usuario' in us.columns else us.head(15).index.astype(str),cs='Blues')
            fig.update_layout(height=450,coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True)
    with t4:
        c1,c2,c3=st.columns(3)
        with c1: fp=st.selectbox("📦 Produto:",['Todos']+(rp['nome_produto'].dropna().unique().tolist() if 'nome_produto' in rp.columns else []),key="fpe")
        with c2: fu=st.selectbox("👤 Usuário:",['Todos']+(rp['nome_usuario'].dropna().unique().tolist()[:100] if 'nome_usuario' in rp.columns else []),key="fue")
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
        cm={'🟢 Muito Confiável':CL['success'],'🟡 Confiável':CL['warning'],'🟠 Atenção':'#E67E22','🔴 Suspeito':CL['danger'],'⛔ Muito Suspeito':'#8E44AD'}
        fig=px.pie(values=cc.values.tolist(),names=cc.index.tolist(),color=cc.index.tolist(),color_discrete_map=cm,hole=.4)
        fig.update_layout(height=400); st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="chart-title">Top 10 Suspeitos</div>',unsafe_allow_html=True)
    top=sc.nsmallest(10,'score')
    fig=px.bar(top,x='score',y='nome_usuario',orientation='h',color='score',color_continuous_scale='RdYlGn')
    fig.update_layout(height=400,coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
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
    sel=st.selectbox("🔍 Selecione:",ul['d'].tolist(),key="su")
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
    t1,t2,t3,t4=st.tabs(["📁 Categoria","📂 Subcategoria","📦 Produto","📅 Temporal"])
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
    t1,t2=st.tabs(["📋 Lista de Campanhas","📅 Timeline"])
    with t1:
        disp=ca.copy()
        if 'data_fim' in disp.columns:
            disp['status']=disp['data_fim'].apply(lambda x:'🟢 Ativa' if pd.notna(x) and x>=hoje else '🔴 Encerrada')
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
    t1,t2,t3=st.tabs(["📁 Categorias","📂 Subcategorias","🌳 Treemap"])
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
    t1,t2,t3=st.tabs(["📋 Catálogo","📊 Análise","🔎 Detalhe"])
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
    t1,t2=st.tabs(["📋 Lista","📊 Análise"])
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
    t1,t2=st.tabs(["📋 Lista","🔗 Vínculos"])
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
    t1,t2,t3,t4=st.tabs(["📦 Por Produto","📂 Por Subcategoria","📋 Sessões","❓ Perguntas"])
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
    t1,t2,t3=st.tabs(["🎁 Catálogo","📊 Resgates","📈 Dashboard"])
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
    t1,t2,t3=st.tabs(["📋 Lista","📊 Análise","👥 Usuários"])
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
    t1,t2=st.tabs(["🏠 Banners","⭐ Recomendados"])
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
    t1,t2,t3,t4=st.tabs(["📋 Base","🗺️ Geografia","📈 Evolução","🎯 Cohorts"])
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
1. {'✅' if spct(cc,nu)>70 else '⚠️'} Completude de cadastros ({spct(cc,nu)}%)
2. {'✅' if nq>0 and spct(rq['id_usuario'].nunique(),nu)>30 else '⚠️'} Taxa de ativação ({spct(rq['id_usuario'].nunique(),nu) if nq>0 and 'id_usuario' in rq.columns else 0}%)
3. {'✅' if np_>0 and nq>0 and 'id_produto' in rq.columns and spct(rq['id_produto'].nunique(),np_)>50 else '⚠️'} Cobertura de produtos ({spct(rq['id_produto'].nunique(),np_) if np_>0 and nq>0 and 'id_produto' in rq.columns else 0}%)
""")

# ============================================================================
# PLACEHOLDER
# ============================================================================
def pg_placeholder(nome):
    st.markdown(f'<h2 class="sh">{nome}</h2>',unsafe_allow_html=True)
    st.info(f"🚧 Módulo **{nome}** será implementado na próxima atualização. Os dados já estão sendo carregados.")

# ============================================================================
# MAIN
# ============================================================================
def main():
    with st.sidebar:
        st.markdown("""<div style="text-align:center;padding:1.2rem 0 .8rem">
            <div style="background:linear-gradient(135deg,#307FE2,#4ECDC4);border-radius:12px;padding:14px;margin:0 auto 10px;width:fit-content">
            <span style="color:white;font-size:1.5rem;font-weight:800;font-family:'Inter';letter-spacing:2px">FT</span></div>
            <div style="color:#6b7280;font-size:.7rem;letter-spacing:1px;text-transform:uppercase">Foodtest Analytics</div></div>""",unsafe_allow_html=True)
        st.markdown('<div style="height:1px;background:#e5e7eb;margin:8px 0 16px"></div>',unsafe_allow_html=True)
        data_dir=st.text_input("Diretório:",value=".",help="Pasta com os .txt",label_visibility="collapsed")
        if st.button("Recarregar Dados",use_container_width=True): st.session_state['loaded']=False; st.cache_data.clear()
        st.markdown('<div style="height:1px;background:#e5e7eb;margin:12px 0"></div>',unsafe_allow_html=True)
        page=st.radio("Navegacao",options=[
            "📊 Dashboard Geral","📝 Respostas","🔍 Qualidade dos Dados",
            "👤 Consulta Usuário","📂 Mapeamento de Pesquisas","👥 Análise Demográfica",
            "📢 Campanhas","📂 Categorias & Subcategorias","📦 Produtos","🏷️ Marcas",
            "🤝 Parceiros","🔬 Gestão de Pesquisas","🎁 Benefícios & Resgates",
            "🏢 Empresas","🏠 Banners & Recomendados","👥 Gestão de Testadores","🧠 Central de Insights"
        ],label_visibility="collapsed",key="nav")
        st.markdown('<div style="height:1px;background:#e5e7eb;margin:12px 0"></div>',unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;font-size:.7rem;color:#9ca3af;padding:8px 0">suporte@foodtest.com.br<br>v2.0</div>',unsafe_allow_html=True)
    # Load
    if 'data' not in st.session_state or not st.session_state.get('loaded',False):
        with st.spinner("Carregando dados..."):
            try:
                raw=load_all(data_dir); data=enrich(raw)
                st.session_state['data']=data; st.session_state['loaded']=True
                total=sum(len(df) for df in data.values() if isinstance(df,pd.DataFrame))
                if total==0: st.warning("Nenhum dado encontrado."); return
            except Exception as e: st.error(f"Erro: {e}"); return
    data=st.session_state.get('data',{})
    # Route
    R={
        "📊 Dashboard Geral":pg_overview,"📝 Respostas":pg_respostas,
        "🔍 Qualidade dos Dados":pg_qualidade,
        "👤 Consulta Usuário":pg_usuario,"📂 Mapeamento de Pesquisas":pg_mapeamento,
        "👥 Análise Demográfica":pg_demografica,
        "📢 Campanhas":pg_campanhas,"📂 Categorias & Subcategorias":pg_categorias,
        "📦 Produtos":pg_produtos,"🏷️ Marcas":pg_marcas,"🤝 Parceiros":pg_parceiros,
        "🔬 Gestão de Pesquisas":pg_pesquisas,"🎁 Benefícios & Resgates":pg_beneficios,
        "🏢 Empresas":pg_empresas,"🏠 Banners & Recomendados":pg_banners,
        "👥 Gestão de Testadores":pg_testadores,"🧠 Central de Insights":pg_insights,
    }
    fn=R.get(page)
    if fn: fn(data)
    else: pg_placeholder(page)

if __name__=="__main__":
    main()