import numpy as np
import threading

from collections import deque

bar_data = np.zeros(4680, dtype=[
    ('time', 'int64'),
    ('open', 'float64'),
    ('high', 'float64'),
    ('low', 'float64'),
    ('close', 'float64'),
    ('volume', 'float64')
])
bar_data_idx = 0
bar_data_lock = threading.Lock()

def append_bar_data(bar):
    global buffer, bar_data, bar_data_idx, bar_data_lock, bar_data_size

    with bar_data_lock:
        bar_data[bar_data_idx] = (
            bar.date,
            bar.open,
            bar.high,
            bar.low,
            bar.close,
            bar.volume
        )
        bar_data_idx = (bar_data_idx + 1) % len(bar_data)

def get_bars(field, num_bars=40):
    global bar_data, bar_data_idx, bar_data_lock

    with bar_data_lock:
        num_bars = min(num_bars, len(bar_data))
        start = (bar_data_idx - num_bars) % len(bar_data)

        if start < bar_data_idx:
            return bar_data[field][start:bar_data_idx]
        else:
            return np.concatenate((
                bar_data[field][start:],
                bar_data[field][:bar_data_idx]
            ))

buffer = deque(maxlen=15)
