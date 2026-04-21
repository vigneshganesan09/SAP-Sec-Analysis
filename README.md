# 🔒 SAP Security Analyzer

> **SAP Security Gap Analysis Tool** — Audit dormant users, SoD conflicts, critical authorizations, security parameters, RFC security, and 13 other controls. Generates a PDF report with one click.

[![Live App](https://img.shields.io/badge/Live%20App-GitHub%20Pages-blue?style=for-the-badge&logo=github)](https://YOUR-USERNAME.github.io/sap-security-analyzer/sap-security-analyzer.html)
[![Benchmark](https://img.shields.io/badge/Benchmark-SAP%20Security%20Baseline%20v1.8-orange?style=for-the-badge)](https://support.sap.com)

---

## Features

- **13 Security Controls** — Dormant users, SoD conflicts, debug access, RFC security, client settings, firefighter access, and more
- **Controls Configuration** — Enable/disable controls, edit thresholds, add custom controls with condition builder
- **Connection Manager** — Proxy / Direct / Demo modes with OData support
- **PDF Report** — Cover page, executive summary, per-control findings tables, remediation priorities
- **CORS Proxy** — Python + Node.js proxy servers included
- **Zero Build Tools** — Single HTML file, open in any browser

---

## Quick Start

### Open directly (Demo mode — no SAP needed)
Download `sap-security-analyzer.html` and open it in Chrome/Edge/Firefox.
Set connection mode to **Demo** to explore with sample data.

### Connect to real SAP

**Step 1 — Start the proxy** (needed because browsers block direct SAP calls):

```bash
# Python (recommended — usually pre-installed)
python  sap_proxy.py    # Windows
python3 sap_proxy.py    # Mac / Linux

# OR Node.js
node sap-proxy-server.js
```

You should see:
```
SAP OData CORS Proxy (Python) on http://localhost:3100
Set Proxy URL in app -> http://localhost:3100
```

**Step 2 — Configure connection in the app:**
- Mode: **Proxy**
- Proxy URL: `http://localhost:3100`
- Server/IP, Port, SID, Client, User, Password

**Step 3 — Run Analysis → Export PDF**

---

## Project Files

```
sap-security-analyzer/
├── sap-security-analyzer.html   # Main app (~140KB, single file)
├── sap_proxy.py                 # Python CORS proxy (no dependencies)
├── sap-proxy-server.js          # Node.js CORS proxy (no dependencies)
└── README.md
```

---

## Security Controls

| # | Control | SAP Table | SAP Note |
|---|---|---|---|
| 1 | Dormant Users (>90 days) | USR02 | 2034492 |
| 2 | Password Age Violations | USR02 | 863610 |
| 3 | Security Profile Parameters | PAHI/RZ11 | 2034492 |
| 4 | Critical Authorizations (SAP_ALL) | AGR_USERS | 1484597 |
| 5 | Default & Standard Users | USR02 | 2216306 |
| 6 | SoD Conflicts | AGR_1251 | 1490023 |
| 7 | Debug Access in Production | AGR_USERS | 1554667 |
| 8 | Sensitive Table Access | S_TABU_DIS | 1539539 |
| 9 | RFC Destination Security | RFCDES | 1682316 |
| 10 | Client Security Settings (SCC4) | T000 | 861377 |
| 11 | Failed Login Attempts | USR02/SM21 | 2015449 |
| 12 | Firefighter / Emergency Access | AGR_USERS | 2476344 |
| 13 | License Assignment Review | USR41_MLD | — |

Custom controls can be added via the Controls Configuration page.

---

## SAP OData Service

The app calls a custom OData service `ZTEST_TABLE_SRV` on your SAP system:

```
http://<host>:<port>/sap/opu/odata/sap/ZTEST_TABLE_SRV/<EntitySet>?$format=json
```

Create entity sets in SAP for each control (DormantUsersSet, CriticalAuthSet, etc.) returning standard OData JSON format.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | React 18 via CDN — no build step |
| JSX | Babel Standalone (in-browser compilation) |
| PDF | jsPDF 2.5.1 + jsPDF-AutoTable |
| Proxy | Python `http.server` or Node.js `http` — zero npm dependencies |

---

## Privacy

The proxy runs locally on your machine. SAP credentials never leave your network. No telemetry or external data collection.

---

## License

MIT
