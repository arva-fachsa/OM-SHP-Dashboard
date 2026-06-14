# PRD — Product Requirements Document
## Shipping Operations Dashboard

| Feld | Wert |
|------|------|
| **Produkt** | Shipping Operations Dashboard |
| **Abteilung** | SE GS C LOT OM SHP |
| **Standort** | Gasturbinen Berlin |
| **Owner** | Arva Fachsa |
| **Version** | 1.0 |
| **Datum** | Juni 2025 |
| **Status** | Live |

---

## 1. Zusammenfassung

Ein interaktives Web-Dashboard zur Echtzeit-Überwachung aller Versandoperationen (Delivery Monitor + KanLog) der Abteilung SE GS C LOT OM SHP. Das Dashboard bietet dem Management und dem Operations-Team eine zentrale Sicht auf Liefervolumen, Transportmodi, Zollstatus, Engpässe und Sonderfälle.

---

## 2. Problemstellung

| Problem | Auswirkung |
|---------|-----------|
| Daten verstreut in SAP, Excel-Reports und Alteryx-Workflows | Keine Gesamtsicht, zeitaufwändige manuelle Zusammenführung |
| Chef/Management hat keinen Snowflake-Zugang | Kein Echtzeit-Zugriff auf aktuelle Versanddaten |
| Monatliche Excel-Reports sind statisch | Keine Drill-Down-Möglichkeit, keine Filterung |
| Engpässe (NzV, ECC-Sperren) werden spät erkannt | Verzögerungen in der Lieferkette |

---

## 3. Zielgruppen

| Persona | Bedarf |
|---------|--------|
| **Abteilungsleiter** | Schnelle KPI-Übersicht, Ready-to-Ship-Status, monatliche Trends |
| **Operations Team (Bukarest/Berlin)** | Detaillierte Blocker-Analyse, Spezialfälle, Projektübersicht |
| **Logistik-Koordination** | Transport-Modi, Speditions-Hubs, Länderverteilung |

---

## 4. Funktionale Anforderungen

### 4.1 Delivery Monitor

| ID | Feature | Priorität |
|----|---------|-----------|
| DM-01 | KPI-Karten: Total, AWV, EU/NONEU, NZV flag, NzV transport | Must |
| DM-02 | Team Assignment Donut-Chart (Bukarest/Berlin/LWF) | Must |
| DM-03 | Monthly Volume Bar-Chart (Jul–Sep 2025) | Must |
| DM-04 | Auswertung Categories Top 6 | Should |
| DM-05 | Status Signals: Transport Mode, ECC Customs, Transport Lock | Must |
| DM-06 | Ready to Ship Berechnung (Formel-basiert) | Must |
| DM-07 | Schedule by Month (Quartalsaufteilung) | Should |
| DM-08 | Bottlenecks: 5 Blocker-Kategorien + Donut | Must |
| DM-09 | Special Cases NZV: 6 KPI-Karten mit Quellangabe | Should |
| DM-10 | Top Destination Countries (farbige Balken) | Should |

### 4.2 KanLog

| ID | Feature | Priorität |
|----|---------|-----------|
| KL-01 | Volume Overview: 6 KPI-Karten mit Sub-Text | Must |
| KL-02 | Monthly Shipments by Team (Stacked Bar) | Must |
| KL-03 | Business Area Split (Donut: W/O/P3/G/SLS) | Must |
| KL-04 | Geography: Top 10 Destination Countries (farbig) | Should |
| KL-05 | Projects: Top 12 + Business Area Volume Karten | Should |
| KL-06 | Operations: Transport orders, Invoices, Sender Orgs | Should |
| KL-07 | Freight Forwarder Hubs (Stadt_Warbe_VB) | Should |

### 4.3 Übergreifend

| ID | Feature | Priorität |
|----|---------|-----------|
| UX-01 | Dark-Theme (Siemens Energy Branding) | Must |
| UX-02 | Sidebar-Filter: Period, Team, Category, Plant | Must |
| UX-03 | Refresh-Button für Daten-Aktualisierung | Must |
| UX-04 | Live-Badge oben rechts | Nice |
| UX-05 | Professionelle Plotly-Tooltips (Hover-Info) | Must |
| UX-06 | Italic Sub-Text bei jeder KPI-Karte (Datenquelle) | Must |
| UX-07 | Chart-Titel + Subtitle innerhalb der Chart-Card | Must |
| UX-08 | Öffentliche URL ohne Login (Chef-tauglich) | Must |

---

## 5. Nicht-funktionale Anforderungen

| Anforderung | Zielwert |
|-------------|----------|
| Verfügbarkeit | 99% (Streamlit Community Cloud) |
| Ladezeit | < 3 Sekunden |
| Responsiveness | Desktop-optimiert (1920x1080) |
| Deployment | Auto-Deploy bei Git Push (~60 Sekunden) |
| Datenschutz | Keine personenbezogenen Daten im Dashboard |
| Aktualisierung | Bei jedem Alteryx-Lauf via `auto_push.bat` |

---

## 6. Datenquellen

| Quelle | Tabelle/File | Records | Felder |
|--------|-------------|---------|--------|
| Alteryx → CSV | `data/dm_data.csv` | ~3.326 | MONTH, TEAM, CATEGORY, PLANT, EU_NONEU, LAND_ENDKUNDE, TRATY_CODE, LIEFERSPERRE, TRANSPORTSPERRGRUND, NZV_FLAG, AUSWERTUNG |
| Alteryx → CSV | `data/kl_data.csv` | ~855 | MONTH, TEAM, PROJKENNW, GESCHAEFTSGEBIET_KZ, ORG_ID_ABSENDER, VERSANDZUST_DEU, STADT_WARBE_VB, LANDNAME_FM, LANDNAME_ENDVERW, TV_NR, PACKNR, RECHNR, KOLLONR_LIEFERANT |
| Snowflake (Backup) | DELIVERY_MONITOR | 3.326 | Gleiche Felder |
| Snowflake (Backup) | KANLOG_SHIPMENTS | 855 | Gleiche Felder |

---

## 7. Erfolgskriterien

| Metrik | Ziel |
|--------|------|
| Management nutzt Dashboard wöchentlich | Ja |
| Ready-to-Ship-Quote sichtbar | > 0% (aktuell dynamisch berechnet) |
| Blocker werden innerhalb 24h erkannt | Ja (via Dashboard) |
| Kein manueller Excel-Report mehr nötig | Mittelfristig |

---

## 8. Abgrenzung (Out of Scope v1.0)

- Keine Benutzer-Authentifizierung (öffentlich)
- Keine Schreiboperationen (nur lesend)
- Kein Alerting/Notification (zukünftig via Snowflake Alerts)
- Keine historischen Trends > 3 Monate (wird mit rollendem Fenster erweitert)
- Keine Integration FastEntry, ILoB, TM4all, S4Unify (Phase 2)

---

## 9. Roadmap

| Phase | Inhalt | Status |
|-------|--------|--------|
| Phase 1 | DM + KanLog Dashboard live | Done |
| Phase 2 | Rolling 12 months, FastEntry Integration | Geplant |
| Phase 3 | Snowflake Alerts, automatische Anomalie-Erkennung | Konzept |
| Phase 4 | Multi-Team Comparison, YoY Vergleich | Idee |
