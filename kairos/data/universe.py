"""NSE stock universe loader using nsetools and jugaad-trader fallback."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from core.exceptions import DataError
from core.logger import get_logger

_log = get_logger(__name__)

_FALLBACK_NIFTY500: list[str] = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "SBIN",
    "BHARTIARTL", "KOTAKBANK", "ITC", "LT", "AXISBANK", "BAJFINANCE", "MARUTI",
    "HCLTECH", "ASIANPAINT", "SUNPHARMA", "TITAN", "WIPRO", "ULTRACEMCO",
    "NTPC", "TATAMOTORS", "POWERGRID", "NESTLEIND", "ONGC", "JSWSTEEL",
    "M&M", "ADANIENT", "ADANIPORTS", "TATASTEEL", "TECHM", "BAJAJFINSV",
    "HDFCLIFE", "DIVISLAB", "GRASIM", "COALINDIA", "CIPLA", "BRITANNIA",
    "SBILIFE", "DRREDDY", "EICHERMOT", "APOLLOHOSP", "INDUSINDBK", "TATACONSUM",
    "HEROMOTOCO", "BAJAJ-AUTO", "DABUR", "BPCL", "HINDALCO", "PIDILITIND",
    "GODREJCP", "HAVELLS", "SIEMENS", "AMBUJACEM", "DLF", "ACC",
    "BIOCON", "NAUKRI", "BERGEPAINT", "COLPAL", "MARICO", "JUBLFOOD",
    "BALKRISIND", "MUTHOOTFIN", "VOLTAS", "TRENT", "MRF", "PIIND",
    "CONCOR", "IDFCFIRSTB", "PEL", "CANBK", "BANKBARODA", "PNB",
    "FEDERALBNK", "MPHASIS", "LTIM", "PERSISTENT", "COFORGE", "TATACOMM",
    "ABCAPITAL", "AUROPHARMA", "LUPIN", "TORNTPHARM", "ALKEM", "IPCALAB",
    "LAURUSLABS", "ZYDUSLIFE", "METROPOLIS", "LALPATHLAB", "MAXHEALTH", "ASTRAL",
    "POLYCAB", "KEI", "CUMMINSIND", "THERMAX", "CGPOWER", "BEL",
    "HAL", "BHEL", "IRCTC", "INDIANHOTELS", "PAGEIND", "CROMPTON",
    "WHIRLPOOL", "BATAINDIA", "RELAXO", "SYNGENE", "AAVAS", "CANFINHOME",
    "CHOLAFIN", "MANAPPURAM", "LICHSGFIN", "RECLTD", "PFC", "IRFC",
    "IOC", "GAIL", "PETRONET", "SAIL", "NMDC", "VEDL",
    "JINDALSTEL", "NATIONALUM", "HINDCOPPER", "TATAPOWER", "ADANIGREEN",
    "ADANITRANS", "TATAELXSI", "LTTS", "HAPPSTMNDS", "SONACOMS", "DIXON",
    "KAYNES", "ABB", "HONAUT", "SCHAEFFLER", "SKFINDIA", "TIMKEN",
    "GRINDWELL", "ATUL", "DEEPAKNTR", "NAVINFLUOR", "SRF", "FLUOROCHEM",
    "CLEAN", "BOSCHLTD", "MOTHERSON", "SUNTV", "ZEEL", "PVR",
    "UPL", "GNFC", "CHAMBLFERT", "COROMANDEL", "DHANUKA", "RALLIS",
    "EMAMILTD", "GODREJPROP", "OBEROIRLTY", "PRESTIGE", "PHOENIXLTD",
    "BRIGADE", "SOBHA", "SUNTECK", "ZOMATO", "NYKAA", "PAYTM",
    "DELHIVERY", "POLICYBZR", "STARHEALTH", "LICI", "GICRE", "NIACL",
    "ICICIGI", "ICICIPRULI", "HDFCAMC", "NIPPONLIFE", "UTI", "CAMS",
    "MCX", "BSE", "CDSL", "IEX", "ANGELONE", "JIOFIN",
    "BAJAJHLDNG", "MINDTREE", "ZENSAR", "ROUTE", "TANLA", "RATEGAIN",
    "SAPPHIRE", "MASTEK", "NEWGEN", "INTELLECT", "OFSS", "KPITTECH",
    "CYIENT", "AFFLE", "LATENTVIEW", "DATAPATTNS", "MAPMYINDIA", "YATHARTH",
]


@dataclass(slots=True)
class UniverseLoader:
    """Loads NSE stock symbols for the screener."""

    max_symbols: int = 500
    _symbols: list[str] = field(default_factory=list, init=False)

    async def load(self) -> list[str]:
        """Return list of NSE ticker symbols."""
        self._symbols = await self._load_from_nsetools()
        if len(self._symbols) < 50:
            _log.warning("nsetools returned few symbols, using fallback list")
            self._symbols = _FALLBACK_NIFTY500[: self.max_symbols]
        return self._symbols[: self.max_symbols]

    async def _load_from_nsetools(self) -> list[str]:
        """Attempt loading symbols via nsetools in a thread."""
        try:
            symbols = await asyncio.to_thread(self._fetch_nsetools)
            _log.info(f"Loaded {len(symbols)} symbols from nsetools")
            return symbols
        except Exception as exc:
            _log.warning(f"nsetools failed: {exc}, falling back to hardcoded list")
            return []

    @staticmethod
    def _fetch_nsetools() -> list[str]:
        """Synchronous nsetools fetch wrapped for thread execution."""
        try:
            from nsetools import Nse
            nse = Nse()
            all_codes = list(nse.get_stock_codes().keys())
            filtered = [s for s in all_codes if s != "SYMBOL" and len(s) <= 20]
            return sorted(filtered)
        except ImportError:
            raise DataError("nsetools not installed")
        except Exception as exc:
            raise DataError(f"nsetools error: {exc}")
