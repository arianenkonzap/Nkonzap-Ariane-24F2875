
import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LinearRegression
from datetime import datetime
import random
import streamlit.components.v1 as components

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PredictTrack | Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS – DARK PREMIUM THEME
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0D0F14;
    color: #E2E8F0;
}

/* Main background */
.stApp {
    background: linear-gradient(135deg, #0D0F14 0%, #141824 100%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141824 0%, #1A1F2E 100%);
    border-right: 1px solid #2D3748;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1A1F2E 0%, #212840 100%);
    border: 1px solid #2D3748;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

[data-testid="metric-container"]:hover {
    border-color: #6366F1;
    box-shadow: 0 4px 30px rgba(99,102,241,0.2);
    transition: all 0.3s ease;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366F1, #8B5CF6);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 10px 24px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(99,102,241,0.5);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #1A1F2E;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #94A3B8;
    border-radius: 8px;
    font-weight: 600;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    color: white !important;
}

/* Inputs */
.stNumberInput input, .stSlider {
    background: #1A1F2E !important;
    border-color: #2D3748 !important;
    color: #E2E8F0 !important;
    border-radius: 8px !important;
}

/* Section header */
.section-header {
    font-size: 1.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6366F1, #A78BFA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 16px;
}

/* Info box */
.info-box {
    background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1));
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
}

/* Equation display */
.equation-box {
    background: linear-gradient(135deg, #1A1F2E, #212840);
    border: 1px solid #6366F1;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    font-size: 1.3rem;
    color: #A78BFA;
    font-weight: 600;
    margin: 16px 0;
}

/* Logo title */
.logo-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6366F1, #A78BFA, #EC4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 4px;
}
.logo-sub {
    font-size: 0.85rem;
    color: #64748B;
    text-align: center;
    margin-bottom: 24px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* Live badge */
.live-badge {
    display: inline-block;
    background: #EF4444;
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 20px;
    letter-spacing: 1px;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

hr.divider {
    border: none;
    border-top: 1px solid #2D3748;
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
DB_PATH = "predicttrack.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_time REAL NOT NULL,
            conversion_score REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    con.commit()
    # Seed with realistic data if empty
    cur.execute("SELECT COUNT(*) FROM analytics")
    count = cur.fetchone()[0]
    if count == 0:
        seed_data = []
        np.random.seed(42)
        for _ in range(80):
            t = round(np.random.uniform(10, 300), 2)
            score = round(0.3 * t + np.random.normal(0, 20), 2)
            score = max(0, min(100, score))
            ts = datetime(2026, 4, random.randint(1, 24),
                          random.randint(0, 23), random.randint(0, 59)).isoformat()
            seed_data.append((t, score, ts))
        cur.executemany(
            "INSERT INTO analytics (session_time, conversion_score, timestamp) VALUES (?,?,?)",
            seed_data
        )
        con.commit()
    con.close()

def load_data() -> pd.DataFrame:
    con = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM analytics ORDER BY timestamp DESC", con
    )
    con.close()
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour
    return df

def insert_row(session_time: float, conversion_score: float):
    con = get_connection()
    con.execute(
        "INSERT INTO analytics (session_time, conversion_score, timestamp) VALUES (?,?,?)",
        (session_time, conversion_score, datetime.now().isoformat())
    )
    con.commit()
    con.close()

def clear_data():
    con = get_connection()
    con.execute("DELETE FROM analytics")
    con.commit()
    con.close()

# ─────────────────────────────────────────────
# ML
# ─────────────────────────────────────────────
def train_model(df: pd.DataFrame):
    if len(df) < 3:
        return None, None, None
    X = df[["session_time"]].values
    y = df["conversion_score"].values
    model = LinearRegression()
    model.fit(X, y)
    r2 = model.score(X, y)
    return model, model.coef_[0], r2

# ─────────────────────────────────────────────
# PLOTLY HELPERS  (dark theme)
# ─────────────────────────────────────────────
DARK_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(20,24,36,0.8)",
    font=dict(color="#E2E8F0", family="Inter"),
    xaxis=dict(gridcolor="#2D3748", zerolinecolor="#2D3748"),
    yaxis=dict(gridcolor="#2D3748", zerolinecolor="#2D3748"),
    margin=dict(l=20, r=20, t=40, b=20),
)

def fig_scatter(df, model, coef, intercept):
    fig = go.Figure()
    # Points
    fig.add_trace(go.Scatter(
        x=df["session_time"], y=df["conversion_score"],
        mode="markers",
        name="Données",
        marker=dict(
            color=df["conversion_score"],
            colorscale="Viridis",
            size=8, opacity=0.8,
            line=dict(width=1, color="#6366F1")
        )
    ))
    # Regression line
    if model is not None:
        x_range = np.linspace(df["session_time"].min(), df["session_time"].max(), 200)
        y_pred = model.predict(x_range.reshape(-1, 1))
        fig.add_trace(go.Scatter(
            x=x_range, y=y_pred,
            mode="lines", name="Régression",
            line=dict(color="#EC4899", width=3, dash="solid")
        ))
    fig.update_layout(
        **DARK_LAYOUT,
        title="Nuage de Points + Droite de Régression",
        xaxis_title="Temps de Session (s)",
        yaxis_title="Score d'Engagement",
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    return fig

def fig_histogram(df):
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df["session_time"],
        nbinsx=20,
        name="Sessions",
        marker=dict(
            color="#6366F1",
            opacity=0.85,
            line=dict(color="#A78BFA", width=1)
        )
    ))
    fig.update_layout(
        **DARK_LAYOUT,
        title="Distribution des Temps de Session",
        xaxis_title="Temps de Session (s)",
        yaxis_title="Fréquence",
        bargap=0.05
    )
    return fig

def fig_pie(df):
    threshold = df["conversion_score"].median()
    high = (df["conversion_score"] >= threshold).sum()
    low = (df["conversion_score"] < threshold).sum()
    fig = go.Figure(go.Pie(
        labels=["Haute Engagement", "Bas Engagement"],
        values=[high, low],
        hole=0.45,
        marker=dict(colors=["#6366F1", "#EC4899"]),
        textfont=dict(color="white", size=13),
    ))
    fig.update_layout(
        **DARK_LAYOUT,
        title="Engagement : Haute vs Bas",
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    return fig

def fig_bar_hour(df):
    if "hour" not in df.columns:
        return go.Figure()
    counts = df.groupby("hour").size().reset_index(name="count")
    fig = go.Figure(go.Bar(
        x=counts["hour"], y=counts["count"],
        name="Sessions",
        marker=dict(
            color=counts["count"],
            colorscale="Plasma",
            line=dict(color="#A78BFA", width=0.5)
        )
    ))
    fig.update_layout(
        **DARK_LAYOUT,
        title="Sessions par Heure de la Journée",
        xaxis_title="Heure",
        yaxis_title="Nombre de Sessions",
        bargap=0.15
    )
    return fig

# ─────────────────────────────────────────────
# JAVASCRIPT PING COMPONENT
# ─────────────────────────────────────────────
JS_PING = """
<div style="
    background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.05));
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 12px;
    padding: 14px 18px;
    font-family: 'Inter', sans-serif;
">
  <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
    <div id="dot" style="
        width:10px; height:10px; border-radius:50%;
        background:#EF4444;
        box-shadow: 0 0 8px #EF4444;
        animation: blink 1.5s infinite;
    "></div>
    <span style="color:#A78BFA; font-weight:700; font-size:0.9rem; letter-spacing:1px;">LIVE SESSION TRACKER</span>
  </div>
  <div style="color:#94A3B8; font-size:0.8rem;">Ping envoyé toutes les <b style="color:#E2E8F0">5 secondes</b></div>
  <div style="margin-top:8px; color:#E2E8F0; font-size:0.85rem;">
    ⏱ Temps actuel : <span id="timer" style="color:#6366F1; font-weight:700;">0s</span>
    &nbsp;|&nbsp; 📡 Pings : <span id="pings" style="color:#EC4899; font-weight:700;">0</span>
  </div>
</div>

<style>
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.2; }
}
</style>

<script>
(function() {
    var elapsed = 0;
    var pings = 0;
    function updateUI() {
        document.getElementById('timer').textContent = elapsed + 's';
        document.getElementById('pings').textContent = pings;
    }
    setInterval(function() {
        elapsed += 1;
        updateUI();
    }, 1000);
    setInterval(function() {
        pings += 1;
        console.log('[PredictTrack] Session ping #' + pings + ' – elapsed: ' + elapsed + 's');
        updateUI();
    }, 5000);
})();
</script>
"""

# ─────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────
init_db()
df = load_data()
model, coef, r2 = train_model(df)
intercept = model.intercept_ if model else None

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo-title">📊 PredictTrack</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">Analytics Engine v1.0</div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown("### ➕ Injection Manuelle")
    with st.form("inject_form"):
        col1, col2 = st.columns(2)
        with col1:
            session_time_input = st.number_input(
                "⏱ Session (s)", min_value=1.0, max_value=600.0,
                value=120.0, step=5.0
            )
        with col2:
            conversion_input = st.number_input(
                "🎯 Score", min_value=0.0, max_value=100.0,
                value=50.0, step=1.0
            )
        submitted = st.form_submit_button("💾 Injecter", use_container_width=True)
        if submitted:
            insert_row(session_time_input, conversion_input)
            st.success("✅ Donnée ajoutée !")
            st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("### 🤖 Génération Aléatoire")
    n_random = st.slider("Nombre de points", 5, 100, 20)
    if st.button("⚡ Générer", use_container_width=True):
        for _ in range(n_random):
            t = round(np.random.uniform(10, 300), 2)
            score = round(0.3 * t + np.random.normal(0, 20), 2)
            score = max(0.0, min(100.0, score))
            insert_row(t, score)
        st.success(f"✅ {n_random} points ajoutés !")
        st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if st.button("🗑️ Effacer toutes les données", use_container_width=True):
        clear_data()
        st.warning("Base de données réinitialisée.")
        st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("### 📡 Simulateur Live")
    components.html(JS_PING, height=110)

# ─────────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────────
st.markdown('<div class="logo-title">📊 PredictTrack Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="logo-sub">Régression Linéaire · Engagement Analytique · ML Temps Réel</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Metrics row ──
avg_session = df["session_time"].mean() if not df.empty else 0
avg_score   = df["conversion_score"].mean() if not df.empty else 0
predicted_score_avg = model.predict([[avg_session]])[0] if model else 0
total_records = len(df)

c1, c2, c3, c4 = st.columns(4)
c1.metric("⏱ Temps Moyen (s)", f"{avg_session:.1f} s",
          delta=f"±{df['session_time'].std():.1f}" if not df.empty else None)
c2.metric("🎯 Score Moyen", f"{avg_score:.1f}",
          delta=f"±{df['conversion_score'].std():.1f}" if not df.empty else None)
c3.metric("🤖 Score Prédit (moy.)", f"{predicted_score_avg:.1f}")
c4.metric("📦 Total Entrées", f"{total_records}")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Equation + R² ──
if model is not None:
    st.markdown(
        f'<div class="equation-box">'
        f'y = <b>{coef:.4f}</b> · x + <b>{intercept:.4f}</b>'
        f'&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;R² = <b>{r2:.4f}</b>'
        f'</div>',
        unsafe_allow_html=True
    )
else:
    st.info("⚠️ Ajoutez au moins 3 données pour entraîner le modèle.")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔵 Régression",
    "📊 Distribution",
    "🥧 Engagement",
    "🕐 Par Heure",
    "🔮 Prédiction"
])

with tab1:
    st.markdown('<div class="section-header">Nuage de Points & Droite de Régression</div>', unsafe_allow_html=True)
    if df.empty:
        st.warning("Aucune donnée disponible.")
    else:
        st.plotly_chart(fig_scatter(df, model, coef, intercept),
                        use_container_width=True)
        with st.expander("📋 Voir les données brutes"):
            st.dataframe(
                df[["id", "session_time", "conversion_score", "timestamp"]]
                  .sort_values("timestamp", ascending=False),
                use_container_width=True
            )

with tab2:
    st.markdown('<div class="section-header">Distribution des Temps de Session</div>', unsafe_allow_html=True)
    if df.empty:
        st.warning("Aucune donnée disponible.")
    else:
        st.plotly_chart(fig_histogram(df), use_container_width=True)
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("📉 Min", f"{df['session_time'].min():.1f} s")
        col_b.metric("📈 Max", f"{df['session_time'].max():.1f} s")
        col_c.metric("📊 Médiane", f"{df['session_time'].median():.1f} s")

with tab3:
    st.markdown('<div class="section-header">Répartition Haute / Bas Engagement</div>', unsafe_allow_html=True)
    if df.empty:
        st.warning("Aucune donnée disponible.")
    else:
        threshold = df["conversion_score"].median()
        high_count = (df["conversion_score"] >= threshold).sum()
        low_count  = (df["conversion_score"] <  threshold).sum()
        col_pie, col_info = st.columns([2, 1])
        with col_pie:
            st.plotly_chart(fig_pie(df), use_container_width=True)
        with col_info:
            st.markdown(f"""
            <div class="info-box">
                <div style="font-size:1rem; font-weight:700; color:#A78BFA; margin-bottom:12px;">📊 Statistiques</div>
                <div style="margin-bottom:8px;">🟣 <b>Haute Engagement</b><br>
                    <span style="font-size:1.5rem; color:#6366F1; font-weight:800;">{high_count}</span>
                    <span style="color:#64748B;"> sessions ({high_count/total_records*100:.1f}%)</span>
                </div>
                <div style="margin-bottom:8px;">🔴 <b>Bas Engagement</b><br>
                    <span style="font-size:1.5rem; color:#EC4899; font-weight:800;">{low_count}</span>
                    <span style="color:#64748B;"> sessions ({low_count/total_records*100:.1f}%)</span>
                </div>
                <hr style="border-color:#2D3748;">
                <div style="color:#64748B; font-size:0.8rem;">Seuil médian : <b style="color:#E2E8F0">{threshold:.1f}</b></div>
            </div>
            """, unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section-header">Sessions par Heure de la Journée</div>', unsafe_allow_html=True)
    if df.empty:
        st.warning("Aucune donnée disponible.")
    else:
        st.plotly_chart(fig_bar_hour(df), use_container_width=True)
        if "hour" in df.columns:
            peak_hour = df.groupby("hour").size().idxmax()
            st.markdown(
                f'<div class="info-box">🏆 Heure de pic : <b style="color:#6366F1">{peak_hour}h00</b> — '
                f'{df[df["hour"]==peak_hour].shape[0]} sessions</div>',
                unsafe_allow_html=True
            )

with tab5:
    st.markdown('<div class="section-header">🔮 Prédiction d\'Engagement</div>', unsafe_allow_html=True)
    if model is None:
        st.warning("Le modèle n'est pas encore entraîné. Ajoutez au moins 3 données.")
    else:
        col_pred, col_result = st.columns([1, 1])
        with col_pred:
            st.markdown("""
            <div class="info-box">
                Entrez un temps de session hypothétique pour obtenir
                le <b>score d'engagement prédit</b> par le modèle ML.
            </div>
            """, unsafe_allow_html=True)
            pred_session = st.number_input(
                "⏱ Temps de session hypothétique (secondes)",
                min_value=1.0, max_value=1000.0, value=150.0, step=10.0,
                key="pred_input"
            )
            predict_btn = st.button("🚀 Prédire", use_container_width=True)

        with col_result:
            if predict_btn:
                predicted = model.predict([[pred_session]])[0]
                predicted = max(0.0, min(100.0, predicted))
                level = "🟢 HAUTE" if predicted >= df["conversion_score"].median() else "🔴 BASSE"
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1));
                    border: 2px solid #6366F1;
                    border-radius: 16px;
                    padding: 28px;
                    text-align: center;
                ">
                    <div style="color:#94A3B8; font-size:0.9rem; margin-bottom:8px;">Score d'Engagement Prédit</div>
                    <div style="font-size:3.5rem; font-weight:800;
                                background: linear-gradient(135deg,#6366F1,#A78BFA);
                                -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        {predicted:.1f}
                    </div>
                    <div style="font-size:0.9rem; color:#64748B;">/ 100</div>
                    <div style="margin-top:12px; font-size:1rem; font-weight:600; color:#E2E8F0;">
                        Engagement : {level}
                    </div>
                    <div style="margin-top:8px; font-size:0.8rem; color:#64748B;">
                        y = {coef:.4f} × {pred_session} + {intercept:.4f}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Mini gauge chart
                gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=predicted,
                    domain={"x": [0, 1], "y": [0, 1]},
                    gauge={
                        "axis": {"range": [0, 100], "tickcolor": "#E2E8F0"},
                        "bar": {"color": "#6366F1"},
                        "bgcolor": "#1A1F2E",
                        "bordercolor": "#2D3748",
                        "steps": [
                            {"range": [0, 40],  "color": "rgba(239,68,68,0.2)"},
                            {"range": [40, 70], "color": "rgba(234,179,8,0.2)"},
                            {"range": [70, 100],"color": "rgba(99,102,241,0.2)"},
                        ],
                        "threshold": {
                            "line": {"color": "#EC4899", "width": 3},
                            "thickness": 0.75,
                            "value": predicted
                        }
                    },
                    number={"font": {"color": "#A78BFA", "size": 36}}
                ))
                gauge.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E2E8F0"),
                    height=220,
                    margin=dict(l=20, r=20, t=30, b=10)
                )
                st.plotly_chart(gauge, use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center; color:#2D3748; font-size:0.75rem;">PredictTrack © 2026 · Powered by Streamlit · scikit-learn · Plotly</div>',
    unsafe_allow_html=True
)
