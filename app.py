"""
🍽️ FOODTEST - Dashboard Completo de Analytics v2.0
Plataforma de Análise Sensorial, Gestão e Inteligência de Dados
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json, os, glob
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
st.set_page_config(page_title="Foodtest Analytics", page_icon="🍽️", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@400;500;700&display=swap');
.main{background:linear-gradient(135deg,#f8fafc,#e2e8f0)}.stApp{font-family:'DM Sans',sans-serif}
h1,h2,h3{font-family:'Space Grotesk',sans-serif!important;font-weight:700!important}
.mc{background:linear-gradient(135deg,#fff,#f8fafc);border-radius:16px;padding:20px;box-shadow:0 4px 20px rgba(0,0,0,.08);border:1px solid rgba(48,127,226,.1);transition:transform .3s,box-shadow .3s}
.mc:hover{transform:translateY(-3px)}.mv{font-family:'Space Grotesk';font-size:2rem;font-weight:700;color:#307FE2;margin:0;line-height:1.2}
.ml{font-size:.8rem;color:#64748b;text-transform:uppercase;letter-spacing:.5px;margin-top:6px}
.md{font-size:.8rem;padding:3px 8px;border-radius:8px;display:inline-block;margin-top:6px}
.dp{background:rgba(46,204,113,.15);color:#2ECC71}.dn{background:rgba(231,76,60,.15);color:#E74C3C}
.sh{background:linear-gradient(90deg,#307FE2,#4ECDC4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:1.4rem;font-weight:700;margin:1.5rem 0 1rem;font-family:'Space Grotesk'}
.ib{background:linear-gradient(135deg,#1e293b,#334155);border-radius:14px;padding:18px;color:#fff;margin:12px 0}
.ib h4{color:#60a5fa;margin-bottom:8px;font-size:.9rem}.ib p{color:#e2e8f0;font-size:.85rem;line-height:1.5}
.it{display:inline-block;padding:2px 10px;border-radius:10px;font-size:.65rem;font-weight:700;text-transform:uppercase;margin-bottom:6px}
.ts{background:rgba(139,92,246,.3);color:#c4b5fd}.tt{background:rgba(59,130,246,.3);color:#93c5fd}.to{background:rgba(16,185,129,.3);color:#6ee7b7}
#MainMenu{visibility:hidden}footer{visibility:hidden}
.stTabs [data-baseweb="tab-list"]{gap:8px}.stTabs [data-baseweb="tab"]{background:#fff;border-radius:8px;padding:10px 20px;border:1px solid #e2e8f0}
.stTabs [aria-selected="true"]{background:linear-gradient(90deg,#307FE2,#4ECDC4);color:#fff!important}
</style>""", unsafe_allow_html=True)

# ============================================================================
# UI COMPONENTS
# ============================================================================
def mcard(v, l, d=None, dt='positive', c=None):
    cs = f"color:{c};" if c else "color:#307FE2;"
    dh = f'<span class="md {"dp" if dt=="positive" else "dn"}">{d}</span>' if d else ""
    return f'<div class="mc"><p class="mv" style="{cs}">{v}</p><p class="ml">{l}</p>{dh}</div>'

def gauge(v, t, mx=100):
    fig = go.Figure(go.Indicator(mode="gauge+number",value=v,title={'text':t,'font':{'size':14}},
        gauge={'axis':{'range':[0,mx]},'bar':{'color':CL['primary']},
        'steps':[{'range':[0,40],'color':'#fee2e2'},{'range':[40,60],'color':'#fef3c7'},{'range':[60,80],'color':'#d1fae5'},{'range':[80,100],'color':'#a7f3d0'}],
        'threshold':{'line':{'color':'red','width':4},'thickness':.75,'value':60}}))
    fig.update_layout(height=220,margin=dict(l=20,r=20,t=40,b=20),paper_bgcolor='rgba(0,0,0,0)')
    return fig

def ibox(tag, title, text):
    tc = {'Estratégico':'ts','Tático':'tt','Operacional':'to'}.get(tag,'tt')
    return f'<div class="ib"><span class="it {tc}">{tag}</span><h4>💡 {title}</h4><p>{text}</p></div>'

def spct(p, t): return round(p/t*100,1) if t>0 else 0

# ============================================================================
# DATA LOADER (TODAS AS TABELAS)
# ============================================================================
@st.cache_data(ttl=3600)
def find_f(pat, d="."): 
    f = glob.glob(os.path.join(d, f"{pat}*.txt"))
    return max(f, key=os.path.getmtime) if f else None

@st.cache_data(ttl=3600)
def load_t(fp):
    if fp is None: return pd.DataFrame()
    try:
        with open(fp,'r',encoding='utf-8') as f: lines=f.readlines()
        fl = [l for l in lines if l.strip().replace('|','').replace('-','').strip()!='']
        df = pd.read_csv(StringIO(''.join(fl)),sep='|',skipinitialspace=True)
        df = df.loc[:,~df.columns.str.contains('^Unnamed')]; df.columns=df.columns.str.strip()
        for c in df.select_dtypes(include=['object']).columns: df[c]=df[c].astype(str).str.strip()
        for c in [c for c in df.columns if c.startswith('id') or c=='id']:
            df[c]=pd.to_numeric(df[c].astype(str).str.replace('.','',regex=False).str.strip(),errors='coerce')
        return df
    except: return pd.DataFrame()

def pj(v):
    if pd.isna(v) or v in('','""','nan'): return {}
    try:
        if isinstance(v,str): v=v.strip('"').replace('""','"')
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
    idv = set(d['usuario']['id'].tolist()) if len(d['usuario'])>0 and 'id' in d['usuario'].columns else set()
    # resp_questionario
    rq=d['resp_questionario']
    if len(rq)>0:
        if 'id_usuario' in rq.columns and idv: rq=rq[rq['id_usuario'].isin(idv)]
        for c,dk in [('id_usuario','usuario'),('id_produto','produto'),('id_pesquisa_subcategoria','subcategoria')]:
            if c in rq.columns: rq[f'nome_{dk}']=rq[c].map(di.get(dk,{}))
        if 'id_pesquisa_subcategoria' in rq.columns:
            rq['id_categoria']=rq['id_pesquisa_subcategoria'].map(dsc); rq['nome_categoria']=rq['id_categoria'].map(di['categoria'])
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
            us['genero']=dp.apply(lambda x:x.get('opcao_genero'))
            us['ano_nascimento']=dp.apply(lambda x:x.get('ano_nascimento'))
            us['faixa_renda']=dp.apply(lambda x:x.get('opcao_faixa_renda_mensal'))
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
    st.markdown('<h2 class="sh">📊 Dashboard Geral da Plataforma</h2>',unsafe_allow_html=True)
    us,pr,rp,rq=data['usuario'],data['produto'],data['resp_pergunta'],data['resp_questionario']
    ca,em=data['campanha'],data['empresa']
    nu,nq,nr=len(us),len(rq),len(rp)
    pts=int(rq['pontos_ganhos'].sum()) if 'pontos_ganhos' in rq.columns and len(rq)>0 else 0
    c1,c2,c3,c4,c5=st.columns(5)
    with c1: st.markdown(mcard(f"{nu:,}","Testadores"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{nq:,}","Questionários",c=CL['accent1']),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{nr:,}","Respostas",c=CL['accent2']),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{pts:,}","Pontos",c=CL['orange']),unsafe_allow_html=True)
    with c5: st.markdown(mcard(f"{len(pr):,}","Produtos",c=CL['purple']),unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(mcard(f"{len(data['categoria'])}","Categorias",c=CL['teal']),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{len(data['subcategoria'])}","Subcategorias",c=CL['success']),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{len(em)}","Empresas",c=CL['dark']),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{len(ca)}","Campanhas",c=CL['pink']),unsafe_allow_html=True)
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("#### 📁 Distribuição por Categoria")
        if len(rq)>0 and 'nome_categoria' in rq.columns and rq['nome_categoria'].notna().any():
            cc=rq['nome_categoria'].value_counts()
            fig=px.pie(values=cc.values.tolist(),names=cc.index.tolist(),color_discrete_sequence=PAL,hole=.4)
            fig.update_layout(height=400); st.plotly_chart(fig,use_container_width=True)
    with c2:
        st.markdown("#### 📈 Evolução Temporal")
        if len(rq)>0 and 'createdAt' in rq.columns:
            dt=rq.groupby(rq['createdAt'].dt.date).size().reset_index(); dt.columns=['data','qtd']
            fig=px.area(dt,x='data',y='qtd',color_discrete_sequence=[CL['primary']])
            fig.update_layout(height=400); st.plotly_chart(fig,use_container_width=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown("#### 🏆 Top 10 Subcategorias")
        if len(rq)>0 and 'nome_subcategoria' in rq.columns:
            ts=rq['nome_subcategoria'].value_counts().head(10)
            fig=px.bar(x=ts.values.tolist(),y=ts.index.tolist(),orientation='h',color=ts.values.tolist(),color_continuous_scale='Blues')
            fig.update_layout(height=400,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True)
    with c2:
        st.markdown("#### 👥 Top 10 Testadores")
        if len(rq)>0 and 'nome_usuario' in rq.columns:
            tu=rq.groupby('nome_usuario').size().sort_values(ascending=False).head(10)
            fig=px.bar(x=tu.values.tolist(),y=tu.index.tolist(),orientation='h',color=tu.values.tolist(),color_continuous_scale='Greens')
            fig.update_layout(height=400,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True)
    # Insights
    st.markdown("#### 🧠 Insights Automatizados")
    ih=""
    if len(rq)>0 and 'createdAt' in rq.columns:
        wk=rq.groupby(rq['createdAt'].dt.to_period('W')).size()
        if len(wk)>=2:
            l,p=wk.iloc[-1],wk.iloc[-2]; ch=spct(l-p,p) if p>0 else 0
            ih+=ibox("Estratégico","Tendência",f"Última semana: {l} questionários ({'↑' if ch>0 else '↓'} {abs(ch)}%). {'Manter campanhas.' if ch>0 else 'Ação de reengajamento recomendada.'}")
    if nu>0 and len(rq)>0 and 'id_usuario' in rq.columns:
        tx=spct(rq['id_usuario'].nunique(),nu)
        ih+=ibox("Tático","Ativação",f"{tx}% dos {nu:,} testadores responderam. Bonificação para primeiros acessos pode elevar a base ativa.")
    if ih: st.markdown(ih,unsafe_allow_html=True)

# ============================================================================
# PG2: RESPOSTAS
# ============================================================================
def pg_respostas(data):
    st.markdown('<h2 class="sh">📝 Análise de Respostas</h2>',unsafe_allow_html=True)
    rp,rq=data['resp_pergunta'],data['resp_questionario']
    if len(rp)==0: st.warning("Sem dados."); return
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(mcard(f"{len(rp):,}","Total Respostas"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{len(rq):,}","Questionários",c=CL['accent1']),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{rp['id_usuario'].nunique():,}" if 'id_usuario' in rp.columns else "0","Usuários",c=CL['accent2']),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{rp['id_produto'].nunique():,}" if 'id_produto' in rp.columns else "0","Produtos",c=CL['purple']),unsafe_allow_html=True)
    st.markdown("---")
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
                            fig=px.bar(x=rc.values.tolist(),y=rc.index.tolist(),orientation='h',color=rc.values.tolist(),color_continuous_scale='Blues')
                            fig.update_layout(height=400,coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                            st.plotly_chart(fig,use_container_width=True)
    with t2:
        if 'nome_produto' in rp.columns:
            pp=rp.groupby('nome_produto').size().sort_values(ascending=False).head(20)
            fig=px.bar(x=pp.values.tolist(),y=pp.index.tolist(),orientation='h',color=pp.values.tolist(),color_continuous_scale='Greens')
            fig.update_layout(height=500,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True)
    with t3:
        if 'id_usuario' in rp.columns:
            us=rp.groupby('id_usuario').agg({'id':'count','id_produto':'nunique'}).rename(columns={'id':'resp','id_produto':'prod'})
            if 'nome_usuario' in rp.columns: us=us.join(rp.groupby('id_usuario')['nome_usuario'].first())
            us=us.sort_values('resp',ascending=False)
            fig=px.bar(x=us.head(15)['resp'].values.tolist(),y=us.head(15)['nome_usuario'].values.tolist() if 'nome_usuario' in us.columns else us.head(15).index.astype(str).tolist(),orientation='h',color=us.head(15)['resp'].values.tolist(),color_continuous_scale='Blues')
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
    st.markdown('<h2 class="sh">🔍 Qualidade de Dados</h2>',unsafe_allow_html=True)
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
    st.markdown("---")
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
    st.markdown("#### ⚠️ Top 10 Suspeitos")
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
    st.markdown('<h2 class="sh">👤 Consulta de Usuário</h2>',unsafe_allow_html=True)
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
            st.markdown("#### 🎯 Confiabilidade")
            c1,c2=st.columns([1,2])
            with c1: st.plotly_chart(gauge(us_.iloc[0]['score'],"Score"),use_container_width=True); st.markdown(f"<h3 style='text-align:center'>{us_.iloc[0]['classif']}</h3>",unsafe_allow_html=True)
            with c2:
                cp=pd.DataFrame({'Comp':['Rapidez','Repetitividade','Extremismo','Volume'],'Score':[us_.iloc[0]['sr'],us_.iloc[0]['srp'],us_.iloc[0]['se'],us_.iloc[0]['sv']]})
                fig=px.bar(cp,x='Comp',y='Score',color='Score',color_continuous_scale='RdYlGn_r'); fig.update_layout(height=300,coloraxis_showscale=False)
                st.plotly_chart(fig,use_container_width=True)
    if len(ru)>0:
        st.markdown("#### 📋 Últimas 20 Respostas")
        cols=[c for c in ['createdAt','nome_produto','titulo_pergunta','resposta'] if c in ru.columns]
        st.dataframe(ru[cols].sort_values('createdAt',ascending=False).head(20),hide_index=True,use_container_width=True)

# ============================================================================
# PG5: MAPEAMENTO
# ============================================================================
def pg_mapeamento(data):
    st.markdown('<h2 class="sh">📂 Mapeamento de Pesquisas</h2>',unsafe_allow_html=True)
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
            fig=px.bar(x=pp.values.tolist(),y=pp.index.tolist(),orientation='h',color=pp.values.tolist(),color_continuous_scale='Greens')
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
    st.markdown('<h2 class="sh">👥 Análise Demográfica</h2>',unsafe_allow_html=True)
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
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1:
        if 'genero' in us.columns:
            st.markdown("#### 👤 Gênero")
            gc=us['genero'].value_counts()
            fig=px.pie(values=gc.values.tolist(),names=gc.index.tolist(),color_discrete_sequence=[CL['primary'],CL['secondary'],CL['accent1']],hole=.4)
            fig.update_layout(height=400); st.plotly_chart(fig,use_container_width=True)
    with c2:
        if 'idade' in us.columns:
            st.markdown("#### 📊 Faixa Etária")
            dv=us[us['idade'].notna()&(us['idade']>0)].copy()
            if len(dv)>0:
                dv['fx']=pd.cut(dv['idade'].astype(float),bins=[0,25,35,45,55,65,100],labels=['18-25','26-35','36-45','46-55','56-65','65+'])
                fc=dv['fx'].value_counts().sort_index()
                fig=px.bar(x=fc.index.astype(str).tolist(),y=fc.values.tolist(),color=fc.values.tolist(),color_continuous_scale='Blues')
                fig.update_layout(height=400,coloraxis_showscale=False); st.plotly_chart(fig,use_container_width=True)
    if 'faixa_renda' in us.columns:
        st.markdown("#### 💰 Faixa de Renda")
        rc=us['faixa_renda'].value_counts()
        fig=px.bar(pd.DataFrame({'r':rc.index.tolist(),'q':rc.values.tolist()}),x='q',y='r',orientation='h',color='q',color_continuous_scale='Greens')
        fig.update_layout(height=400,coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig,use_container_width=True)
    if 'nome_estado' in us.columns:
        st.markdown("#### 🗺️ Geografia")
        ec=us['nome_estado'].value_counts().head(15)
        fig=px.bar(x=ec.values.tolist(),y=ec.index.tolist(),orientation='h',color=ec.values.tolist(),color_continuous_scale='Purples')
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
    st.markdown('<h2 class="sh">📢 Campanhas</h2>',unsafe_allow_html=True)
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
    st.markdown("---")
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
    st.markdown('<h2 class="sh">📂 Categorias & Subcategorias</h2>',unsafe_allow_html=True)
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
    st.markdown("---")
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
    st.markdown('<h2 class="sh">📦 Produtos</h2>',unsafe_allow_html=True)
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
    st.markdown("---")
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
            st.markdown("#### Por Categoria")
            if 'nome_categoria' in pr.columns:
                pc=pr['nome_categoria'].value_counts().head(15)
                fig=px.bar(x=pc.values.tolist(),y=pc.index.tolist(),orientation='h',color=pc.values.tolist(),color_continuous_scale='Blues')
                fig.update_layout(height=450,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        with c2:
            st.markdown("#### Por Marca")
            if 'nome_marca' in pr.columns:
                pm=pr['nome_marca'].value_counts().head(15)
                fig=px.bar(x=pm.values.tolist(),y=pm.index.tolist(),orientation='h',color=pm.values.tolist(),color_continuous_scale='Greens')
                fig.update_layout(height=450,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        if 'nome_empresa' in pr.columns:
            st.markdown("#### Por Empresa")
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
                    st.markdown(f"#### 📝 {len(rpr)} respostas para este produto")
                    if len(rpr)>0 and 'titulo_pergunta' in rpr.columns and 'resposta' in rpr.columns:
                        # Perfil sensorial
                        pergs=rpr.groupby('titulo_pergunta').apply(lambda x: pd.to_numeric(x['resposta'].str.replace('"',''),errors='coerce').mean()).dropna()
                        if len(pergs)>=3:
                            st.markdown("##### 🎯 Perfil Sensorial")
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
    st.markdown('<h2 class="sh">🏷️ Marcas</h2>',unsafe_allow_html=True)
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
    st.markdown("---")
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
            fig=px.bar(x=mc_.values.tolist(),y=mc_.index.tolist(),orientation='h',color=mc_.values.tolist(),color_continuous_scale='Blues',title="Top 20 Marcas por Nº de Produtos")
            fig.update_layout(height=500,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True)
            # Por empresa
            if 'nome_empresa' in pr.columns:
                st.markdown("#### Marcas por Empresa")
                me=pr.groupby(['nome_empresa','nome_marca']).size().reset_index(name='qtd').sort_values('qtd',ascending=False).head(30)
                fig=px.bar(me,x='qtd',y='nome_marca',color='nome_empresa',orientation='h',color_discrete_sequence=PAL)
                fig.update_layout(height=500,yaxis_title=""); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)

# ============================================================================
# PG11: PARCEIROS
# ============================================================================
def pg_parceiros(data):
    st.markdown('<h2 class="sh">🤝 Parceiros</h2>',unsafe_allow_html=True)
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
    st.markdown("---")
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
                fig=px.bar(x=pc.values.tolist(),y=pc.index.tolist(),orientation='h',color=pc.values.tolist(),color_continuous_scale='Greens',title="Produtos por Parceiro")
                fig.update_layout(height=400,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        else: st.info("Sem vínculos produto-parceiro cadastrados.")
    ih=ibox("Operacional","Rede de Parceiros",f"{np_} parceiros ativos com {nl} vínculos de produtos. {'Rede bem estruturada.' if nl>np_*2 else 'Ampliar vínculos com parceiros existentes.'}")
    st.markdown(ih,unsafe_allow_html=True)

# ============================================================================
# PG12: GESTÃO DE PESQUISAS
# ============================================================================
def pg_pesquisas(data):
    st.markdown('<h2 class="sh">🔬 Gestão de Pesquisas</h2>',unsafe_allow_html=True)
    pp=data['pesq_produto']; ps=data['pesq_subcategoria']; se=data['sessao']; pg_=data['pergunta']
    rq=data['resp_questionario']
    npp=len(pp); nps=len(ps); nse=len(se); npg=len(pg_)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(mcard(f"{npp}","Pesq. Produto"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{nps}","Pesq. Subcategoria",c=CL['accent1']),unsafe_allow_html=True)
    with c3: st.markdown(mcard(f"{nse}","Sessões",c=CL['teal']),unsafe_allow_html=True)
    with c4: st.markdown(mcard(f"{npg}","Perguntas",c=CL['purple']),unsafe_allow_html=True)
    st.markdown("---")
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
                st.markdown("#### Sessões por Pesquisa")
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
    st.markdown('<h2 class="sh">🎁 Benefícios & Resgates</h2>',unsafe_allow_html=True)
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
    st.markdown("---")
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
                    st.markdown("#### Top Benefícios Resgatados")
                    bc=rg['nome_beneficio'].value_counts().head(10)
                    fig=px.bar(x=bc.values.tolist(),y=bc.index.tolist(),orientation='h',color=bc.values.tolist(),color_continuous_scale='Blues')
                    fig.update_layout(height=400,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                    st.plotly_chart(fig,use_container_width=True)
            with c2:
                if 'nome_usuario' in rg.columns:
                    st.markdown("#### Top Usuários que Resgataram")
                    uc=rg['nome_usuario'].value_counts().head(10)
                    fig=px.bar(x=uc.values.tolist(),y=uc.index.tolist(),orientation='h',color=uc.values.tolist(),color_continuous_scale='Greens')
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
            st.markdown("#### 📈 Evolução de Resgates")
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
            st.markdown("#### 💰 Distribuição de Pontos")
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
    st.markdown('<h2 class="sh">🏢 Empresas</h2>',unsafe_allow_html=True)
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
    st.markdown("---")
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
                st.markdown("#### Produtos por Empresa")
                ec=pr['nome_empresa'].value_counts().head(15)
                fig=px.bar(x=ec.values.tolist(),y=ec.index.tolist(),orientation='h',color=ec.values.tolist(),color_continuous_scale='Blues')
                fig.update_layout(height=450,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        with c2:
            if len(pr)>0 and 'nome_empresa' in pr.columns and 'nome_categoria' in pr.columns:
                st.markdown("#### Categorias por Empresa")
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
    st.markdown('<h2 class="sh">🏠 Banners & Recomendados</h2>',unsafe_allow_html=True)
    bh=data['banner_home']; pr=data['prod_recomendado']
    nb=len(bh); nrec=len(pr)
    c1,c2=st.columns(2)
    with c1: st.markdown(mcard(f"{nb}","Banners Home"),unsafe_allow_html=True)
    with c2: st.markdown(mcard(f"{nrec}","Prod. Recomendados",c=CL['accent1']),unsafe_allow_html=True)
    st.markdown("---")
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
    st.markdown('<h2 class="sh">👥 Gestão de Testadores</h2>',unsafe_allow_html=True)
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
    st.markdown("---")
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
                st.markdown("#### Por Estado")
                ec=us['nome_estado'].value_counts().head(15)
                fig=px.bar(x=ec.values.tolist(),y=ec.index.tolist(),orientation='h',color=ec.values.tolist(),color_continuous_scale='Blues')
                fig.update_layout(height=450,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        with c2:
            if 'nome_cidade' in us.columns:
                st.markdown("#### Top 15 Cidades")
                cc_=us['nome_cidade'].value_counts().head(15)
                fig=px.bar(x=cc_.values.tolist(),y=cc_.index.tolist(),orientation='h',color=cc_.values.tolist(),color_continuous_scale='Greens')
                fig.update_layout(height=450,yaxis_title="",coloraxis_showscale=False); fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig,use_container_width=True)
        # Mapa de calor estado x gênero
        if 'nome_estado' in us.columns and 'genero' in us.columns:
            st.markdown("#### Heatmap Estado × Gênero")
            hm=us.groupby(['nome_estado','genero']).size().reset_index(name='qtd')
            hm_p=hm.pivot_table(index='nome_estado',columns='genero',values='qtd',fill_value=0)
            top_est=us['nome_estado'].value_counts().head(15).index
            hm_p=hm_p[hm_p.index.isin(top_est)]
            if len(hm_p)>0:
                fig=px.imshow(hm_p,color_continuous_scale='Blues',aspect='auto')
                fig.update_layout(height=400); st.plotly_chart(fig,use_container_width=True)
    with t3:
        if 'createdAt' in us.columns:
            st.markdown("#### Cadastros ao Longo do Tempo")
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
            st.markdown("#### Cohorts de Engajamento")
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
    st.markdown('<h2 class="sh">🧠 Central de Insights</h2>',unsafe_allow_html=True)
    us=data['usuario']; pr=data['produto']; rq=data['resp_questionario']; rp=data['resp_pergunta']
    rg=data['resgate']; ca=data['campanha']; em=data['empresa']; bn=data['beneficio']
    st.markdown("#### Visão consolidada de todos os insights estratégicos, táticos e operacionais da plataforma")
    st.markdown("---")
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
        st.markdown("#### 📊 Indicadores-Chave")
        kpis=[]
        if nu>0 and nq>0 and 'id_usuario' in rq.columns: kpis.append(f"• Taxa de ativação: **{spct(rq['id_usuario'].nunique(),nu)}%**")
        if nu>0: kpis.append(f"• Cadastros completos: **{spct(cc,nu)}%**")
        if np_>0 and nq>0 and 'id_produto' in rq.columns: kpis.append(f"• Cobertura de produtos: **{spct(rq['id_produto'].nunique(),np_)}%**")
        if len(rg)>0 and 'id_usuario' in rg.columns: kpis.append(f"• Taxa de resgate: **{spct(rg['id_usuario'].nunique(),nu)}%**")
        kpis.append(f"• Empresas: **{ne}** | Campanhas: **{len(ca)}**")
        st.markdown("\n".join(kpis))
    st.markdown("---")
    # Todos os insights
    st.markdown("### 🔮 Insights Estratégicos")
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
    st.markdown("### 🎯 Insights Táticos")
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
    st.markdown("### ⚙️ Insights Operacionais")
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
    st.markdown("---")
    st.markdown("### 📋 Resumo Executivo")
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
        st.markdown("""<div style="text-align:center;padding:1rem 0">
            <div style="background:linear-gradient(135deg,#307FE2,#4ECDC4);border-radius:14px;padding:12px;margin-bottom:8px">
            <span style="color:white;font-size:1.3rem;font-weight:700;font-family:'Space Grotesk'">🍽️ FOODTEST</span></div>
            <span style="color:#64748b;font-size:.75rem">Analytics Platform v2.0</span></div>""",unsafe_allow_html=True)
        st.markdown("---")
        data_dir=st.text_input("📁 Diretório dos .txt:",value=".",help="Pasta com os .txt do DBeaver")
        if st.button("🔄 Recarregar",use_container_width=True): st.session_state['loaded']=False; st.cache_data.clear()
        st.markdown("---")
        st.markdown("### 🧭 Navegação")
        page=st.radio("",options=[
            "📊 Dashboard Geral","📢 Campanhas","📂 Categorias","📦 Produtos","🏷️ Marcas",
            "🤝 Parceiros","🏠 Banners","🔬 Pesquisas","📝 Respostas","🔍 Qualidade",
            "👤 Consulta Usuário","📂 Mapeamento","👥 Demográfica","🎁 Benefícios",
            "🏢 Empresas","👥 Testadores","🧠 Insights"
        ],label_visibility="collapsed",key="nav")
        st.markdown("---")
        st.markdown('<div style="text-align:center;font-size:.75rem;color:#94a3b8">📧 suporte@foodtest.com.br<br>v2.0</div>',unsafe_allow_html=True)
    # Header
    st.markdown("""<div style="background:linear-gradient(90deg,#307FE2,#4ECDC4);padding:1.5rem 2rem;border-radius:16px;margin-bottom:1.5rem">
        <h1 style="color:white;margin:0;font-family:'Space Grotesk'">🍽️ Foodtest Analytics</h1>
        <p style="color:rgba(255,255,255,.9);margin:.3rem 0 0">Plataforma Completa de Análise Sensorial e Inteligência de Dados</p></div>""",unsafe_allow_html=True)
    # Load
    if 'data' not in st.session_state or not st.session_state.get('loaded',False):
        with st.spinner("Carregando dados..."):
            try:
                raw=load_all(data_dir); data=enrich(raw)
                st.session_state['data']=data; st.session_state['loaded']=True
                total=sum(len(df) for df in data.values() if isinstance(df,pd.DataFrame))
                if total==0: st.warning(f"⚠️ Nenhum dado em **{data_dir}**."); return
            except Exception as e: st.error(f"Erro: {e}"); return
    data=st.session_state.get('data',{})
    # Route
    R={
        "📊 Dashboard Geral":pg_overview,"📝 Respostas":pg_respostas,"🔍 Qualidade":pg_qualidade,
        "👤 Consulta Usuário":pg_usuario,"📂 Mapeamento":pg_mapeamento,"👥 Demográfica":pg_demografica,
        "📢 Campanhas":pg_campanhas,"📂 Categorias":pg_categorias,"📦 Produtos":pg_produtos,
        "🏷️ Marcas":pg_marcas,"🤝 Parceiros":pg_parceiros,
        "🔬 Pesquisas":pg_pesquisas,"🎁 Benefícios":pg_beneficios,"🏢 Empresas":pg_empresas,
        "🏠 Banners":pg_banners,"👥 Testadores":pg_testadores,"🧠 Insights":pg_insights,
    }
    fn=R.get(page)
    if fn: fn(data)
    else: pg_placeholder(page)

if __name__=="__main__":
    main()