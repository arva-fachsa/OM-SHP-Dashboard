# PLAN — Projektplan & Umsetzungsdokumentation
## Shipping Operations Dashboard

| Feld | Wert |
|------|------|
| **Projekt** | OM SHP Dashboard Deployment |
| **Zeitraum** | Mai – Juni 2025 |
| **Owner** | Arva Fachsa |
| **Tools** | Cortex Code, Streamlit, GitHub, Alteryx |

---

## 1. Projektgenese

### Ausgangslage
- Monatliche manuelle Excel-Reports für Management
- Daten in SAP BW über Alteryx extrahiert
- Chef hat keinen Snowflake-Zugang
- Kein interaktives Dashboard verfügbar

### Zielsetzung
- Öffentlich erreichbares Dashboard ohne Login
- Automatische Aktualisierung bei neuen Daten
- Professionelles Design (Siemens Energy Branding)
- Alle relevanten KPIs auf einen Blick

---

## 2. Evaluierte Optionen

| Option | Vorteile | Nachteile | Entscheidung |
|--------|---------|-----------|-------------|
| Streamlit in Snowflake (SiS) | Nativ integriert, Sicherheit | Erfordert Snowflake-Login | Backup-Lösung |
| Snowflake Native App (Next.js) | Volle UI-Kontrolle | EAI-Blocker, komplexes Setup | Abgelehnt |
| **Streamlit Community Cloud** | **Kostenlos, öffentliche URL, Auto-Deploy** | **Repo muss public sein** | **Gewählt** |
| Power BI | Bekannt im Unternehmen | Lizenzkosten, nicht direkt teilbar | Abgelehnt |

---

## 3. Umsetzungs-Chronologie

### Phase 1: Snowflake-Grundlagen (Mai 2025)
- Snowflake-Tabellen DELIVERY_MONITOR + KANLOG_SHIPMENTS erstellt
- Erste SiS-Version deployed (nur intern nutzbar)
- Problem erkannt: Chef kann nicht auf Snowflake zugreifen

### Phase 2: Streamlit Community Cloud (Juni 2025)

#### Schritt 1: Repository-Setup
- GitHub-Repo `arva-fachsa/OM-SHP-Dashboard` erstellt
- Repo public gesetzt (Voraussetzung für Streamlit Cloud)
- Daten als CSV exportiert (`dm_data.csv`, `kl_data.csv`)

#### Schritt 2: App-Entwicklung
- `streamlit_app.py` als Single-File-App geschrieben
- Dark Theme mit Siemens Energy Branding
- Alle DM + KanLog Tabs implementiert
- Sidebar: Filter + Logo + Refresh-Button

#### Schritt 3: Deployment
- Streamlit Community Cloud Account verbunden
- App deployed unter `om-shp-dashboard.streamlit.app`
- Erste Fehler behoben:
  - Repo war private → public gestellt
  - URL-Paste-Modus für Deploy genutzt

#### Schritt 4: UI-Polish (Mehrere Iterationen)
1. Siemens Energy Logo (Text-Version: SIEMENS teal + energy lila)
2. Light/Dark Toggle → verworfen (Dark-only)
3. Logo zentriert in Sidebar
4. Plotly Hover-Tooltips professionell formatiert
5. KPI-Karten mit italic Sub-Text (Datenquelle)
6. Section-Headers: "B1 · Transport Mode", "D · READY TO SHIP" etc.
7. Charts: Titel + Subtitle innerhalb der Card
8. Ready-to-Ship Float-Bug gefixt (`== 3.0` statt `== "3.0"`)
9. Abstände/Margins professionell angepasst
10. Business Area Split als Donut + Volume-Karten

#### Schritt 5: Automatisierung
- `auto_push.bat` erstellt für Alteryx-Integration
- Workflow: Alteryx → CSV → auto_push.bat → GitHub → Auto-Deploy

---

## 4. Bugs & Fixes

| Bug | Ursache | Fix |
|-----|---------|-----|
| "Ready to Ship" zeigt immer 0 | `TRANSPORTSPERRGRUND` ist float64, Vergleich mit String "3.0" | Geändert zu `== 3.0` |
| Git Push rejected | Remote hatte Codespace-Commits | `git pull --rebase origin main` |
| "Repository does not exist" auf Streamlit Cloud | Repo war private | Auf public umgestellt |
| Texte unsichtbar im Light Mode | Hardcoded weiße Farbe | Light Mode entfernt, Dark-only |
| 121 staged files im Hauptordner | Versehentlicher `git init` in `c:\Data Warehouse FY26\` | `.git` Ordner dort gelöscht |

---

## 5. Aktueller Stand (Juni 2025)

### Live-Features
- 5 DM Sub-Tabs: Overview, Status Signals, Ready to Ship, Bottlenecks, Special Cases
- 4 KL Sub-Tabs: Volume, Geography, Projects, Operations
- Alle KPI-Karten mit Quellenangabe
- Alle Charts mit Titel/Subtitle in Card
- Professionelle Tooltips bei Hover
- Sidebar-Filter (Period, Team, Category, Plant)
- Refresh-Button
- Auto-Deploy Pipeline

### Offene Punkte (Phase 2)
- Rolling 12 months Zeitfenster
- FastEntry, ILoB, TM4all Integration
- Snowflake Alerts bei Anomalien
- Custom Domain (optional)

---

## 6. Wartung & Betrieb

### Routine-Update (nach Alteryx-Lauf)
```
1. Alteryx exportiert neue CSVs nach streamlit_cloud_app/data/
2. auto_push.bat ausführen (oder manuell git push)
3. Dashboard aktualisiert sich in ~60 Sekunden
4. Stichprobenartig prüfen auf om-shp-dashboard.streamlit.app
```

### Troubleshooting

| Symptom | Lösung |
|---------|--------|
| App zeigt alte Daten | Refresh-Button klicken oder Seite neu laden |
| App ist offline/sleeping | Seite aufrufen, wartet 30s und startet neu |
| Push schlägt fehl | `git pull --rebase origin main` dann nochmal pushen |
| Chart zeigt 0 Werte | Datentyp-Mismatch prüfen (float vs string) |

---

## 7. Lessons Learned

1. **Datentypen immer prüfen** — Pandas liest numerische CSV-Spalten als float, nicht als String
2. **Public Repo nötig** für Streamlit Community Cloud (kostenlos)
3. **Dark Mode only** ist besser als ein schlechter Light Mode
4. **Plotly `hovertemplate`** statt Standard-Tooltips für professionelles Erscheinungsbild
5. **Git-Repo separat halten** — nicht im Hauptprojektordner initialisieren
6. **Iteratives UI-Design** — Schritt für Schritt verbessern, nicht alles auf einmal
7. **Auto-Push Script** spart langfristig enorm viel Zeit

---

## 8. Kontakt & Ressourcen

| Ressource | Link/Pfad |
|-----------|----------|
| Live Dashboard | https://om-shp-dashboard.streamlit.app/ |
| GitHub Repo | https://github.com/arva-fachsa/OM-SHP-Dashboard |
| Lokaler Code | `c:\Data Warehouse FY26\streamlit_cloud_app\` |
| Snowflake SiS Backup | SNOWFLAKE_LEARNING_DB.GS_FIN_NA_FT |
| Alteryx Workflows | [Interner Pfad] |
| Cortex Code (IDE) | Für zukünftige Änderungen |
