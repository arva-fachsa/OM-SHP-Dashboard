import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Shipping Operations Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

def kpi_card(label, value, color="#e8eaf2", sub=""):
    return f"""<div style='background:#1a1f30;border:1px solid #2a3050;border-radius:8px;padding:10px 12px'>
    <div style='font-size:10px;color:#7b85a8'>{label}</div>
    <div style='font-size:22px;font-weight:500;color:{color}'>{value}</div>
    <div style='font-size:9px;color:#7b85a8;opacity:.6;font-style:italic'>{sub}</div></div>"""

def color_box(value, label, color):
    bg = f"rgba({','.join(str(int(color[i:i+2],16)) for i in (1,3,5))},.1)"
    border = f"rgba({','.join(str(int(color[i:i+2],16)) for i in (1,3,5))},.25)"
    return f"""<div style='background:{bg};border:1px solid {border};border-radius:8px;padding:9px;text-align:center'>
    <div style='font-size:18px;font-weight:500;color:{color}'>{value:,}</div>
    <div style='font-size:9px;color:{color}'>{label}</div></div>"""

def dark_layout(fig, height=250):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e8eaf2", height=height,
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis=dict(gridcolor="rgba(42,48,80,.6)", title=""),
        yaxis=dict(gridcolor="rgba(42,48,80,.6)", title=""),
    )
    return fig

# --- Sidebar Filters ---
st.sidebar.markdown("### Shipping Operations Dashboard")
st.sidebar.caption("SE GS C LOT OM SHP · Gasturbinen Berlin")
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
    st.markdown("# Shipping Operations Dashboard")
with col_h2:
    st.markdown(
        """<div style='text-align:right;padding-top:10px'>
        <span style='background:rgba(0,201,177,.12);color:#00c9b1;padding:4px 10px;border-radius:99px;font-size:12px;border:1px solid rgba(0,201,177,.3)'>● Live</span>
        <br><span style='color:#00c9b1;font-weight:500'>SIEMENS</span> <span style='color:#9b59d0;font-weight:500'>energy</span>
        </div>""", unsafe_allow_html=True)

active_filters = sum([period_val is not None, team_filter != "All teams", category != "All", plant != "All"])
if active_filters > 0:
    st.markdown(f"<div style='background:rgba(0,201,177,.08);border:1px solid rgba(0,201,177,.2);border-radius:6px;padding:7px 12px;font-size:11px;color:#00c9b1;margin-bottom:10px'>⚡ {active_filters} filter(s) active · {len(dm):,} DM / {len(kl):,} KL records</div>", unsafe_allow_html=True)

# ===========================================================
# DELIVERY MONITOR
# ===========================================================
tab_dm, tab_kl = st.tabs(["📦 Delivery Monitor", "🚚 KanLog"])

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
            c3.markdown(kpi_card("EU", f"{eu:,}", "#e8eaf2", safe_pct(eu, total) + " of total"), unsafe_allow_html=True)
            c4.markdown(kpi_card("NONEU", f"{noneu:,}", "#e8eaf2", safe_pct(noneu, total) + " of total"), unsafe_allow_html=True)
            c5.markdown(kpi_card("NZV flag", f"{nzv_flag:,}", "#f39c12", 'NZV_Flag = "Ja"'), unsafe_allow_html=True)
            c6.markdown(kpi_card("NzV transport", f"{nzv_traty:,}", "#f39c12", 'TRATY_Code = "ZZZ"'), unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Team Assignment")
                team_counts = dm["TEAM"].value_counts().reset_index()
                team_counts.columns = ["Team", "Count"]
                fig = px.pie(team_counts, values="Count", names="Team",
                             color_discrete_sequence=["#9b59d0", "#00c9b1", "#f39c12"], hole=0.55)
                st.plotly_chart(dark_layout(fig, 250), use_container_width=True)

            with col2:
                st.subheader("Monthly Volume")
                month_counts = dm["MONTH"].value_counts().sort_index().reset_index()
                month_counts.columns = ["Month", "Count"]
                month_names = {"2025-07": "Jul 2025", "2025-08": "Aug 2025", "2025-09": "Sep 2025"}
                month_counts["Label"] = month_counts["Month"].map(month_names).fillna(month_counts["Month"])
                fig = px.bar(month_counts, x="Label", y="Count", color_discrete_sequence=["#9b59d0"],
                             category_orders={"Label": ["Jul 2025", "Aug 2025", "Sep 2025"]})
                fig.update_layout(xaxis_type="category")
                st.plotly_chart(dark_layout(fig, 250), use_container_width=True)

            st.subheader("Auswertung Categories")
            ausw = dm["AUSWERTUNG"].value_counts().head(6)
            rows_html = ""
            for cat_name, cnt in ausw.items():
                rows_html += f"""<div style='display:flex;justify-content:space-between;align-items:center;padding:6px 9px;background:#181c27;border-radius:6px;border:1px solid #2a3050;margin-bottom:4px'>
                <span style='font-size:11px;color:#e8eaf2'>{cat_name}</span>
                <span style='font-size:12px;font-weight:500;color:#e8eaf2'>{cnt:,}</span></div>"""
            st.markdown(rows_html, unsafe_allow_html=True)

        with subtab_st:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader("Transport Mode")
                traty_map = {"T": "LKW Ladung", "C": "Kurier", "ZZZ": "NzV billing", "LT": "Sammelgut", "A": "Luftfracht", "S": "Seefracht"}
                traty_colors = {"T": "#2ecc71", "C": "#4a90d9", "ZZZ": "#f39c12", "LT": "#7b85a8", "A": "#7b85a8", "S": "#7b85a8"}
                traty = dm["TRATY_CODE"].value_counts().head(6)
                rows_html = ""
                for code, count in traty.items():
                    label = f"{traty_map.get(code, code)} ({code})"
                    color = traty_colors.get(code, "#7b85a8")
                    rows_html += f"""<div style='display:flex;justify-content:space-between;align-items:center;padding:6px 9px;background:#181c27;border-radius:6px;border:1px solid #2a3050;margin-bottom:4px'>
                    <span style='font-size:11px;color:#e8eaf2'>{label}</span>
                    <span style='font-size:12px;font-weight:500;color:{color}'>{count:,}</span></div>"""
                st.markdown(rows_html, unsafe_allow_html=True)

            with col2:
                st.subheader("ECC Customs")
                zh = len(dm[dm["LIEFERSPERRE"] == "ZH"])
                ze = len(dm[dm["LIEFERSPERRE"] == "ZE"])
                z1 = len(dm[dm["LIEFERSPERRE"] == "Z1"])
                st.markdown(f"<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px'>{color_box(zh,'ZH released','#2ecc71')}{color_box(ze,'ZE blocked','#e74c3c')}{color_box(z1,'Z1 partial','#f39c12')}</div>", unsafe_allow_html=True)

            with col3:
                st.subheader("Transport Lock")
                l3 = len(dm[dm["TRANSPORTSPERRGRUND"] == "3.0"])
                l2 = len(dm[dm["TRANSPORTSPERRGRUND"] == "2.0"])
                l_other = total - l3 - l2
                st.markdown(f"<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px'>{color_box(l3,'Released (03)','#2ecc71')}{color_box(l2,'Locked (02)','#e74c3c')}{color_box(l_other,'Freigegeben','#f39c12')}</div>", unsafe_allow_html=True)
                if l2 > 0:
                    st.markdown(f"<div style='background:rgba(0,201,177,.08);border:1px solid rgba(0,201,177,.2);border-radius:6px;padding:7px 10px;font-size:10px;color:#00c9b1;margin-top:8px'>{l2} locked deliveries (02) need action</div>", unsafe_allow_html=True)

            st.subheader("Top Destination Countries")
            countries = dm["LAND_ENDKUNDE"].value_counts().head(8).reset_index()
            countries.columns = ["Country", "Count"]
            bar_colors = ["#9b59d0", "#00c9b1", "#4a90d9", "#f39c12", "#e74c3c", "#2ecc71", "#7b85a8", "#854F0B"]
            fig = go.Figure(go.Bar(x=countries["Count"].tolist(), y=countries["Country"].tolist(), orientation="h",
                                   marker_color=bar_colors[:len(countries)]))
            fig.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(dark_layout(fig, 300), use_container_width=True)

        with subtab_rts:
            ready = len(dm[(dm["LIEFERSPERRE"] == "ZH") & (dm["TRANSPORTSPERRGRUND"] == "3.0") &
                           (dm["TRATY_CODE"] != "ZZZ") & (dm["NZV_FLAG"] == "Nein")])
            not_ready = total - ready
            st.caption('Liefersperre="ZH" AND Transportsperrgrund=3 AND TRATY_Code!="ZZZ" AND NZV_Flag="Nein"')
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

        with subtab_bn:
            nzv_zzz = len(dm[dm["TRATY_CODE"] == "ZZZ"])
            ecc_ze = len(dm[dm["LIEFERSPERRE"] == "ZE"])
            nzv_fl = len(dm[dm["NZV_FLAG"] == "Ja"])
            lock_02 = len(dm[dm["TRANSPORTSPERRGRUND"] == "2.0"])
            ecc_z1 = len(dm[dm["LIEFERSPERRE"] == "Z1"])
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Open Blockers")
                blockers = [("E1 · NzV billing (ZZZ)", nzv_zzz, "#f39c12"), ("E2 · ECC blocked (ZE)", ecc_ze, "#e74c3c"),
                            ("E3 · NZV flag active", nzv_fl, "#f39c12"), ("E4 · Transport locked", lock_02, "#e74c3c"),
                            ("E5 · ECC partial (Z1)", ecc_z1, "#7b85a8")]
                rows_html = ""
                for label, val, color in blockers:
                    rows_html += f"""<div style='display:flex;justify-content:space-between;align-items:center;padding:6px 9px;background:#181c27;border-radius:6px;border:1px solid #2a3050;margin-bottom:4px'>
                    <span style='font-size:11px;color:#e8eaf2'>{label}</span>
                    <span style='font-size:12px;font-weight:500;color:{color}'>{val:,}</span></div>"""
                st.markdown(rows_html, unsafe_allow_html=True)
            with col2:
                st.subheader("Blocker Distribution")
                if sum([nzv_zzz, ecc_ze, nzv_fl, lock_02, ecc_z1]) > 0:
                    fig = px.pie(values=[nzv_zzz, ecc_ze, nzv_fl, lock_02, ecc_z1],
                                 names=["NzV ZZZ", "ECC ZE", "NZV flag", "Lock 02", "Z1"],
                                 color_discrete_sequence=["#f39c12", "#e74c3c", "#854F0B", "#c0392b", "#7b85a8"], hole=0.5)
                    st.plotly_chart(dark_layout(fig, 300), use_container_width=True)

        with subtab_sp:
            st.subheader("NZV Special Cases")
            wth12 = len(dm[dm["AUSWERTUNG"].str.contains("WTH 0012", na=False)])
            wth09 = len(dm[dm["AUSWERTUNG"].str.contains("WTH 0009", na=False)])
            wth10 = len(dm[dm["AUSWERTUNG"].str.contains("WTH 0010", na=False)])
            sonstige = len(dm[dm["AUSWERTUNG"].str.contains("Sonstige", na=False)])
            c1, c2, c3 = st.columns(3)
            c1.markdown(kpi_card("NZV flag", f"{nzv_flag:,}", "#f39c12"), unsafe_allow_html=True)
            c2.markdown(kpi_card("NzV transport", f"{nzv_traty:,}", "#f39c12"), unsafe_allow_html=True)
            c3.markdown(kpi_card("WTH 0012", f"{wth12:,}", "#f39c12"), unsafe_allow_html=True)
            c4, c5, c6 = st.columns(3)
            c4.markdown(kpi_card("AWV SAP EU", f"{wth09:,}", "#00c9b1"), unsafe_allow_html=True)
            c5.markdown(kpi_card("AWV ohne KanLog", f"{wth10:,}", "#00c9b1"), unsafe_allow_html=True)
            c6.markdown(kpi_card("Sonstige", f"{sonstige:,}", "#7b85a8"), unsafe_allow_html=True)

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
            kl_invoices = kl["RECHNR"].nunique()
            kl_months = kl["MONTH"].nunique()
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.markdown(kpi_card("Total shipments", f"{kl_total:,}"), unsafe_allow_html=True)
            c2.markdown(kpi_card("Bukarest", f"{kl_bukarest:,}", "#9b59d0", safe_pct(kl_bukarest, kl_total)), unsafe_allow_html=True)
            c3.markdown(kpi_card("Berlin", f"{kl_berlin:,}", "#00c9b1", safe_pct(kl_berlin, kl_total)), unsafe_allow_html=True)
            c4.markdown(kpi_card("Avg / month", f"{kl_total // max(1, kl_months):,}"), unsafe_allow_html=True)
            c5.markdown(kpi_card("Invoices", f"{kl_invoices:,}"), unsafe_allow_html=True)
            c6.markdown(kpi_card("Ships / invoice", f"{kl_total/max(1,kl_invoices):.1f}", "#2ecc71"), unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Monthly Shipments by Team")
                monthly_team = kl.groupby(["MONTH", "TEAM"]).size().reset_index(name="Count")
                month_labels = {"2025-07": "Jul 2025", "2025-08": "Aug 2025", "2025-09": "Sep 2025"}
                monthly_team["Label"] = monthly_team["MONTH"].map(month_labels).fillna(monthly_team["MONTH"])
                fig = px.bar(monthly_team, x="Label", y="Count", color="TEAM",
                             color_discrete_map={"Bukarest": "#9b59d0", "Berlin": "#00c9b1"}, barmode="stack",
                             category_orders={"Label": ["Jul 2025", "Aug 2025", "Sep 2025"]})
                fig.update_layout(legend_title="", xaxis_type="category")
                st.plotly_chart(dark_layout(fig, 250), use_container_width=True)
            with col2:
                st.subheader("Business Area Split")
                areas = kl["GESCHAEFTSGEBIET_KZ"].value_counts().reset_index()
                areas.columns = ["Area", "Count"]
                fig = px.pie(areas, values="Count", names="Area",
                             color_discrete_sequence=["#9b59d0", "#00c9b1", "#4a90d9", "#f39c12", "#7b85a8"], hole=0.55)
                st.plotly_chart(dark_layout(fig, 250), use_container_width=True)

        with subtab_geo:
            countries_kl = kl["LANDNAME_ENDVERW"].value_counts()
            n_countries = len(countries_kl[countries_kl.index != ""])
            transit_de = len(kl[kl["LANDNAME_FM"] == "Deutschland"])
            domestic = len(kl[kl["LANDNAME_ENDVERW"] == "Deutschland"])
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(kpi_card("Dest. countries", f"{n_countries}"), unsafe_allow_html=True)
            c2.markdown(kpi_card("Transit via DE", f"{transit_de:,}", "#2ecc71"), unsafe_allow_html=True)
            c3.markdown(kpi_card("Domestic DE", f"{domestic:,}", "#00c9b1"), unsafe_allow_html=True)
            c4.markdown(kpi_card("International", f"{kl_total - domestic:,}"), unsafe_allow_html=True)

            st.subheader("Top 10 Destination Countries")
            top_countries = countries_kl[countries_kl.index != ""].head(10).reset_index()
            top_countries.columns = ["Country", "Count"]
            fig = go.Figure(go.Bar(x=top_countries["Count"].tolist(), y=top_countries["Country"].tolist(),
                                   orientation="h", marker_color="#9b59d0"))
            fig.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(dark_layout(fig, 350), use_container_width=True)

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
            c1.markdown(kpi_card("Active projects", f"{len(projects_valid)}"), unsafe_allow_html=True)
            c2.markdown(kpi_card("Top project", f"{top_proj.iloc[0]['Shipments']}" if len(top_proj) > 0 else "0", "#00c9b1",
                                 top_proj.iloc[0]["Project"] if len(top_proj) > 0 else ""), unsafe_allow_html=True)
            c3.markdown(kpi_card("Top 5 share", safe_pct(top_proj.head(5)["Shipments"].sum(), kl_total)), unsafe_allow_html=True)

            st.subheader("Top 12 Projects")
            st.dataframe(top_proj, use_container_width=True, hide_index=True)

        with subtab_ops:
            tv_nrs = kl["TV_NR"].nunique()
            packs = kl["PACKNR"].nunique()
            invoices = kl["RECHNR"].nunique()
            kollonrs = kl["KOLLONR_LIEFERANT"].nunique()
            orgs = kl[kl["ORG_ID_ABSENDER"] != ""]["ORG_ID_ABSENDER"].nunique()
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.markdown(kpi_card("Transport orders", f"{tv_nrs:,}"), unsafe_allow_html=True)
            c2.markdown(kpi_card("Pack orders", f"{packs:,}"), unsafe_allow_html=True)
            c3.markdown(kpi_card("Invoices", f"{invoices:,}"), unsafe_allow_html=True)
            c4.markdown(kpi_card("Ships / invoice", f"{kl_total/max(1,invoices):.1f}", "#2ecc71"), unsafe_allow_html=True)
            c5.markdown(kpi_card("Unique suppliers", f"{kollonrs:,}"), unsafe_allow_html=True)
            c6.markdown(kpi_card("ORG senders", f"{orgs}", "#00c9b1"), unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Sender Organisations")
                org_counts = kl["ORG_ID_ABSENDER"].value_counts().head(5)
                rows_html = ""
                for org_id, cnt in org_counts.items():
                    label = org_id if org_id else "NULL records"
                    color = "#e74c3c" if not org_id else "#2ecc71"
                    rows_html += f"""<div style='display:flex;justify-content:space-between;align-items:center;padding:6px 9px;background:#181c27;border-radius:6px;border:1px solid #2a3050;margin-bottom:4px'>
                    <span style='font-size:11px;color:#e8eaf2'>{label}</span>
                    <span style='font-size:12px;font-weight:500;color:{color}'>{cnt:,} ({safe_pct(cnt, kl_total)})</span></div>"""
                st.markdown(rows_html, unsafe_allow_html=True)
            with col2:
                st.subheader("Freight Forwarder Hubs")
                ff_ops = kl[kl["STADT_WARBE_VB"] != ""]["STADT_WARBE_VB"].value_counts().head(5).reset_index()
                ff_ops.columns = ["City", "Count"]
                fig = px.bar(ff_ops, x="City", y="Count", color_discrete_sequence=["#00c9b1"])
                st.plotly_chart(dark_layout(fig, 250), use_container_width=True)
