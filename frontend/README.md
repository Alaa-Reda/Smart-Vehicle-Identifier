# Vehicle Vision AI — Frontend

Streamlit + custom CSS frontend for the Smart Vehicle Identifier project.

## Structure

```
frontend/
├── app.py                   Home page (Streamlit entry point)
├── pages/                    One file per page, native Streamlit multipage
│   ├── 1_Detect.py               Image upload
│   ├── 2_Loading.py              Step-by-step processing animation + API call
│   ├── 3_Result.py               Detection result
│   ├── 4_Chat.py                 AI assistant / chat
│   ├── 5_Features.py             Feature grid
│   ├── 6_Developers.py           Team page
│   ├── 7_Developer_Profile.py    Single developer detail page
│   ├── 8_Team_Photo.py           Team photo page
│   ├── 9_About.py                About the project
│   ├── 10_History.py             Past detections
│   └── 11_PDF_Report.py          PDF report preview / download
├── components/                 Reusable UI pieces (navbar, cards, upload zone)
├── api/                          HTTP client + endpoint wrappers — see integration/README.md
├── utils/                        Theme, i18n, session-state helpers
├── assets/css/theme.css           All design tokens + component styles
└── integration/                   Notes + .env.example for connecting to the FastAPI backend
```

This intentionally merges the old `app_pages/` + `pages/` split into one
`pages/` folder (Streamlit's native multipage convention), and drops the
`models/`, `services/`, `config/` layers in favor of the simpler
`api/` + `utils/` split — fewer places to look for the same logic.

## Running

```
pip install -r requirements.txt
streamlit run app.py
```

Set `API_BASE_URL` before running to point at your FastAPI backend (see
`integration/README.md`). Without it, pages fall back to demo data so the
UI can be reviewed without a backend running.

## Design

Colors, spacing and component styles all live in `assets/css/theme.css`
as CSS variables, with a `[data-theme="dark"]` block for dark mode. Do not
hardcode colors in page files — use the existing `vv-*` classes or add a
new variable to `theme.css`.
