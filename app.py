import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- Page Config ---
st.set_page_config(
    page_title="RideIQ — Ride-Share Analytics",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&family=Syne:wght@700;800&display=swap');
    
    .stApp { background-color: #060b14; }
    h1, h2, h3 { font-family: 'Syne', sans-serif !important; }
    
    .main-title {
        font-family: 'Syne', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00aaff, #ffffff, #00aaff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        letter-spacing: 3px;
        padding: 1rem 0 0.2rem 0;
    }
    .subtitle {
        text-align: center;
        color: #4a7fa5;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.95rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #0d1b2a, #0a1628);
        border: 1px solid #00aaff22;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 0 24px #00aaff0a;
    }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 1.9rem;
        font-weight: 800;
        color: #00aaff;
    }
    .metric-label {
        color: #4a7fa5;
        font-size: 0.75rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-top: 0.3rem;
        font-family: 'Space Grotesk', sans-serif;
    }
    .section-header {
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        color: #00aaff;
        border-left: 3px solid #ffffff33;
        padding-left: 1rem;
        margin: 2rem 0 0.5rem 0;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .insight-box {
        background: linear-gradient(135deg, #0d1b2a, #060b14);
        border: 1px solid #00aaff33;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        color: #aac8e0;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.9rem;
        line-height: 1.7;
    }
    .rec-box {
        background: linear-gradient(135deg, #0a1f35, #060b14);
        border: 1px solid #00aaff55;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin: 0.8rem 0;
        color: #cce4f7;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.92rem;
        line-height: 1.7;
    }
    section[data-testid="stSidebar"] {
        background: #0a1220;
        border-right: 1px solid #00aaff11;
    }
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("rideshare_kaggle.csv")
    df = df.dropna(subset=['price', 'distance', 'cab_type', 'name', 'surge_multiplier'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='s', errors='coerce')
    df = df.dropna(subset=['datetime'])
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.day_name()
    df['month'] = df['datetime'].dt.month_name()
    df['is_surge'] = df['surge_multiplier'] > 1.0
    df['price_per_mile'] = df['price'] / df['distance'].replace(0, np.nan)
    return df

df = load_data()

# --- Sidebar ---
st.sidebar.markdown("### 🎛️ Filters")
cab_filter = st.sidebar.multiselect("Platform", df['cab_type'].unique(), default=list(df['cab_type'].unique()))
filtered_df = df[df['cab_type'].isin(cab_filter)]

# --- Header ---
st.markdown('<div class="main-title">RIDEIQ</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ride-Share Product Analytics · Boston Market · 2018</div>', unsafe_allow_html=True)

# --- KPIs ---
st.markdown('<div class="section-header">Market Overview</div>', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{len(filtered_df):,}</div>
        <div class="metric-label">Total Rides</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">${filtered_df['price'].mean():.2f}</div>
        <div class="metric-label">Avg Fare</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{filtered_df['distance'].mean():.1f} mi</div>
        <div class="metric-label">Avg Distance</div>
    </div>""", unsafe_allow_html=True)
with col4:
    surge_pct = filtered_df['is_surge'].mean() * 100
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{surge_pct:.1f}%</div>
        <div class="metric-label">Surge Rate</div>
    </div>""", unsafe_allow_html=True)
with col5:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{filtered_df['price_per_mile'].mean():.2f}</div>
        <div class="metric-label">$/Mile Avg</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# --- Section 1: Demand Patterns ---
st.markdown('<div class="section-header">01 — Demand Patterns</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Rides by Hour of Day**")
    hourly = filtered_df.groupby('hour').size().reset_index(name='rides')
    fig = px.bar(hourly, x='hour', y='rides',
                 color='rides', color_continuous_scale=['#0a1628', '#00aaff'])
    fig.update_layout(paper_bgcolor='#060b14', plot_bgcolor='#060b14',
                      font=dict(color='#aac8e0', family='Space Grotesk'),
                      xaxis=dict(gridcolor='#0d1b2a', title='Hour'),
                      yaxis=dict(gridcolor='#0d1b2a', title='Rides'),
                      coloraxis_showscale=False, height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**Rides by Day of Week**")
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    daily = filtered_df.groupby('day_of_week').size().reset_index(name='rides')
    daily['day_of_week'] = pd.Categorical(daily['day_of_week'], categories=day_order, ordered=True)
    daily = daily.sort_values('day_of_week')
    fig = px.bar(daily, x='day_of_week', y='rides',
                 color='rides', color_continuous_scale=['#0a1628', '#00aaff'])
    fig.update_layout(paper_bgcolor='#060b14', plot_bgcolor='#060b14',
                      font=dict(color='#aac8e0', family='Space Grotesk'),
                      xaxis=dict(gridcolor='#0d1b2a', title=''),
                      yaxis=dict(gridcolor='#0d1b2a', title='Rides'),
                      coloraxis_showscale=False, height=350)
    st.plotly_chart(fig, use_container_width=True)

peak_hour = hourly.loc[hourly['rides'].idxmax(), 'hour']
peak_day = daily.loc[daily['rides'].idxmax(), 'day_of_week']
st.markdown(f"""<div class="insight-box">
    💡 <b>Insight:</b> Demand peaks at <b style="color:#00aaff">{peak_hour}:00</b> and is highest on <b style="color:#00aaff">{peak_day}</b>.
    A product team should pre-position drivers in high-demand zones 30 minutes before peak hours to reduce wait times and cancellations.
</div>""", unsafe_allow_html=True)

st.markdown("---")

# --- Section 2: Surge Pricing Analysis ---
st.markdown('<div class="section-header">02 — Surge Pricing Analysis</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Avg Fare by Surge Multiplier**")
    surge_fare = filtered_df.groupby('surge_multiplier')['price'].mean().reset_index()
    fig = px.scatter(surge_fare, x='surge_multiplier', y='price',
                     size='price', color='price',
                     color_continuous_scale=['#0a1628', '#00aaff', '#ffffff'])
    fig.update_layout(paper_bgcolor='#060b14', plot_bgcolor='#060b14',
                      font=dict(color='#aac8e0', family='Space Grotesk'),
                      xaxis=dict(gridcolor='#0d1b2a', title='Surge Multiplier'),
                      yaxis=dict(gridcolor='#0d1b2a', title='Avg Price ($)'),
                      coloraxis_showscale=False, height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**Surge Rate by Hour**")
    surge_hour = filtered_df.groupby('hour')['is_surge'].mean().reset_index()
    surge_hour['surge_pct'] = surge_hour['is_surge'] * 100
    fig = px.line(surge_hour, x='hour', y='surge_pct', markers=True,
                  color_discrete_sequence=['#00aaff'])
    fig.update_layout(paper_bgcolor='#060b14', plot_bgcolor='#060b14',
                      font=dict(color='#aac8e0', family='Space Grotesk'),
                      xaxis=dict(gridcolor='#0d1b2a', title='Hour'),
                      yaxis=dict(gridcolor='#0d1b2a', title='Surge Rate (%)'),
                      height=350)
    fig.update_traces(line=dict(width=2.5))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- Section 3: Platform Comparison ---
st.markdown('<div class="section-header">03 — Uber vs Lyft Head-to-Head</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Avg Price by Ride Type**")
    price_type = filtered_df.groupby(['cab_type', 'name'])['price'].mean().reset_index()
    fig = px.bar(price_type, x='name', y='price', color='cab_type',
                 barmode='group',
                 color_discrete_map={'Uber': '#00aaff', 'Lyft': '#ff00aa'})
    fig.update_layout(paper_bgcolor='#060b14', plot_bgcolor='#060b14',
                      font=dict(color='#aac8e0', family='Space Grotesk'),
                      xaxis=dict(gridcolor='#0d1b2a', tickangle=45),
                      yaxis=dict(gridcolor='#0d1b2a', title='Avg Price ($)'),
                      legend=dict(bgcolor='#0d1b2a'), height=380)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**Price Distribution**")
    fig = px.box(filtered_df[filtered_df['price'] < 60], x='cab_type', y='price',
                 color='cab_type',
                 color_discrete_map={'Uber': '#00aaff', 'Lyft': '#ff00aa'})
    fig.update_layout(paper_bgcolor='#060b14', plot_bgcolor='#060b14',
                      font=dict(color='#aac8e0', family='Space Grotesk'),
                      xaxis=dict(gridcolor='#0d1b2a', title=''),
                      yaxis=dict(gridcolor='#0d1b2a', title='Price ($)'),
                      legend=dict(bgcolor='#0d1b2a'), height=380)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- Section 4: Price vs Distance ---
st.markdown('<div class="section-header">04 — Price Efficiency Analysis</div>', unsafe_allow_html=True)
sample = filtered_df[filtered_df['price'] < 60].sample(min(3000, len(filtered_df)), random_state=42)
fig = px.scatter(sample, x='distance', y='price', color='cab_type',
                 opacity=0.5, trendline='ols',
                 color_discrete_map={'Uber': '#00aaff', 'Lyft': '#ff00aa'})
fig.update_layout(paper_bgcolor='#060b14', plot_bgcolor='#060b14',
                  font=dict(color='#aac8e0', family='Space Grotesk'),
                  xaxis=dict(gridcolor='#0d1b2a', title='Distance (miles)'),
                  yaxis=dict(gridcolor='#0d1b2a', title='Price ($)'),
                  legend=dict(bgcolor='#0d1b2a'), height=420)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- Section 5: Product Recommendations ---
st.markdown('<div class="section-header">05 — Product Recommendations</div>', unsafe_allow_html=True)
st.markdown("*Based on the data analysis above, here are 3 product decisions I'd bring to a review:*")

st.markdown(f"""<div class="rec-box">
    🚗 <b style="color:#00aaff">Recommendation 1: Proactive Driver Positioning</b><br>
    Demand consistently peaks at {peak_hour}:00 and on {peak_day}s. The product team should implement 
    a push notification system alerting drivers to go online 30 minutes before predicted demand spikes, 
    reducing surge pricing frequency and improving rider satisfaction scores.
</div>""", unsafe_allow_html=True)

st.markdown(f"""<div class="rec-box">
    💰 <b style="color:#00aaff">Recommendation 2: Surge Transparency Feature</b><br>
    {surge_pct:.1f}% of rides in this market are surge-priced. Riders who see surge pricing without context 
    often cancel and churn. Adding a "surge countdown" feature showing estimated time until normal pricing 
    returns would reduce cancellations and improve retention among price-sensitive users.
</div>""", unsafe_allow_html=True)

st.markdown(f"""<div class="rec-box">
    📊 <b style="color:#00aaff">Recommendation 3: Price-Per-Mile Transparency</b><br>
    Average price per mile is ${filtered_df['price_per_mile'].mean():.2f}, but this varies significantly 
    by ride type and distance. Surfacing price-per-mile estimates before booking would reduce post-ride 
    dissatisfaction and build long-term trust — particularly for new users comparing platforms.
</div>""", unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown('<div style="text-align:center; color:#1a3a5c; font-family:Space Grotesk; font-size:0.8rem; letter-spacing:1px;">RIDEIQ · PRODUCT ANALYTICS · BUILT WITH PYTHON & STREAMLIT</div>', unsafe_allow_html=True)