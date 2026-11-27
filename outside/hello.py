"""Smoke test for the out_* probe route: which outside hosts answer from GitHub Actions."""
import sys, urllib.request
HOSTS = sys.argv[1:] or ["https://api.hyperliquid.xyz/info", "https://fapi.binance.com/fapi/v1/ping",
    "https://api.bybit.com/v5/market/time", "https://www.okx.com/api/v5/public/time", "https://api.kraken.com/0/public/Time",
    "https://api.smarkets.com/v3/events/?limit=1", "https://data.binance.vision/", "https://api.betfair.com/", "https://www.svenskaspel.se/"]
for h in HOSTS:
    try:
        req = urllib.request.Request(h, headers={"User-Agent": "Mozilla/5.0"})
        if "hyperliquid" in h:
            req = urllib.request.Request(h, data=b'{"type":"meta"}', headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            print(h, r.status, r.read(120))
    except Exception as e:
        print(h, "ERR", str(e)[:150])
