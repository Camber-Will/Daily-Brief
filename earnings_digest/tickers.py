"""
tickers.py

Will's stock portfolio — individual stocks tracked for earnings reports.
ETFs (VOO, QQQ, XBI) are excluded as they don't report quarterly earnings.
"""

EARNINGS_TICKERS: dict[str, str] = {
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "TSM": "Taiwan Semiconductor",
    "MSFT": "Microsoft",
    "MELI": "MercadoLibre",
    "INTU": "Intuit",
    "NVDA": "NVIDIA",
    "ORCL": "Oracle",
    "V": "Visa",
    "AAPL": "Apple",
    "DKNG": "DraftKings",
    "GS": "Goldman Sachs",
    "CMG": "Chipotle",
    "META": "Meta Platforms",
    "PCOR": "Procore Technologies",
    "CRWD": "CrowdStrike",
    "DDOG": "Datadog",
}

# ETFs in portfolio — listed in email footer, not scanned for earnings
ETF_HOLDINGS: dict[str, str] = {
    "VOO": "Vanguard S&P 500 ETF",
    "QQQ": "Invesco Nasdaq-100 ETF",
    "XBI": "SPDR S&P Biotech ETF",
}
