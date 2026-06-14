# TSD — Technical Specification Document
## Shipping Operations Dashboard

| Feld | Wert |
|------|------|
| **System** | Streamlit Community Cloud Web App |
| **Repository** | github.com/arva-fachsa/OM-SHP-Dashboard |
| **URL** | https://om-shp-dashboard.streamlit.app/ |
| **Stack** | Python 3.x, Streamlit, Plotly, Pandas |
| **Autor** | Arva Fachsa |
| **Version** | 1.0 |
| **Datum** | Juni 2025 |

---

## 1. Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────┐
│                   DATENFLUSS                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  SAP/BW ──► Alteryx Workflow ──► CSV-Export              │
│                                      │                   │
│                                      ▼                   │
│                            Local Git Repo                │
│                         (streamlit_cloud_app/)           │
│                                      │                   │
│                              auto_push.bat               │
│                                      │                   │
│                                      ▼                   │
│                        GitHub Repository                 │
│                  (arva-fachsa/OM-SHP-Dashboard)          │
│                                      │                   │
│                              Auto-Deploy                 │
│                                      │                   │
│                                      ▼                   │
│                     Streamlit Community Cloud            │
│                (om-shp-dashboard.streamlit.app)          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Verzeichnisstruktur

```
streamlit_cloud_app/
├── streamlit_app.py          # Haupt-Applikation (Single-File)
├── requirements.txt          # Python Dependencies
├── auto_push.bat             # Auto-Commit + Push Script
├── .streamlit/
│   └── config.toml           # Theme-Konfiguration (Dark)
├── data/
│   ├── dm_data.csv           # Delivery Monitor Daten
│   └── kl_data.csv           # KanLog Daten
└── docs/
    ├── PRD.md                # Product Requirements
    ├── TSD.md                # Technical Specification (dieses Dokument)
    └── PLAN.md               # Projekt-Plan
```

---

## 3. Technischer Stack

| Komponente | Version | Zweck |
|-----------|---------|-------|
| Python | 3.11+ | Runtime |
| Streamlit | >= 1.28 | Web-Framework |
| Pandas | latest | Daten-Manipulation |
| Plotly | latest | Interaktive Charts |
| Git | 2.x | Versionskontrolle |
| Streamlit Community Cloud | - | Hosting (kostenlos) |

---

## 4. Datenmodell

### 4.1 Delivery Monitor (`dm_data.csv`)

| Spalte | Typ | Beschreibung | Beispielwerte |
|--------|-----|-------------|---------------|
| MONTH | string | Berichtsmonat | "2025-07", "2025-08", "2025-09" |
| TEAM | string | Bearbeitungsteam | "Bukarest", "Berlin", "LWF" |
| CATEGORY | string | Lieferkategorie | "AWV", "NZV", "Sonstige" |
| PLANT | string | Werk | "1201", "1203", "12S1" |
| EU_NONEU | string | Zielregion | "EU", "NONEU" |
| LAND_ENDKUNDE | string | Endkunde-Land | "Saudi-Arabien", "Deutschland" |
| TRATY_CODE | string | Transportart-Code | "T", "C", "ZZZ", "A", "S", "LT" |
| LIEFERSPERRE | string | ECC Liefersperre | "ZH", "ZE", "Z1" |
| TRANSPORTSPERRGRUND | float | Transport-Sperrgrund | 3.0, 2.0, 1.0, NaN |
| NZV_FLAG | string | NzV-Kennzeichen | "Ja", "Nein" |
| AUSWERTUNG | string | Auswertungskategorie | "WTH 0009 - AWV...", "Sonstige..." |

**Wichtig:** `TRANSPORTSPERRGRUND` wird als `float64` geladen (nicht String). Vergleiche müssen mit `== 3.0` erfolgen, nicht `== "3.0"`.

### 4.2 KanLog (`kl_data.csv`)

| Spalte | Typ | Beschreibung | Beispielwerte |
|--------|-----|-------------|---------------|
| MONTH | string | Berichtsmonat | "2025-07", "2025-08", "2025-09" |
| TEAM | string | Bearbeitungsteam | "Bukarest", "Berlin" |
| PROJKENNW | string | Projektkennwort | Projekt-IDs |
| GESCHAEFTSGEBIET_KZ | string | Geschäftsgebiet | "W", "O", "P3", "G", "SLS" |
| ORG_ID_ABSENDER | string | Organisation Absender | Org-IDs |
| VERSANDZUST_DEU | string | Versandzuständigkeit | - |
| STADT_WARBE_VB | string | Stadt Warenbegleit-VB | "Berlin", "Hamburg" |
| LANDNAME_FM | string | Land Frachtmanagement | "Deutschland" |
| LANDNAME_ENDVERW | string | Land Endverwendung | "Saudi-Arabien", "Deutschland" |
| TV_NR | string | Transportvorgang-Nr. | - |
| PACKNR | string | Packnummer | - |
| RECHNR | string | Rechnungsnummer | - |
| KOLLONR_LIEFERANT | string | Kollo-Nr. Lieferant | - |

---

## 5. Kernlogik

### 5.1 Ready-to-Ship Formel

```python
ready = len(dm[
    (dm["LIEFERSPERRE"] == "ZH") &           # ECC freigegeben
    (dm["TRANSPORTSPERRGRUND"] == 3.0) &      # Transport freigegeben (FLOAT!)
    (dm["TRATY_CODE"] != "ZZZ") &             # Kein NzV-Transport
    (dm["NZV_FLAG"] == "Nein")                # Kein NzV-Flag
])
```

### 5.2 Helper-Funktionen

```python
def kpi_card(label, value, color=None, sub="")
    # Erzeugt HTML-KPI-Karte mit:
    # - Label (grau, 10px)
    # - Value (farbig, 22px, bold)
    # - Sub-Text (italic, 9px, Datenquelle)

def dark_layout(fig, height=250, title="", subtitle="")
    # Setzt Plotly-Layout:
    # - paper_bgcolor = Card-Hintergrund
    # - Professionelle Hover-Tooltips
    # - Titel + Subtitle im Chart
    # - Gridlines subtil

def color_box(value, label, color)
    # Farbige Status-Box für ECC/Transport-Lock
```

### 5.3 Theme-Konstanten

```python
THEME_TEXT = "#e8eaf2"                    # Haupt-Textfarbe
THEME_BG_CARD = "rgba(26,31,48,.85)"      # Card-Hintergrund
THEME_CHART_FONT = "#e8eaf2"              # Chart-Schriftfarbe
```

### 5.4 Farb-Palette

| Farbe | Hex | Verwendung |
|-------|-----|-----------|
| Lila | #9b59d0 | Bukarest, primäre Charts |
| Teal | #00c9b1 | Berlin, positive Werte |
| Blau | #4a90d9 | P3, sekundäre Daten |
| Orange | #f39c12 | Warnings, NZV |
| Rot | #e74c3c | Blocker, Fehler |
| Grün | #2ecc71 | Freigegeben, Ready |
| Grau | #7b85a8 | Neutral, Sub-Text |

---

## 6. Deployment

### 6.1 Erstmalige Einrichtung

1. GitHub-Repo erstellen (public)
2. Streamlit Community Cloud verbinden
3. App-URL konfigurieren → `om-shp-dashboard.streamlit.app`
4. Branch: `main`, File: `streamlit_app.py`

### 6.2 Update-Workflow

```bash
# Manuell:
cd c:\Data Warehouse FY26\streamlit_cloud_app
git add -A
git commit -m "update: neue Daten [Datum]"
git push origin main
# → Auto-Redeploy in ~60 Sekunden

# Automatisch (nach Alteryx):
auto_push.bat
```

### 6.3 `auto_push.bat`

```batch
@echo off
cd /d "c:\Data Warehouse FY26\streamlit_cloud_app"
git add data/
git diff --cached --quiet && echo Keine Aenderungen. && exit /b
for /f "tokens=*" %%i in ('date /t') do set TODAY=%%i
git commit -m "data update %TODAY%"
git push origin main
echo Push erfolgreich - Dashboard aktualisiert sich in ~60s
```

---

## 7. Konfiguration

### 7.1 `.streamlit/config.toml`

```toml
[theme]
base = "dark"
primaryColor = "#00c9b1"
backgroundColor = "#0f1117"
secondaryBackgroundColor = "#1a1f30"
textColor = "#e8eaf2"
font = "sans serif"
```

### 7.2 `requirements.txt`

```
streamlit>=1.28
pandas
plotly
```

---

## 8. Bekannte Einschränkungen

| Problem | Workaround | Langfristige Lösung |
|---------|-----------|-------------------|
| `TRANSPORTSPERRGRUND` ist float | Vergleich mit `== 3.0` | CSV mit expliziten Typen |
| Streamlit Cloud Free Tier | App geht nach Inaktivität schlafen | Paid Tier oder SiS |
| Keine Auth | URL ist öffentlich | Private URL oder Snowflake Native App |
| Max 3 Monate Daten | Aktueller CSV-Inhalt | Rolling 12 months |

---

## 9. Snowflake-Backup

Falls Streamlit Cloud ausfällt, existiert eine SiS-Version:

| Parameter | Wert |
|-----------|------|
| Account | SIEMENSENERGY-LB88417 |
| Database | SNOWFLAKE_LEARNING_DB |
| Schema | GS_FIN_NA_FT |
| Stage | @STREAMLIT_STAGE |
| App | SHIPPING_OPERATIONS_DASHBOARD |
| Warehouse | WH_PRD_HTT_FIN_REPORT_XS |
| Role | RL_PRD_HTT_FIN_REPORT |

---

## 10. CSS-Injection (Custom Styling)

```css
[data-testid="stPlotlyChart"] {
    border: 1px solid rgba(42,48,80,.5);
    border-radius: 8px;
    padding: 4px;
    margin-top: 8px;
    margin-bottom: 12px;
}
```

Sorgt für konsistente Card-Borders bei allen Plotly-Charts.
