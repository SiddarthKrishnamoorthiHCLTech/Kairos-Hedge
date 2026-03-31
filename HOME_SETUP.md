# KAIROS-HEDGE — Home Setup Guide

> Complete guide to running the system on a fresh machine (no corporate proxy).

---

## Prerequisites

| Requirement | Version | Download |
|---|---|---|
| Python | 3.11 or 3.12 | https://www.python.org/downloads/ |
| Git | Any | https://git-scm.com/downloads |

> **Important:** During Python install on Windows, check **"Add Python to PATH"**.

---

## Step 1 — Get the Code

### Option A — USB / Pendrive / Zip (recommended if no internet at office)
Copy the entire `Kairos-Hedge` folder to your home machine. Skip to Step 2.

### Option B — Git Clone (if you pushed to GitHub/GitLab)
```bash
git clone https://github.com/YOUR_USERNAME/kairos-hedge.git
cd kairos-hedge
```

---

## Step 2 — One-Time Setup

Open a terminal (PowerShell on Windows, bash on Mac/Linux) inside the project folder:

```bash
python setup.py
```

This automatically:
- ✅ Checks Python 3.11+
- ✅ Creates a `venv/` virtual environment
- ✅ Installs all packages (`yfinance`, `pydantic`, `aiohttp`, etc.)
- ✅ Creates output directories
- ✅ Copies `.env.example` → `.env`

---

## Step 3 — Fill In Your API Keys

Open the `.env` file in any text editor (Notepad is fine):

```
Kairos-Hedge\.env
```

### Minimum required (pick at least ONE LLM):

#### Option A — Groq (Free, Fastest — Recommended)
1. Go to https://console.groq.com
2. Sign up (free) → **API Keys** → **Create New Key**
3. Paste into `.env`:
   ```
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

#### Option B — Google Gemini (Free)
1. Go to https://aistudio.google.com
2. Sign in → **Get API Key** → **Create API Key**
3. Paste into `.env`:
   ```
   GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

#### Option C — OpenRouter (Free credits)
1. Go to https://openrouter.ai → Sign up → **API Keys** → **Create Key**
2. Paste into `.env`:
   ```
   OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxxxxxxxxx
   ```

#### Option D — Ollama (100% local, no internet, no key)
1. Download from https://ollama.com and install
2. In a terminal: `ollama pull llama3`
3. No `.env` changes needed — it uses `http://localhost:11434` by default

---

### Optional — Telegram Notifications

Get a Telegram bot to receive the weekly report on your phone:

1. Open Telegram → Search **@BotFather** → Send `/newbot`
2. Follow prompts → copy the **token** (looks like `7123456789:AAF...`)
3. Start your bot (search its username, press Start)
4. Open this URL in your browser (replace `YOUR_TOKEN`):
   ```
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```
5. Send any message to your bot first, then refresh the URL
6. Copy the number from `"chat":{"id": XXXXXXXXX}`
7. Fill in `.env`:
   ```
   TELEGRAM_BOT_TOKEN=7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxx
   TELEGRAM_CHAT_ID=123456789
   ```

---

## Step 4 — Run the Pipeline

### Every Sunday (Weekly Run)

**Windows — Double-click:**
```
run_sunday.bat
```

**Windows — PowerShell:**
```powershell
venv\Scripts\activate
python run_weekly.py
```

**Mac/Linux:**
```bash
source venv/bin/activate
python run_weekly.py
```

---

## What Happens When You Run It

```
KAIROS-HEDGE
│
├── MODULE 1: KAIROS SCREENER
│   ├── Loads 500 NSE stocks (Nifty 500 universe)
│   ├── Fetches 1-year OHLCV + fundamentals from Yahoo Finance
│   ├── Scores each stock across 11 frameworks:
│   │   Minervini, O'Neil, Weinstein, Wyckoff,
│   │   Buffett, Graham, Lynch, Momentum, Value, Growth, Quality
│   ├── Filters: Stage 2, RS Rating, Breakout, Volume, PE, ROE, Debt
│   └── Produces shortlist (top ~5–15 stocks)
│
└── MODULE 2: HEDGE FUND DEBATE ENGINE
    ├── 18 AI Agents analyze each shortlisted stock:
    │   Warren Buffett, Charlie Munger, Michael Burry,
    │   Cathie Wood, Bill Ackman, Ben Graham, Aswath Damodaran,
    │   Technical Analyst, Sentiment Analyst, Macro Analyst,
    │   Risk Manager, Quant Analyst, Momentum Analyst,
    │   Options Flow, Insider Tracker, Sector Rotation,
    │   ESG Analyst, Geopolitical Analyst
    ├── Debate engine detects disagreements, builds consensus
    ├── Portfolio Manager makes final BUY / HOLD / SKIP decision
    ├── Entry zone, Stop-Loss, Target 1, Target 2 calculated
    └── Delivers:
        ├── output/weekly_report.json
        ├── output/reports/kairos_hedge_YYYY-MM-DD.html
        └── Telegram message (if configured)
```

---

## Output Files

| File | Description |
|---|---|
| `output/weekly_report.json` | Machine-readable full report |
| `output/shortlist.json` | KAIROS screener shortlist with scores |
| `output/reports/kairos_hedge_YYYY-MM-DD.html` | Open in browser — visual report |
| `output/logs/kairos_YYYY-MM-DD.log` | Full run log for debugging |

Open the HTML report in any browser to see the formatted results.

---

## Adjusting Settings (Optional)

Edit `config.yaml` to tune behaviour:

| Setting | Default | Description |
|---|---|---|
| `kairos.min_score` | `60` | Minimum KAIROS score to shortlist |
| `kairos.max_stocks` | `15` | Max stocks passed to hedge fund |
| `kairos.lookback_days` | `365` | Days of price history to fetch |
| `hedge_fund.min_confidence` | `60` | Min confidence % to mark as valid trade |
| `trading.skip_week_below` | `3` | Skip week if fewer valid trades than this |

---

## Troubleshooting

### `ModuleNotFoundError`
You skipped setup or forgot to activate venv:
```bash
python setup.py           # re-run setup
venv\Scripts\activate     # Windows — activate venv
python run_weekly.py
```

### `yfinance` returns no data
- Yahoo Finance sometimes rate-limits. Wait 5 minutes and retry.
- Check your internet connection.

### LLM errors (HTTP 403 / 401)
- Your API key is wrong or expired — re-check `.env`
- For Groq: verify key at https://console.groq.com
- The system auto-falls-back through all 4 LLM providers — at least one must work.

### Telegram not sending
- Make sure you sent at least one message TO your bot first
- Verify the `TELEGRAM_CHAT_ID` is numeric (not a username)

### `SSL certificate problem` errors
- You are on a corporate network — run from home instead where there is no SSL proxy.

---

## Run Schedule

Set a weekly Windows Task Scheduler job to automate:

1. Open **Task Scheduler** → **Create Basic Task**
2. Name: `KAIROS-HEDGE Weekly`
3. Trigger: **Weekly → Sunday → 9:00 AM**
4. Action: **Start a Program**
   - Program: `C:\path\to\Kairos-Hedge\run_sunday.bat`
5. **Finish**

---

## Quick Reference Card

```
First time only:
  python setup.py          ← creates venv, installs packages, makes .env
  notepad .env             ← fill in at least one LLM API key

Every Sunday:
  run_sunday.bat           ← double-click, wait ~5 minutes
  (or: venv\Scripts\activate && python run_weekly.py)

Results:
  output\reports\kairos_hedge_YYYY-MM-DD.html   ← open in browser
  Telegram message on your phone (if configured)
```

---

*KAIROS-HEDGE — For educational purposes only. Not financial advice.*
