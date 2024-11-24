# twsbot

Algotrading bot for Interactive Brokers TWS API.

## Features

### Trade signals

Trade signals (buy or sell) are generated as a score. The score is calculated
by the strategies listed below.

- EMA9/EMA20 crossover
- ADX14 trend strength and direction

### Risk management

- Trailing stop-loss level based on ATR14

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
