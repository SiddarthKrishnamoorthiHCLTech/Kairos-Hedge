# KAIROS-HEDGE — Weekly Trading Intelligence System

KAIROS-HEDGE is a unified, locally-run weekly trading intelligence system that combines an NSE stock screener (KAIROS) with a multi-agent AI investment debate engine (Hedge Fund) to identify the best positional and swing trade opportunities on the National Stock Exchange of India every Sunday. It runs 100% on your local laptop with zero paid APIs.

## What This System Does

1. **KAIROS** screens the entire NSE universe (~500 stocks) using 11 scoring frameworks (Minervini, O'Neil, Weinstein, Wyckoff, Buffett, Graham, Lynch, Momentum, Value, Growth, Quality) and outputs a filtered shortlist of top candidates.
2. **Hedge Fund** runs 18 AI analyst agents (Warren Buffett, Charlie Munger, Michael Burry, Cathie Wood, and 14 others) in a simulated debate on each shortlisted stock, producing BUY / HOLD / SELL verdicts with entry zones, stop losses, and targets.
3. The final weekly trade plan is delivered via Telegram and saved locally as both HTML and JSON reports.

---

## Prerequisites

- **Python 3.11+** — Download from [python.org](https://www.python.org/downloads/)
- **Git** — For cloning the repository
- **Ollama** (optional) — Local LLM fallback from [ollama.com](https://ollama.com)
- **Internet connection** — For yfinance data and LLM API calls

---

## Step-by-Step First-Time Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-repo/kairos-hedge.git
cd kairos-hedge
```

### 2. Run the setup script

```bash
python setup.py
```

This will:
- Verify Python 3.11+ is installed
- Create a virtual environment (`venv/`)
- Install all dependencies from `requirements.txt`
- Create output directories
- Copy `.env.example` to `.env`

### 3. Fill in your API keys in `.env`

Open `.env` in any text editor and fill in each key:

```bash
# Edit with your preferred editor
notepad .env        # Windows
code .env           # VS Code
nano .env           # Linux/Mac
```

### 4. (Optional) Adjust thresholds in `config.yaml`

All scoring thresholds, LLM settings, and trading parameters are configurable. The defaults work out of the box.

---

## Where to Get Each API Key

| Service | URL | What to Do |
|---------|-----|------------|
| **Groq** (Primary LLM) | [console.groq.com](https://console.groq.com) | Sign up free → API Keys → Create New Key |
| **Google Gemini** (Fallback 1) | [aistudio.google.com](https://aistudio.google.com) | Sign in → Get API Key → Create API Key |
| **OpenRouter** (Fallback 2) | [openrouter.ai](https://openrouter.ai) | Sign up → API Keys → Create Key |
| **Ollama** (Fallback 3) | [ollama.com](https://ollama.com) | Download → Run `ollama pull llama3` (no key needed) |
| **Telegram Bot** | [@BotFather](https://t.me/BotFather) | Send `/newbot` → Copy token → Get chat ID from `/getUpdates` |
| **Google Sheets** (Optional) | [console.cloud.google.com](https://console.cloud.google.com) | New Project → Enable Sheets API → Create Service Account → Download JSON |

---

## How to Fill `.env` and `config.yaml`

### `.env` — API Keys (fill once)

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxx
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxx
TELEGRAM_BOT_TOKEN=7000000000:AAFxxxxx
TELEGRAM_CHAT_ID=123456789
```

### `config.yaml` — Tunable Parameters

Key settings you may want to adjust:

```yaml
kairos:
  min_kairos_score: 65      # Minimum score to shortlist (0-100)
  top_n_shortlist: 10       # Max stocks to analyze

hedge_fund:
  min_consensus_confidence: 70  # Min confidence for valid trade
  min_buy_agents: 10            # Min agents voting BUY
  sl_percent: 5.0               # Stop loss percentage
```

---

## How to Run Every Sunday

### Option A: One-click launcher

- **Windows**: Double-click `run_sunday.bat`
- **Mac/Linux**: Run `./run_sunday.sh`

### Option B: Manual command

```bash
# Windows
venv\Scripts\activate
python run_weekly.py

# Mac/Linux
source venv/bin/activate
python run_weekly.py
```

### Option C: Single command

```bash
python run_weekly.py
```

The pipeline will:
1. Screen ~500 NSE stocks through 11 frameworks
2. Shortlist top 10 candidates
3. Run 18 AI agents on each stock
4. Generate decisions with entry/exit/SL levels
5. Send Telegram notification
6. Save HTML + JSON reports in `output/`

---

## What the Output Looks Like

### Telegram Message

```
🧠 KAIROS-HEDGE WEEKLY REPORT — 2026-03-29

✅ Valid Trade Setups: 2 of 8 screened

1️⃣ RELIANCE — BUY
   Entry: ₹2840–2860 | SL: ₹2780 | T1: ₹2980 | T2: ₹3100
   Confidence: 76% | Agents: 13 Buy / 4 Hold / 1 Sell
   ⚠️ Risk: Macro analyst flagged rupee weakness

2️⃣ INFY — BUY
   Entry: ₹1420–1435 | SL: ₹1390 | T1: ₹1500 | T2: ₹1560
   Confidence: 81% | Agents: 15 Buy / 2 Hold / 1 Sell

📁 Full report saved locally.
```

### Local Files

- `output/shortlist.json` — KAIROS screener output
- `output/weekly_report.json` — Full structured results
- `output/reports/kairos_hedge_2026-03-29.html` — Archived HTML report

---

## Troubleshooting: Top 5 Common Errors and Fixes

### 1. `ModuleNotFoundError: No module named 'yfinance'`

**Cause**: Dependencies not installed or wrong Python environment.

**Fix**:
```bash
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux
pip install -r requirements.txt
```

### 2. `LLMError: All providers failed`

**Cause**: No LLM API keys configured, or all providers are rate-limited.

**Fix**:
- Check `.env` has at least one valid API key (Groq recommended)
- Verify your key at [console.groq.com](https://console.groq.com)
- If rate-limited, wait 60 seconds and re-run
- Install Ollama as offline fallback: `ollama pull llama3`

### 3. `DataError: No OHLCV data returned`

**Cause**: yfinance couldn't fetch data (weekend/holiday, network issue, or invalid ticker).

**Fix**:
- Ensure you have internet connectivity
- NSE data may be unavailable on holidays — try on a regular trading day
- The system automatically skips failed tickers and continues

### 4. `Telegram API error 401: Unauthorized`

**Cause**: Invalid Telegram bot token.

**Fix**:
- Open Telegram → Search @BotFather → Send `/token` to verify
- Copy the exact token (format: `1234567890:AABBCCddEEffGGhhIIjjKKllMMnnOOppQQ`)
- For chat ID: visit `https://api.telegram.org/bot<TOKEN>/getUpdates` after sending a message to your bot

### 5. `ConfigError` or `.env` not loading

**Cause**: `.env` file missing or incorrectly formatted.

**Fix**:
- Ensure `.env` exists in the project root (same folder as `run_weekly.py`)
- Copy from template: `copy .env.example .env` (Windows) or `cp .env.example .env` (Mac/Linux)
- No spaces around `=` signs
- No quotes around values (unless they contain spaces)

---

## Project Structure

```
kairos-hedge/
├── run_weekly.py          ← Single entry point
├── config.yaml            ← All tunable parameters
├── .env                   ← API secrets (fill once)
├── requirements.txt       ← Pinned dependencies
├── setup.py               ← One-time setup script
├── run_sunday.bat          ← Windows launcher
├── run_sunday.sh           ← Mac/Linux launcher
├── kairos/                ← Module 1: NSE Screener
│   ├── screener.py        ← Pipeline orchestrator
│   ├── data/              ← yfinance fetcher + NSE universe
│   ├── scoring/           ← 11 scoring frameworks
│   └── filters/           ← Technical + fundamental filters
├── hedge_fund/            ← Module 2: AI Debate Engine
│   ├── agents/            ← 18 AI analyst agents
│   ├── engine/            ← Orchestrator + debate + decision
│   ├── llm/               ← Multi-provider router with failover
│   └── backtester.py      ← Performance metrics
├── notifier/              ← Telegram + HTML formatter
├── core/                  ← Config, schemas, logging, exceptions
├── output/                ← Generated reports (auto-created)
└── credentials/           ← Google service account (optional)
```

---

## License

This project is for educational and personal use only. Not financial advice. Always do your own research before making investment decisions.