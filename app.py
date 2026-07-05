import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# PAGE SETTINGS
# -------------------------------------------------

st.set_page_config(
    page_title="Laboratory Quality Dashboard - DXC 700",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Biochemistry Laboratory Quality Dashboard - DXC 700")
st.markdown("### Measurement Uncertainty - Total Error (MUTE) Decision Support System")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

data = pd.read_excel(
    "ICMR 2025 MU and TAE.xlsx",
    sheet_name="FINAL DATA L1",
    header=1
)

# Rename columns
data.columns = [
    "Analytes",
    "MU",
    "Allowable MU",
    "TE",
    "TEa",
    "MU index",
    "TE index",
    "MUTE index",
    "Blank",
    "B1","B2","B3","B4","B5","B6","B7"
]

# Keep only required columns
data = data[
    [
        "Analytes",
        "MU",
        "Allowable MU",
        "TE",
        "TEa",
        "MU index",
        "TE index",
        "MUTE index"
    ]
]

# Remove empty rows
data = data.dropna(subset=["Analytes"])

# -------------------------------------------------
# CREATE STATUS COLUMN
# -------------------------------------------------

def status(m):

    if m < 0.50:
        return "🟢 Excellent"

    elif m < 1.00:
        return "🟡 Acceptable"

    else:
        return "🔴 Needs Improvement"

data["Status"] = data["MUTE index"].apply(status)

# -------------------------------------------------
# LAB SUMMARY
# -------------------------------------------------

good = len(data[data["MUTE index"] < 0.50])
acceptable = len(data[(data["MUTE index"] >= 0.50) &
                      (data["MUTE index"] < 1.00)])
poor = len(data[data["MUTE index"] >= 1.00])

c1, c2, c3, c4 = st.columns(4)

c1.metric("Analytes", len(data))
c2.metric("🟢 Excellent", good)
c3.metric("🟡 Acceptable", acceptable)
c4.metric("🔴 Needs Improvement", poor)

st.divider()

# -------------------------------------------------
# ANALYTE SELECTION
# -------------------------------------------------

analyte = st.selectbox(
    "🔍 Select Analyte",
    sorted(data["Analytes"])
)

selected = data[data["Analytes"] == analyte]

st.subheader(f"📋 Quality Assessment : {analyte}")

# -------------------------------------------------
# KPI CARDS
# -------------------------------------------------

row1 = st.columns(4)

row1[0].metric("Measurement Uncertainity (MU)",
               f"{selected['MU'].values[0]:.2f}%")

row1[1].metric("Allowable MU",
               f"{selected['Allowable MU'].values[0]:.2f}%")

row1[2].metric("Total Error (TE)",
               f"{selected['TE'].values[0]:.2f}%")

row1[3].metric("TE allowable",
               f"{selected['TEa'].values[0]:.2f}%")

row2 = st.columns(3)

row2[0].metric("MU Index",
               f"{selected['MU index'].values[0]:.2f}")

row2[1].metric("TE Index",
               f"{selected['TE index'].values[0]:.2f}")

row2[2].metric("MUTE Index",
               f"{selected['MUTE index'].values[0]:.2f}")

# -------------------------------------------------
# STATUS
# -------------------------------------------------

status_value = selected["Status"].values[0]

if "Excellent" in status_value:
    st.success(status_value)

elif "Acceptable" in status_value:
    st.warning(status_value)

else:
    st.error(status_value)

st.sidebar.markdown("## 🚦 MUTE Classification")

st.sidebar.success("🟢 Excellent\n\nMUTE < 0.75")

st.sidebar.warning("🟡 Acceptable\n\n0.75 ≤ MUTE ≤ 1.00")

st.sidebar.error("🔴 Needs Improvement\n\nMUTE > 1.00")

# -------------------------------------------------
# AI RECOMMENDATION
# -------------------------------------------------

st.subheader("🤖 AI Recommendation")

mu = selected["MU index"].values[0]
te = selected["TE index"].values[0]

if mu > 1 and te < 1:

    st.warning("""
### Primary Issue
**High Measurement Uncertainty**

### Suggested Actions

• Review long-term IQC precision

• Verify instrument maintenance

• Check calibration performance

• Review operator technique

• Continue monitoring after corrective action
""")

elif mu < 1 and te > 1:

    st.warning("""
### Primary Issue
**High Total Error**

### Suggested Actions

• Review calibration

• Review External Quality Assessment (EQA)

• Check reagent lot performance

• Investigate systematic bias
""")

elif mu > 1 and te > 1:

    st.error("""
### Primary Issue
**Critical Analytical Performance**

### Suggested Actions

• Immediate corrective action required

• Review IQC precision

• Verify calibration

• Review EQA performance

• Check reagent lot

• Perform maintenance

• Repeat analytical verification
""")

else:

    st.success("""
### Primary Issue
**Within Analytical Specification**

### Suggested Actions

• Continue routine IQC

• Continue scheduled maintenance

• Maintain present analytical performance
""")

st.divider()

st.divider()

st.subheader("📈 MU Index vs TE Index (Risk Quadrants)")

fig = px.scatter(
    data,
    x="MU index",
    y="TE index",
    text="Analytes",
    color="MUTE index",
    hover_name="Analytes",
    hover_data={
        "MU":":.2f",
        "TE":":.2f",
        "MUTE index":":.2f"
    },
    color_continuous_scale="RdYlGn_r",
    height=650
)

# Decision limits
fig.add_vline(
    x=1,
    line_dash="dash",
    line_color="red",
    annotation_text="MU Target",
    annotation_position="top"
)

fig.add_hline(
    y=1,
    line_dash="dash",
    line_color="red",
    annotation_text="TE Target",
    annotation_position="right"
)

# Improve label placement
fig.update_traces(
    textposition="top center",
    marker=dict(size=16)
)

fig.update_layout(
    xaxis_title="MU Index",
    yaxis_title="TE Index",
    title="Risk Quadrant Analysis",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)
# -------------------------------------------------
# MUTE RANKING CHART
# -------------------------------------------------

st.subheader("📊 MUTE Ranking")

chart = data.sort_values("MUTE index")

fig = px.bar(
    chart,
    x="MUTE index",
    y="Analytes",
    orientation="h",
    color="MUTE index",
    title="Ranking of Analytes by MUTE Index",
    text="MUTE index"
)

fig.update_layout(height=700)

st.plotly_chart(fig, use_container_width=True)

