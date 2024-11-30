# twsbot

Algotrading bot for Interactive Brokers TWS API.

## Features

### Indicators

- Moving Averages (EMA, VMA)
- Average Directional Index (ADX)
- Bollinger Bands (BB)
- Keltner Channels (KC)
- Average True Range (ATR)

### Trade signals

- EMA crossovers
- ADX trend strength and direction
- Consolidation detection
- WIP: Breakout detection

### Risk management

- Trailing stop-loss level based on ATR

## Installation

```bash
git clone https://github.com/jarijokinen/twsbot
cd twsbot
python3 -m venv venv
source venv/bin/activate
pip install -e .
twsbot NVDA
```

## License

MIT License. Copyright (c) 2024 [Jari Jokinen](https://jarijokinen.com).  See
[LICENSE](https://github.com/jarijokinen/twsbot/blob/main/LICENSE.txt)
for further details.
