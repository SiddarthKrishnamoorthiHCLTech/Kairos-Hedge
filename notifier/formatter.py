"""Formats JSON results into Telegram messages and HTML reports."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from core.logger import get_logger
from core.schemas import Signal, StockDecision, WeeklyReport

_log = get_logger(__name__)

_NUMBER_EMOJI = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


def format_telegram_message(report: WeeklyReport) -> str:
    """Format weekly report into Telegram-friendly text."""
    lines: list[str] = []
    lines.append(f"🧠 KAIROS-HEDGE WEEKLY REPORT — {report.date}")
    lines.append("")

    if report.skip_week:
        lines.append(report.skip_message)
        lines.append("📁 Full report saved locally.")
        return "\n".join(lines)

    valid = [d for d in report.decisions if d.valid_trade]
    lines.append(f"✅ Valid Trade Setups: {len(valid)} of {report.total_screened} screened")
    lines.append("")

    for i, dec in enumerate(report.decisions):
        emoji = _NUMBER_EMOJI[i] if i < len(_NUMBER_EMOJI) else f"{i + 1}."
        lines.append(f"{emoji} {dec.ticker} — {dec.consensus.value}")
        if dec.valid_trade and dec.consensus == Signal.BUY:
            lines.append(f"   Entry: {dec.entry_zone} | SL: {dec.stop_loss} | T1: {dec.target_1} | T2: {dec.target_2}")
            lines.append(f"   Confidence: {dec.consensus_confidence}% | Agents: {_vote_summary(dec)}")
            if dec.disagreements:
                lines.append(f"   ⚠️ Risk: {dec.disagreements[0]}")
        elif dec.consensus == Signal.HOLD:
            lines.append("   Awaiting breakout confirmation. Skip this week.")
        elif dec.consensus == Signal.SELL:
            lines.append("   Bearish consensus. Avoid.")
        lines.append("")

    if not valid:
        lines.append("⏭️ No valid trade setups this week. Stand aside. ✋")

    lines.append("📁 Full report saved locally.")
    return "\n".join(lines)


def _vote_summary(dec: StockDecision) -> str:
    """Format agent vote counts into compact string."""
    buy = dec.agent_votes.get("BUY", 0)
    hold = dec.agent_votes.get("HOLD", 0)
    sell = dec.agent_votes.get("SELL", 0)
    return f"{buy} Buy / {hold} Hold / {sell} Sell"


def format_html_report(report: WeeklyReport) -> str:
    """Generate a full HTML report from weekly results."""
    valid = [d for d in report.decisions if d.valid_trade]
    rows = ""
    for dec in report.decisions:
        badge = _signal_badge(dec.consensus)
        rows += f"""
        <tr>
            <td><strong>{dec.ticker}</strong></td>
            <td>{badge}</td>
            <td>{dec.consensus_confidence}%</td>
            <td>{dec.entry_zone or '—'}</td>
            <td>{dec.stop_loss or '—'}</td>
            <td>{dec.target_1 or '—'}</td>
            <td>{dec.target_2 or '—'}</td>
            <td>{dec.hold_weeks or '—'}</td>
            <td>{_vote_summary(dec)}</td>
        </tr>"""

    agent_details = ""
    for dec in report.decisions:
        agent_rows = ""
        for ao in dec.agent_outputs:
            badge = _signal_badge(ao.signal)
            risks = ", ".join(ao.key_risks) if ao.key_risks else "—"
            agent_rows += f"""
            <tr>
                <td>{ao.agent}</td>
                <td>{badge}</td>
                <td>{ao.confidence}%</td>
                <td>{ao.reasoning[:150]}...</td>
                <td>{risks}</td>
            </tr>"""
        agent_details += f"""
        <h3>{dec.ticker} — Agent Breakdown</h3>
        <table>
            <tr><th>Agent</th><th>Signal</th><th>Confidence</th><th>Reasoning</th><th>Risks</th></tr>
            {agent_rows}
        </table>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KAIROS-HEDGE Weekly Report — {report.date}</title>
<style>
    body {{ font-family: 'Segoe UI', sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #0d1117; color: #c9d1d9; }}
    h1 {{ color: #58a6ff; border-bottom: 2px solid #30363d; padding-bottom: 10px; }}
    h2 {{ color: #79c0ff; margin-top: 30px; }}
    h3 {{ color: #d2a8ff; margin-top: 20px; }}
    table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
    th {{ background: #161b22; color: #58a6ff; padding: 10px; text-align: left; border: 1px solid #30363d; }}
    td {{ padding: 8px 10px; border: 1px solid #30363d; }}
    tr:nth-child(even) {{ background: #161b22; }}
    .badge {{ padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em; }}
    .buy {{ background: #238636; color: white; }}
    .hold {{ background: #d29922; color: white; }}
    .sell {{ background: #da3633; color: white; }}
    .summary {{ background: #161b22; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #30363d; }}
</style>
</head>
<body>
<h1>🧠 KAIROS-HEDGE Weekly Report — {report.date}</h1>
<div class="summary">
    <p><strong>Universe Screened:</strong> {report.shortlist.universe_size} stocks</p>
    <p><strong>Passed Filters:</strong> {report.shortlist.filtered_count} stocks</p>
    <p><strong>Shortlisted:</strong> {len(report.shortlist.items)} stocks</p>
    <p><strong>Valid Trades:</strong> {len(valid)} of {report.total_screened}</p>
</div>
<h2>📊 Trade Decisions</h2>
<table>
    <tr><th>Ticker</th><th>Signal</th><th>Confidence</th><th>Entry</th><th>SL</th><th>T1</th><th>T2</th><th>Hold</th><th>Votes</th></tr>
    {rows}
</table>
<h2>🤖 Agent Analysis Details</h2>
{agent_details}
<footer style="margin-top:40px; color:#484f58; text-align:center;">
    <p>Generated by KAIROS-HEDGE on {report.date} — For educational purposes only. Not financial advice.</p>
</footer>
</body>
</html>"""
    return html


def _signal_badge(signal: Signal) -> str:
    """Return HTML badge for a signal."""
    css_class = signal.value.lower()
    return f'<span class="badge {css_class}">{signal.value}</span>'


def save_html_report(report: WeeklyReport, archive_dir: str) -> Path:
    """Save HTML report to archive directory."""
    out_dir = Path(archive_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"kairos_hedge_{report.date}.html"
    path = out_dir / filename
    path.write_text(format_html_report(report), encoding="utf-8")
    _log.info(f"HTML report saved to {path}")
    return path
