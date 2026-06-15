import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from PIL import Image

_favicon = Image.open(Path(__file__).parent / "assets" / "se_favicon.ico")

st.set_page_config(
    page_title="OM SHP Dashboard",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Theme (Dark only) ---
THEME_TEXT = "#e8eaf2"
THEME_BG_CARD = "rgba(26,31,48,.85)"
THEME_CHART_FONT = "#e8eaf2"

# --- Data Loading from CSV ---
DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_dm():
    df = pd.read_csv(DATA_DIR / "dm_data.csv", header=None,
                     names=["MONTH", "TEAM", "CATEGORY", "PLANT", "EU_NONEU",
                            "LAND_ENDKUNDE", "TRATY_CODE", "LIEFERSPERRE",
                            "TRANSPORTSPERRGRUND", "NZV_FLAG", "AUSWERTUNG"])
    return df

@st.cache_data
def load_kl():
    df = pd.read_csv(DATA_DIR / "kl_data.csv", header=None,
                     names=["MONTH", "TEAM", "PROJKENNW", "GESCHAEFTSGEBIET_KZ",
                            "ORG_ID_ABSENDER", "VERSANDZUST_DEU", "STADT_WARBE_VB",
                            "LANDNAME_FM", "LANDNAME_ENDVERW", "TV_NR", "PACKNR",
                            "RECHNR", "KOLLONR_LIEFERANT"])
    return df

df_dm = load_dm()
df_kl = load_kl()

# --- Helpers ---
def safe_pct(part, total):
    return f"{part/total*100:.1f}%" if total > 0 else "0%"

def kpi_card(label, value, color=None, sub=""):
    if color is None:
        color = THEME_TEXT
    bg = THEME_BG_CARD
    return f"""<div style='background:{bg};border:1px solid rgba(42,48,80,.5);border-radius:8px;padding:10px 12px'>
    <div style='font-size:10px;color:#7b85a8'>{label}</div>
    <div style='font-size:22px;font-weight:500;color:{color}'>{value}</div>
    <div style='font-size:9px;color:#7b85a8;opacity:.6;font-style:italic'>{sub}</div></div>"""

def color_box(value, label, color):
    bg = f"rgba({','.join(str(int(color[i:i+2],16)) for i in (1,3,5))},.1)"
    border = f"rgba({','.join(str(int(color[i:i+2],16)) for i in (1,3,5))},.25)"
    return f"""<div style='background:{bg};border:1px solid {border};border-radius:8px;padding:9px;text-align:center'>
    <div style='font-size:18px;font-weight:500;color:{color}'>{value:,}</div>
    <div style='font-size:9px;color:{color}'>{label}</div></div>"""

def dark_layout(fig, height=250, title="", subtitle=""):
    fig.update_layout(
        paper_bgcolor=THEME_BG_CARD, plot_bgcolor="rgba(0,0,0,0)",
        font_color=THEME_CHART_FONT, height=height,
        margin=dict(t=50 if title else 20, b=20, l=20, r=20),
        xaxis=dict(gridcolor="rgba(42,48,80,.6)", title=""),
        yaxis=dict(gridcolor="rgba(42,48,80,.6)", title=""),
        hoverlabel=dict(bgcolor="#1a1f30", font_size=12, font_color="#e8eaf2", bordercolor="#2a3050"),
    )
    if title:
        fig.update_layout(
            title=dict(
                text=f"<b>{title}</b><br><span style='font-size:10px;color:#7b85a8;font-style:italic'>{subtitle}</span>" if subtitle else f"<b>{title}</b>",
                x=0.02, y=0.97, xanchor="left", yanchor="top",
                font=dict(size=13, color=THEME_TEXT),
            ),
            margin=dict(t=55, b=20, l=20, r=20),
        )
    for trace in fig.data:
        if hasattr(trace, 'type'):
            if trace.type == 'bar':
                trace.hovertemplate = '<b>%{x}</b>: %{y:,}<extra></extra>' if trace.orientation != 'h' else '<b>%{y}</b>: %{x:,}<extra></extra>'
            elif trace.type == 'pie':
                trace.hovertemplate = '<b>%{label}</b>: %{value:,} (%{percent})<extra></extra>'
    return fig

# Inject CSS for spacing and card styling
st.markdown("""<style>
[data-testid="stPlotlyChart"] {
    border: 1px solid rgba(42,48,80,.5);
    border-radius: 8px;
    padding: 4px;
    margin-top: 8px;
    margin-bottom: 12px;
}
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
    margin-bottom: 6px;
}
[data-testid="column"] > div {
    gap: 0.4rem;
}
h3 {
    margin-top: 16px !important;
    margin-bottom: 4px !important;
}
</style>""", unsafe_allow_html=True)

# --- Sidebar Filters ---

st.sidebar.markdown("### Shipping Operations Dashboard")
st.sidebar.caption("SE GS C LGT OM SHP ·  Gasturbinenwerk Berlin")
st.sidebar.divider()

# Refresh button
if st.sidebar.button("Refresh", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.divider()

period = st.sidebar.selectbox("Period", ["Jul–Sep 2025", "Jul 2025", "Aug 2025", "Sep 2025"])
team_filter = st.sidebar.selectbox("Team", ["All teams", "Bukarest", "Berlin", "LWF"])
category = st.sidebar.selectbox("Category", ["All", "AWV", "NZV", "Sonstige"])
plant = st.sidebar.selectbox("Plant", ["All", "1201", "1203", "12S1"])

period_map = {"Jul–Sep 2025": None, "Jul 2025": "2025-07", "Aug 2025": "2025-08", "Sep 2025": "2025-09"}
period_val = period_map[period]

# --- Apply Filters ---
dm = df_dm.copy()
if period_val:
    dm = dm[dm["MONTH"] == period_val]
if team_filter != "All teams":
    dm = dm[dm["TEAM"] == team_filter]
if category != "All":
    dm = dm[dm["CATEGORY"] == category]
if plant != "All":
    dm = dm[dm["PLANT"] == plant]

kl = df_kl.copy()
if period_val:
    kl = kl[kl["MONTH"] == period_val]
if team_filter != "All teams":
    kl = kl[kl["TEAM"] == team_filter]

# --- Header ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("# OM SHP Dashboard")
with col_h2:
    st.markdown(
        """<div style='text-align:right;padding-top:10px'>
        <span style='background:rgba(0,201,177,.12);color:#00c9b1;padding:4px 10px;border-radius:99px;font-size:11px;border:1px solid rgba(0,201,177,.3)'>● Live</span>
        </div>""", unsafe_allow_html=True)

active_filters = sum([period_val is not None, team_filter != "All teams", category != "All", plant != "All"])
if active_filters > 0:
    st.markdown(f"<div style='background:rgba(0,201,177,.08);border:1px solid rgba(0,201,177,.2);border-radius:6px;padding:7px 12px;font-size:11px;color:#00c9b1;margin-bottom:10px'>⚡ {active_filters} filter(s) active · {len(dm):,} DM / {len(kl):,} KL records</div>", unsafe_allow_html=True)

# ===========================================================
# DELIVERY MONITOR
# ===========================================================
tab_dm, tab_kl = st.tabs(["Delivery Monitor", "KanLog"])

with tab_dm:
    total = len(dm)
    if total == 0:
        st.warning("Keine Daten fuer die aktuelle Filterauswahl.")
    else:
        subtab_ov, subtab_st, subtab_rts, subtab_bn, subtab_sp = st.tabs(
            ["Overview", "Status Signals", "Ready to Ship", "Bottlenecks", "Special Cases"])

        awv = len(dm[dm["CATEGORY"] == "AWV"])
        eu = len(dm[dm["EU_NONEU"] == "EU"])
        noneu = len(dm[dm["EU_NONEU"] == "NONEU"])
        nzv_flag = len(dm[dm["NZV_FLAG"] == "Ja"])
        nzv_traty = len(dm[dm["TRATY_CODE"] == "ZZZ"])

        with subtab_ov:
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.markdown(kpi_card("Total deliveries", f"{total:,}"), unsafe_allow_html=True)
            c2.markdown(kpi_card("AWV deliveries", f"{awv:,}", "#00c9b1", "WTH 0009 + 0010"), unsafe_allow_html=True)
            c3.markdown(kpi_card("EU", f"{eu:,}", THEME_TEXT, safe_pct(eu, total) + " of total"), unsafe_allow_html=True)
            c4.markdown(kpi_card("NONEU", f"{noneu:,}", THEME_TEXT, safe_pct(noneu, total) + " of total"), unsafe_allow_html=True)
            c5.markdown(kpi_card("NZV flag", f"{nzv_flag:,}", "#f39c12", 'NZV_Flag = "Ja"'), unsafe_allow_html=True)
            c6.markdown(kpi_card("NzV transport", f"{nzv_traty:,}", "#f39c12", 'TRATY_Code = "ZZZ"'), unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                team_counts = dm["TEAM"].value_counts().reset_index()
                team_counts.columns = ["Team", "Count"]
                fig = px.pie(team_counts, values="Count", names="Team",
                             color_discrete_sequence=["#9b59d0", "#00c9b1", "#f39c12"], hole=0.55)
                st.plotly_chart(dark_layout(fig, 280, "Team Assignment", f"TEAM · {total:,} deliveries"), use_container_width=True)

            with col2:
                month_counts = dm["MONTH"].value_counts().sort_index().reset_index()
                month_counts.columns = ["Month", "Count"]
                month_names = {"2025-07": "Jul 2025", "2025-08": "Aug 2025", "2025-09": "Sep 2025"}
                month_counts["Label"] = month_counts["Month"].map(month_names).fillna(month_counts["Month"])
                fig = px.bar(month_counts, x="Label", y="Count", color_discrete_sequence=["#9b59d0"],
                             category_orders={"Label": ["Jul 2025", "Aug 2025", "Sep 2025"]})
                fig.update_layout(xaxis_type="category")
                st.plotly_chart(dark_layout(fig, 280, "Monthly Volume", f"MONTH · {total:,} deliveries"), use_container_width=True)

            st.markdown("**Auswertung Categories**")
            st.caption(f"AUSWERTUNG · top 6 of {total:,}")
            ausw = dm["AUSWERTUNG"].value_counts().head(6)
            rows_html = ""
            for cat_name, cnt in ausw.items():
                rows_html += f"""<div style='display:flex;justify-content:space-between;align-items:center;padding:6px 9px;background:#181c27;border-radius:6px;border:1px solid #2a3050;margin-bottom:4px'>
                <span style='font-size:11px;color:{THEME_TEXT}'>{cat_name}</span>
                <span style='font-size:12px;font-weight:500;color:{THEME_TEXT}'>{cnt:,}</span></div>"""
            st.markdown(rows_html, unsafe_allow_html=True)

        with subtab_st:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**B1 · Transport Mode**")
                st.caption("TRATY_Code field")
                traty_map = {"T": "LKW Ladung", "C": "Kurier", "ZZZ": "NzV billing", "LT": "Sammelgut", "A": "Luftfracht", "S": "Seefracht"}
                traty_colors = {"T": "#2ecc71", "C": "#4a90d9", "ZZZ": "#f39c12", "LT": "#7b85a8", "A": "#7b85a8", "S": "#7b85a8"}
                traty = dm["TRATY_CODE"].value_counts().head(6)
                rows_html = ""
                for code, count in traty.items():
                    label = f"{traty_map.get(code, code)} ({code})"
                    color = traty_colors.get(code, "#7b85a8")
                    rows_html += f"""<div style='display:flex;justify-content:space-between;align-items:center;padding:6px 9px;background:#181c27;border-radius:6px;border:1px solid #2a3050;margin-bottom:4px'>
                    <span style='font-size:11px;color:{THEME_TEXT}'>{label}</span>
                    <span style='font-size:12px;font-weight:500;color:{color}'>{count:,}</span></div>"""
                st.markdown(rows_html, unsafe_allow_html=True)

            with col2:
                st.markdown("**B2 · ECC Customs**")
                st.caption("Liefersperre field")
                zh = len(dm[dm["LIEFERSPERRE"] == "ZH"])
                ze = len(dm[dm["LIEFERSPERRE"] == "ZE"])
                z1 = len(dm[dm["LIEFERSPERRE"] == "Z1"])
                st.markdown(f"<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px'>{color_box(zh,'ZH released','#2ecc71')}{color_box(ze,'ZE blocked','#e74c3c')}{color_box(z1,'Z1 partial','#f39c12')}</div>", unsafe_allow_html=True)

            with col3:
                st.markdown("**B3 · Transport Lock**")
                st.caption("Transportsperrgrund")
                l3 = len(dm[dm["TRANSPORTSPERRGRUND"] == 3.0])
                l2 = len(dm[dm["TRANSPORTSPERRGRUND"] == 2.0])
                l_other = total - l3 - l2
                st.markdown(f"<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px'>{color_box(l3,'Released (03)','#2ecc71')}{color_box(l2,'Locked (02)','#e74c3c')}{color_box(l_other,'Freigegeben','#f39c12')}</div>", unsafe_allow_html=True)
                if l2 > 0:
                    st.markdown(f"<div style='background:rgba(0,201,177,.08);border:1px solid rgba(0,201,177,.2);border-radius:6px;padding:7px 10px;font-size:10px;color:#00c9b1;margin-top:8px'>{l2} locked deliveries (02) need action</div>", unsafe_allow_html=True)

            countries = dm["LAND_ENDKUNDE"].value_counts().head(8).reset_index()
            countries.columns = ["Country", "Count"]
            bar_colors = ["#9b59d0", "#00c9b1", "#4a90d9", "#f39c12", "#e74c3c", "#2ecc71", "#7b85a8", "#854F0B"]
            fig = go.Figure(go.Bar(x=countries["Count"].tolist(), y=countries["Country"].tolist(), orientation="h",
                                   marker_color=bar_colors[:len(countries)]))
            fig.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(dark_layout(fig, 330, "Top Destination Countries", f"LAND_ENDKUNDE · {total:,} deliveries"), use_container_width=True)

        with subtab_rts:
            st.markdown("**D · READY TO SHIP**")
            ready = len(dm[(dm["LIEFERSPERRE"] == "ZH") & (dm["TRANSPORTSPERRGRUND"] == 3.0) &
                           (dm["TRATY_CODE"] != "ZZZ") & (dm["NZV_FLAG"] == "Nein")])
            not_ready = total - ready
            st.markdown(f"""<div style='background:{THEME_BG_CARD};border:1px solid rgba(42,48,80,.5);border-radius:10px;padding:14px 16px;margin-bottom:12px'>
            <div style='font-size:13px;font-weight:600;color:{THEME_TEXT}'>Ready to ship formula</div>
            <div style='font-size:11px;color:#00c9b1;font-style:italic;margin-top:2px'>Liefersperre="ZH" AND Transportsperrgrund=3 AND TRATY_Code≠"ZZZ" AND NZV_Flag="Nein"</div></div>""", unsafe_allow_html=True)
            r1, r2 = st.columns(2)
            with r1:
                st.markdown(f"""<div style='background:rgba(46,204,113,.1);border:1px solid rgba(46,204,113,.25);border-radius:12px;padding:20px;text-align:center'>
                <div style='font-size:36px;font-weight:600;color:#2ecc71'>{ready:,}</div>
                <div style='font-size:14px;color:#2ecc71'>Ready to ship</div>
                <div style='font-size:12px;color:rgba(46,204,113,.7)'>{safe_pct(ready, total)} of total</div></div>""", unsafe_allow_html=True)
            with r2:
                st.markdown(f"""<div style='background:rgba(231,76,60,.1);border:1px solid rgba(231,76,60,.25);border-radius:12px;padding:20px;text-align:center'>
                <div style='font-size:36px;font-weight:600;color:#e74c3c'>{not_ready:,}</div>
                <div style='font-size:14px;color:#e74c3c'>Not ready</div>
                <div style='font-size:12px;color:rgba(231,76,60,.7)'>{safe_pct(not_ready, total)} of total</div></div>""", unsafe_allow_html=True)

            # Schedule by month
            st.markdown("**C · SCHEDULE BY MONTH**")
            months_rts = dm["MONTH"].value_counts().sort_index()
            month_names_rts = {"2025-07": "Jul 2025", "2025-08": "Aug 2025", "2025-09": "Sep 2025"}
            mc = st.columns(len(months_rts)) if len(months_rts) > 0 else []
            for i, (m, cnt) in enumerate(months_rts.items()):
                mc[i].markdown(kpi_card(month_names_rts.get(m, m), f"{cnt:,}", None, safe_pct(cnt, total) + " of quarter"), unsafe_allow_html=True)

        with subtab_bn:
            st.markdown("**E · BOTTLENECKS**")
            nzv_zzz = len(dm[dm["TRATY_CODE"] == "ZZZ"])
            ecc_ze = len(dm[dm["LIEFERSPERRE"] == "ZE"])
            nzv_fl = len(dm[dm["NZV_FLAG"] == "Ja"])
            lock_02 = len(dm[dm["TRANSPORTSPERRGRUND"] == 2.0])
            ecc_z1 = len(dm[dm["LIEFERSPERRE"] == "Z1"])
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Open Blockers")
                blockers = [
                    ("E1 · NzV billing (ZZZ)", 'TRATY_Code = "ZZZ"', nzv_zzz, "#f39c12"),
                    ("E2 · ECC blocked (ZE)", 'Liefersperre = "ZE"', ecc_ze, "#e74c3c"),
                    ("E3 · NZV flag active", 'NZV_Flag = "Ja"', nzv_fl, "#f39c12"),
                    ("E4 · Transport locked", 'Transportsperrgrund = 2', lock_02, "#e74c3c"),
                    ("E5 · ECC partial (Z1)", 'Liefersperre = "Z1"', ecc_z1, "#7b85a8"),
                ]
                rows_html = ""
                for label, sub, val, color in blockers:
                    rows_html += f"""<div style='display:flex;justify-content:space-between;align-items:center;padding:8px 10px;background:#181c27;border-radius:6px;border:1px solid #2a3050;margin-bottom:4px'>
                    <div><div style='font-size:11px;color:{THEME_TEXT}'>{label}</div><div style='font-size:9px;color:#7b85a8;font-style:italic'>{sub}</div></div>
                    <span style='font-size:13px;font-weight:500;color:{color}'>{val:,}</span></div>"""
                st.markdown(rows_html, unsafe_allow_html=True)
            with col2:
                if sum([nzv_zzz, ecc_ze, nzv_fl, lock_02, ecc_z1]) > 0:
                    fig = px.pie(values=[nzv_zzz, ecc_ze, nzv_fl, lock_02, ecc_z1],
                                 names=["NzV ZZZ", "ECC ZE", "NZV flag", "Lock 02", "Z1"],
                                 color_discrete_sequence=["#f39c12", "#e74c3c", "#854F0B", "#c0392b", "#7b85a8"], hole=0.5)
                    st.plotly_chart(dark_layout(fig, 330, "Blocker Distribution", "Share of open blockers"), use_container_width=True)

        with subtab_sp:
            st.markdown("**F · SPECIAL CASES — NZV**")
            wth12 = len(dm[dm["AUSWERTUNG"].str.contains("WTH 0012", na=False)])
            wth09 = len(dm[dm["AUSWERTUNG"].str.contains("WTH 0009", na=False)])
            wth10 = len(dm[dm["AUSWERTUNG"].str.contains("WTH 0010", na=False)])
            sonstige = len(dm[dm["AUSWERTUNG"].str.contains("Sonstige", na=False)])
            c1, c2, c3 = st.columns(3)
            c1.markdown(kpi_card("NZV flag", f"{nzv_flag:,}", "#f39c12", 'NZV_Flag = "Ja"'), unsafe_allow_html=True)
            c2.markdown(kpi_card("NzV transport", f"{nzv_traty:,}", "#f39c12", 'TRATY_Code = "ZZZ"'), unsafe_allow_html=True)
            c3.markdown(kpi_card("WTH 0012 category", f"{wth12:,}", "#f39c12", "Auswertung NzV"), unsafe_allow_html=True)
            c4, c5, c6 = st.columns(3)
            c4.markdown(kpi_card("AWV with SAP EU", f"{wth09:,}", "#00c9b1", "WTH 0009"), unsafe_allow_html=True)
            c5.markdown(kpi_card("AWV ohne KanLog", f"{wth10:,}", "#00c9b1", "WTH 0010 DE"), unsafe_allow_html=True)
            c6.markdown(kpi_card("Sonstige", f"{sonstige:,}", "#7b85a8", "Not categorised"), unsafe_allow_html=True)

# ===========================================================
# KANLOG
# ===========================================================
with tab_kl:
    kl_total = len(kl)
    if kl_total == 0:
        st.warning("Keine KanLog-Daten fuer die aktuelle Filterauswahl. (KanLog hat nur Teams Bukarest und Berlin)")
    else:
        kl_bukarest = len(kl[kl["TEAM"] == "Bukarest"])
        kl_berlin = len(kl[kl["TEAM"] == "Berlin"])
        subtab_vol, subtab_geo, subtab_proj, subtab_ops = st.tabs(["Volume", "Geography", "Projects", "Operations"])

        with subtab_vol:
            st.markdown("**VOLUME OVERVIEW**")
            kl_invoices = kl["RECHNR"].nunique()
            kl_months = kl["MONTH"].nunique()
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.markdown(kpi_card("Total shipments", f"{kl_total:,}", None, "filtered"), unsafe_allow_html=True)
            c2.markdown(kpi_card("Bukarest", f"{kl_bukarest:,}", "#9b59d0", safe_pct(kl_bukarest, kl_total)), unsafe_allow_html=True)
            c3.markdown(kpi_card("Berlin", f"{kl_berlin:,}", "#00c9b1", safe_pct(kl_berlin, kl_total)), unsafe_allow_html=True)
            c4.markdown(kpi_card("Avg / month", f"{kl_total // max(1, kl_months):,}", None, f"{kl_months} / months"), unsafe_allow_html=True)
            c5.markdown(kpi_card("Invoices", f"{kl_invoices:,}", None, "Distinct Rechnr"), unsafe_allow_html=True)
            c6.markdown(kpi_card("Ships / invoice", f"{kl_total/max(1,kl_invoices):.1f}", "#2ecc71", "Ratio"), unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                monthly_team = kl.groupby(["MONTH", "TEAM"]).size().reset_index(name="Count")
                month_labels = {"2025-07": "Jul 2025", "2025-08": "Aug 2025", "2025-09": "Sep 2025"}
                monthly_team["Label"] = monthly_team["MONTH"].map(month_labels).fillna(monthly_team["MONTH"])
                fig = px.bar(monthly_team, x="Label", y="Count", color="TEAM",
                             color_discrete_map={"Bukarest": "#9b59d0", "Berlin": "#00c9b1"}, barmode="stack",
                             category_orders={"Label": ["Jul 2025", "Aug 2025", "Sep 2025"]})
                fig.update_layout(legend_title="", xaxis_type="category")
                st.plotly_chart(dark_layout(fig, 280, "Monthly Shipments by Team", f"MONTH × TEAM · {kl_total:,} shipments"), use_container_width=True)
            with col2:
                areas = kl["GESCHAEFTSGEBIET_KZ"].value_counts().reset_index()
                areas.columns = ["Area", "Count"]
                fig = px.pie(areas, values="Count", names="Area",
                             color_discrete_sequence=["#9b59d0", "#00c9b1", "#4a90d9", "#f39c12", "#7b85a8"], hole=0.55)
                st.plotly_chart(dark_layout(fig, 280, "Business area split", f"Geschaeftsgebiet_Kz · {kl_total:,} shipments"), use_container_width=True)

        with subtab_geo:
            countries_kl = kl["LANDNAME_ENDVERW"].value_counts()
            n_countries = len(countries_kl[countries_kl.index != ""])
            transit_de = len(kl[kl["LANDNAME_FM"] == "Deutschland"])
            domestic = len(kl[kl["LANDNAME_ENDVERW"] == "Deutschland"])
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(kpi_card("Dest. countries", f"{n_countries}", None, "Landname_Endverw distinct"), unsafe_allow_html=True)
            c2.markdown(kpi_card("Transit via DE", f"{transit_de:,}", "#2ecc71", "Landname_FM = Deutschland"), unsafe_allow_html=True)
            c3.markdown(kpi_card("Domestic DE", f"{domestic:,}", "#00c9b1", "Landname_Endverw = DE"), unsafe_allow_html=True)
            c4.markdown(kpi_card("International", f"{kl_total - domestic:,}", None, "Landname_Endverw ≠ DE"), unsafe_allow_html=True)

            top_countries = countries_kl[countries_kl.index != ""].head(10).reset_index()
            top_countries.columns = ["Country", "Count"]
            geo_colors = ["#9b59d0", "#00c9b1", "#4a90d9", "#f39c12", "#e74c3c", "#2ecc71", "#7b85a8", "#854F0B", "#1abc9c", "#c0392b"]
            fig = go.Figure(go.Bar(x=top_countries["Count"].tolist(), y=top_countries["Country"].tolist(),
                                   orientation="h", marker_color=geo_colors[:len(top_countries)]))
            fig.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(dark_layout(fig, 380, "Top 10 Destination Countries", f"Landname_Endverw · {kl_total:,} shipments"), use_container_width=True)

        with subtab_proj:
            projects = kl["PROJKENNW"].value_counts()
            projects_valid = projects[projects.index != ""]
            top_proj = projects_valid.head(12).reset_index()
            top_proj.columns = ["Project", "Shipments"]
            proj_meta = kl[kl["PROJKENNW"] != ""].drop_duplicates("PROJKENNW")[["PROJKENNW", "GESCHAEFTSGEBIET_KZ", "TEAM"]]
            top_proj = top_proj.merge(proj_meta, left_on="Project", right_on="PROJKENNW", how="left")
            top_proj = top_proj[["Project", "GESCHAEFTSGEBIET_KZ", "TEAM", "Shipments"]]
            top_proj.columns = ["Project", "Area", "Team", "Shipments"]

            c1, c2, c3 = st.columns(3)
            c1.markdown(kpi_card("Active projects", f"{len(projects_valid)}", None, "Distinct Projkennw"), unsafe_allow_html=True)
            c2.markdown(kpi_card("Top project", f"{top_proj.iloc[0]['Shipments']}" if len(top_proj) > 0 else "0", "#00c9b1",
                                 top_proj.iloc[0]["Project"] if len(top_proj) > 0 else ""), unsafe_allow_html=True)
            c3.markdown(kpi_card("Top 5 share", safe_pct(top_proj.head(5)["Shipments"].sum(), kl_total), None, "% of total shipments"), unsafe_allow_html=True)

            # Business area volume cards
            st.markdown("**Business area volume**")
            st.caption("Shipments per Geschaeftsgebiet_Kz")
            area_counts = kl["GESCHAEFTSGEBIET_KZ"].value_counts()
            area_cols = st.columns(min(len(area_counts), 5))
            area_color_map = {"W": "#9b59d0", "O": "#00c9b1", "P3": "#4a90d9", "G": "#f39c12", "SLS": "#7b85a8"}
            for i, (area_name, area_cnt) in enumerate(area_counts.head(5).items()):
                area_cols[i].markdown(kpi_card(area_name, f"{area_cnt:,}", area_color_map.get(area_name, "#7b85a8"), safe_pct(area_cnt, kl_total)), unsafe_allow_html=True)

            st.markdown("**Top 12 Projects**")
            st.caption("Projkennw · Geschaeftsgebiet_Kz · Team")
            st.dataframe(top_proj, use_container_width=True, hide_index=True)

        with subtab_ops:
            tv_nrs = kl["TV_NR"].nunique()
            packs = kl["PACKNR"].nunique()
            invoices = kl["RECHNR"].nunique()
            kollonrs = kl["KOLLONR_LIEFERANT"].nunique()
            orgs = kl[kl["ORG_ID_ABSENDER"] != ""]["ORG_ID_ABSENDER"].nunique()
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.markdown(kpi_card("Transport orders", f"{tv_nrs:,}", None, "Distinct TV_Nr"), unsafe_allow_html=True)
            c2.markdown(kpi_card("Pack orders", f"{packs:,}", None, "Distinct Packnr"), unsafe_allow_html=True)
            c3.markdown(kpi_card("Invoices", f"{invoices:,}", None, "Distinct Rechnr"), unsafe_allow_html=True)
            c4.markdown(kpi_card("Ships / invoice", f"{kl_total/max(1,invoices):.1f}", "#2ecc71", "Ratio"), unsafe_allow_html=True)
            c5.markdown(kpi_card("Unique suppliers", f"{kollonrs:,}", None, "Distinct Kollonr_Lieferant"), unsafe_allow_html=True)
            c6.markdown(kpi_card("ORG senders", f"{orgs}", "#00c9b1", "Distinct Org_ID_Absender"), unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Sender Organisations")
                st.caption("Org_ID_Absender")
                org_counts = kl["ORG_ID_ABSENDER"].value_counts().head(5)
                rows_html = ""
                for org_id, cnt in org_counts.items():
                    label = org_id if org_id else "NULL records"
                    color = "#e74c3c" if not org_id else "#2ecc71"
                    rows_html += f"""<div style='display:flex;justify-content:space-between;align-items:center;padding:6px 9px;background:#181c27;border-radius:6px;border:1px solid #2a3050;margin-bottom:4px'>
                    <span style='font-size:11px;color:{THEME_TEXT}'>{label}</span>
                    <span style='font-size:12px;font-weight:500;color:{color}'>{cnt:,} ({safe_pct(cnt, kl_total)})</span></div>"""
                st.markdown(rows_html, unsafe_allow_html=True)
            with col2:
                ff_ops = kl[kl["STADT_WARBE_VB"] != ""]["STADT_WARBE_VB"].value_counts().head(5).reset_index()
                ff_ops.columns = ["City", "Count"]
                fig = px.bar(ff_ops, x="City", y="Count", color_discrete_sequence=["#00c9b1"])
                st.plotly_chart(dark_layout(fig, 280, "Freight Forwarder Hubs", f"Stadt_Warbe_VB · {kl_total:,} shipments"), use_container_width=True)
