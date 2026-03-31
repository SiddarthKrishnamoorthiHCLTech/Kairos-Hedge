"""Async Telegram notification sender."""

from __future__ import annotations

import aiohttp

from core.exceptions import NotifierError
from core.logger import get_logger

_log = get_logger(__name__)

_TELEGRAM_API = "https://api.telegram.org"


async def send_telegram_message(
    bot_token: str,
    chat_id: str,
    message: str,
) -> bool:
    """Send a message via Telegram Bot API."""
    if not bot_token or not chat_id:
        _log.warning("Telegram credentials not configured, skipping notification")
        return False

    url = f"{_TELEGRAM_API}/bot{bot_token}/sendMessage"
    chunks = _split_message(message, max_len=4000)

    for chunk in chunks:
        success = await _send_chunk(url, chat_id, chunk)
        if not success:
            return False

    _log.info(f"Telegram message sent ({len(chunks)} chunk(s))")
    return True


async def _send_chunk(url: str, chat_id: str, text: str) -> bool:
    """Send a single message chunk to Telegram."""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    _log.error(f"Telegram API error {resp.status}: {body[:200]}")
                    return False
                return True
    except aiohttp.ClientError as exc:
        _log.error(f"Telegram connection error: {exc}")
        return False


def _split_message(message: str, max_len: int = 4000) -> list[str]:
    """Split long messages into Telegram-safe chunks."""
    if len(message) <= max_len:
        return [message]
    chunks: list[str] = []
    lines = message.split("\n")
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > max_len:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        chunks.append(current)
    return chunks
