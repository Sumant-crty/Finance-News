# Finance-News

Aggregates financial headlines from 40+ RSS feeds and news sites (Bloomberg, Reuters, WSJ,
CNBC, Economic Times, Moneycontrol, CoinDesk, Kitco, and more), dedupes them, and serves
them as a single searchable, filterable HTML dashboard grouped by category
(International Markets, Indian Markets, Crypto & Fintech, Commodities).

## Project layout
- `backend/financeNews.py` — scrapes/fetches headlines, generates `frontend/index.html`,
  and serves it via a small Flask app.
- `frontend/` — static output directory; `index.html` here is regenerated on every app
  start, so it doesn't need to be hand-edited.

## Run locally
```
cd backend
pip install -r requirements.txt
python financeNews.py
```
Then open http://localhost:5000.

## Deploy (e.g. Render)
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn financeNews:app`
- The app regenerates `frontend/index.html` on startup, so no separate data pipeline is needed.
