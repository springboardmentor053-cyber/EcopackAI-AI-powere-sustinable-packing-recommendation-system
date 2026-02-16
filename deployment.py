import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import io

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="EcoPack AI Dashboard", page_icon="🌱", layout="wide")

# --- 2. DARK MODE THEME CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    
    /* Global Text Visibility */
    h1, h2, h3, p, label, .stMarkdown { color: #ffffff !important; }

    /* Metric Card Styling */
    div[data-testid="metric-container"] {
        background-color: #1a1a1a !important;
        border: 1px solid #333333 !important;
        padding: 20px;
        border-radius: 12px;
    }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #bbbbbb !important; }

    /* Table Styling for Dark Mode */
    .stDataFrame {
        border: 1px solid #333333;
        border-radius: 10px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #333333;
    }

    /* Success Alert */
    .stAlert { background-color: #06402b !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE CONNECTION ---
@st.cache_resource
def get_db_engine():
    return create_engine("postgresql://eco_project_vvnx_user:gUMHDpqnGVzYWuPSYO0B00W3bS0akPj4@dpg-d5nsjs6id0rc73f77m20-a.singapore-postgres.render.com:5432/eco_project_vvnx")

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2331/2331821.png", width=80)
    st.header("Input Parameters")
    weight = st.number_input("Product Weight (kg)", 0.1, 50.0, 5.0)
    fragility = st.select_slider("Fragility Level (1-10)", options=range(1, 11), value=5)
    st.markdown("---")
    temp_sens = st.selectbox("Temperature Sensitivity", ["Low", "Medium", "High"])
    moisture_sens = st.selectbox("Moisture Sensitivity", ["Low", "Medium", "High"])
    predict_btn = st.button("Generate Analytics")

# --- 5. MAIN CONTENT ---
st.title("📦 EcoPack Smart Advisor")

if predict_btn:
    with st.spinner('Fetching Sustainability Data...'):
        engine = get_db_engine()
        query = f'SELECT * FROM public."Material_dataset" WHERE weight_capacity_kg >= {weight} AND strength_score >= {fragility}'
        df = pd.read_sql(query, engine)

        if not df.empty:
            if moisture_sens != "Low":
                df = df[df['moisture_resistance'].isin([moisture_sens, "High"])]
            
            top_df = df.sort_values(by="eco_score", ascending=False).head(10)
            best = top_df.iloc[0]

            # TOP PICK BANNER
            st.success(f"🏆 Top Recommendation: {best['material_name']}")
            
            # HERO METRICS
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Eco Score", f"{best['eco_score']}")
            c2.metric("Cost/Unit", f"${best['cost_per_unit_usd']:.2f}")
            c3.metric("CO2 Impact", f"{best['co2_emission_kg']:.2f}kg")
            c4.metric("Recyclable", f"{best['recyclability_percent']}%")

            st.divider()

            # --- NEW: COMPARISON TABLE SECTION ---
            st.subheader("📊 Candidate Comparison Matrix")
            
            # Select and rename columns for a cleaner table look
            comparison_table = top_df[['material_name', 'eco_score', 'cost_per_unit_usd', 'co2_emission_kg', 'recyclability_percent']].copy()
            comparison_table.columns = ['Material Name', 'Eco Score', 'Cost ($)', 'CO2 (kg)', 'Recyclability %']
            
            # Displaying the top 5 for comparison
            st.table(comparison_table.head(5)) 

            st.divider()
            
            # CHART SECTION
            st.subheader("Sustainability Benchmark (Visual)")
            st.bar_chart(top_df.head(5).set_index('material_name')['eco_score'])

            # EXPORT
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                top_df.to_excel(writer, index=False)
            st.download_button("📥 Export CSV/Excel", output.getvalue(), "EcoPack_Analytics.xlsx")
        else:
            st.error("No materials meet these requirements.")

else:
    st.image("https://www.upack.in/media/magefan_blog/50.png", caption="E-commerce Packaging Standards", use_container_width=True)
    st.info("👈 Enter product specifications in the sidebar to generate the comparison matrix.")
