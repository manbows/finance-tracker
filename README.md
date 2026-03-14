# Finance Tracker

A personal finance tracker built with Python and Flask. Log income and expenses, set a monthly budget, and visualise your spending over time.

![Python](https://img.shields.io/badge/python-3.11-blueviolet) ![Flask](https://img.shields.io/badge/flask-3.0-lightgrey) ![Deployed on Railway](https://img.shields.io/badge/deployed-railway-purple)

---

## preview

![Dashboard](static/images/dashboard.png)
![Add Transaction](static/images/additem.png)
![Budget](static/images/budget.png)
![History](static/images/history.png)

---

## features

- Add and categorise income and expense transactions
- Dashboard with monthly activity chart (Chart.js)
- Budget tracker with progress bar and alerts at 90% and over-limit
- Spending breakdown by category
- Full transaction history with delete
- Flash notifications for budget warnings

## tech stack

| Layer | Tech |
|---|---|
| Backend | Python, Flask |
| Templating | Jinja2 |
| Frontend | Vanilla JS, Chart.js |
| Data | JSON flat files (local) |
| Deployment | Railway |

## run locally

**1. Clone the repo**
```bash
git clone https://github.com/manbows/finance-tracker.git
cd finance-tracker
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set environment variable**
```bash
export SECRET_KEY=your-secret-key-here   # Mac/Linux
set SECRET_KEY=your-secret-key-here      # Windows
```

**5. Run**
```bash
python app.py
```

Visit `http://localhost:5000`

## deploy to Railway

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
3. Select this repo
4. Add environment variable: `SECRET_KEY` = any long random string
5. Railway detects the `Procfile` automatically

> Data is stored in JSON files which do not persist between Railway redeploys. For a persistent production setup, swap the JSON data layer for PostgreSQL — Railway provides a free PostgreSQL instance, and the data helpers in `app.py` are designed to make this straightforward.

## project structure

```
finance-tracker/
├── app.py                  # Routes and data logic
├── requirements.txt
├── Procfile                # Railway deployment
├── runtime.txt
├── .gitignore
├── README.md
├── static/
│   └── images/             # Screenshots
└── templates/
    ├── base.html           # Shared layout, nav, CSS
    ├── index.html          # Dashboard
    ├── add.html            # Add transaction form
    ├── transactions.html   # Transaction history
    └── budget.html         # Budget tracker
```

## built by

[Emma Bowman](https://github.com/manbows)
