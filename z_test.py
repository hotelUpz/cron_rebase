# # networks.py

# import asyncio
# import aiohttp
# from typing import *
# from c_log import ErrorHandler

# CHECK_URL = "https://api.binance.com/api/v3/ping"
# SESSION_CHECK_INTERVAL = 15  # секунд


# PROXY_LIST: List = [
#     {
#         "enable": True,                     # флаг активности прокси
#         "proxy_address": '154.222.214.132',
#         "proxy_port": '62890',
#         "proxy_login": '1FDJcwJR',
#         "proxy_password": 'U2yrFg4a'
#     },
#     {
#         "enable": True,
#         "proxy_address": '154.218.20.43',
#         "proxy_port": '64630',
#         "proxy_login": '1FDJcwJR',
#         "proxy_password": 'U2yrFg4a'
#     },
#     {
#         "enable": True,
#         "proxy_address": '45.192.135.214',
#         "proxy_port": '59100',
#         "proxy_login": 'nikolassmsttt0Icgm',
#         "proxy_password": 'agrYpvDz7D'
#     },
#     None  # локальный ip адрес
# ]


# def get_proxy_list(cfg_list: List) -> List[Optional[str]]:
#     """
#     Собирает уникальные прокси в порядке появления.
#     Повторяющиеся конфиги удаляются.
#     Возвращает список proxy_url или None.
#     """
#     seen = set()
#     result: List[Optional[str]] = []

#     for cfg in cfg_list:
#         if cfg and cfg.get("enable"):
#             url = (
#                 f"http://{cfg['proxy_login']}:"
#                 f"{cfg['proxy_password']}@"
#                 f"{cfg['proxy_address']}:"
#                 f"{cfg['proxy_port']}"
#             )

#             if url not in seen:
#                 seen.add(url)
#                 result.append(url)
#         else:
#             # добавляем None только один раз
#             if None not in seen:
#                 seen.add(None)
#                 result.append(None)

#     return result

# import math

# current_notional = 25.0
# initial_notional = 10.0

# real_progress = max(1, round(current_notional / initial_notional))

# print(real_progress)

# def reconstruct_entry_price(avg_price: float, grid_orders: list, progress: int, side: str):
#     used = grid_orders[:progress]

#     # итеративно подбираем entry (потому нужна численная оптимизация)
#     def avg_from_entry(entry):
#         prices = [entry * (1 + step['indent']/100) for step in used]
#         qty = [step['volume'] / price for step, price in zip(used, prices)]
#         return sum(p*q for p, q in zip(prices, qty)) / sum(qty)

#     # бинарный поиск (идеально работает)
#     low, high = avg_price * 0.2, avg_price * 5
#     for _ in range(60):
#         mid = (low + high) / 2
#         calc = avg_from_entry(mid)
#         if calc > avg_price:
#             high = mid
#         else:
#             low = mid
#     return (low + high) / 2


# def reconstruct_entry_price(avg_price: float, grid_orders: list, progress: int, side: str) -> float | None:
#     """
#     Восстанавливает исходный entry_price по средней цене Binance.

#     :param avg_price: Binance avgPrice
#     :param grid_orders: список шагов грida [{'indent': -8.0, 'volume': 11.57, ...}, ...]
#     :param progress: фактический шаг усреднения (1 = только первый ордер, 2 = первый+второй и т.д.)
#     :param side: 'LONG' или 'SHORT'
#     """
#     if progress <= 0:
#         return None

#     used = grid_orders[:min(progress, len(grid_orders))]
#     volumes = [step["volume"] for step in used]

#     if not volumes or sum(volumes) == 0:
#         return None

#     # множители цен для каждого шага
#     k = []
#     for step in used:
#         indent = float(step["indent"])
#         # indent у тебя в процентах (отрицательный при усреднении)
#         if side == "LONG":
#             # цена ниже исходной
#             ki = 1.0 + indent / 100.0
#         elif side == "SHORT":
#             # для шорта цена выше исходной:
#             # indent тоже отрицательный, поэтому 1 - indent/100 = 1 + |indent|/100
#             ki = 1.0 - indent / 100.0
#         else:
#             return None

#         k.append(ki)

#     sum_V = sum(volumes)
#     denom = sum(v * ki for v, ki in zip(volumes, k))

#     if denom <= 0:
#         return None

#     entry0 = avg_price * sum_V / denom
#     return entry0




# grid_long = [
#     {'indent': 0.0, 'volume': 10.52, 'signal': True},
#     {'indent': -8.0, 'volume': 11.57, 'signal': False},
#     {'indent': -16.0, 'volume': 12.73, 'signal': False},
#     {'indent': -24.0, 'volume': 14.0,  'signal': False},
#     {'indent': -34.0, 'volume': 15.4,  'signal': False},
#     {'indent': -55.0, 'volume': 16.94, 'signal': False},
#     {'indent': -89.0, 'volume': 18.63, 'signal': False},
# ]

# avg_price = 0.1213   # Binance avgPrice
# progress  = 4        # значит отработали первые 4 ордера (0, -8, -16, -24)

# entry0 = reconstruct_entry_price(avg_price, grid_long, progress, side="LONG")

# print("=== RECONSTRUCT TEST ===")
# print(f"Binance avg_price:   {avg_price:.8f}")
# print(f"Progress:            {progress}")
# print(f"Reconstructed entry: {entry0:.8f}")

# # Проверяем, что если пересчитать среднюю из уровней грida, получим то же avg_price
# used = grid_long[:progress]

# level_prices = [
#     entry0 * (1.0 + step["indent"] / 100.0)
#     for step in used
# ]
# volumes = [step["volume"] for step in used]

# w_avg = sum(p * v for p, v in zip(level_prices, volumes)) / sum(volumes)

# print(f"Level prices:        {[round(p, 8) for p in level_prices]}")
# print(f"Recalc avg:          {w_avg:.8f}")
# print(f"MATCH:               {abs(w_avg - avg_price) < 1e-8}")



# ============================================
#   RECONSTRUCT ENTRY PRICE — FULL TEST MODULE
# ============================================

# # from __future__ import annotations
# from typing import *
# Side = Literal["LONG", "SHORT"]

# grid_long = [
#     {'indent': 0.0, 'volume': 10.52, 'signal': True},
#     {'indent': -8.0, 'volume': 11.57, 'signal': False}, # %
#     {'indent': -16, 'volume': 12.73, 'signal': False}, # %
#     {'indent': -24, 'volume': 14, 'signal': False}, # %
#     {'indent': -34, 'volume': 15.4, 'signal': False}, # %
#     {'indent': -55, 'volume': 16.94, 'signal': False}, # %
#     {'indent': -89, 'volume': 18.63, 'signal': False}, # %
# ]

# def reconstruct_entry_price(
#     avg_price: float,
#     grid_orders: List[dict],
#     progress: int,
#     side: Side
# ) -> Optional[float]:
#     """
#     Восстанавливает исходный entry_price по Binance avg_price.

#     avg_price   – Binance avgPrice
#     grid_orders – [{indent, volume, ...}, ...]
#     progress    – фактическое количество отработанных шагов (1..N)
#     side        – 'LONG' или 'SHORT'
#     """
#     if avg_price <= 0 or progress <= 0:
#         return None

#     used = grid_orders[:min(progress, len(grid_orders))]
#     if not used:
#         return None

#     vols = [float(step["volume"]) for step in used]
#     sum_vols = sum(vols)
#     if sum_vols <= 0:
#         return None

#     num = 0.0

#     for step, v in zip(used, vols):
#         indent = float(step["indent"])

#         if side == "LONG":
#             # цена ниже исходной: entry * (1 + indent/100), indent <= 0
#             k = 1.0 + indent / 100.0
#         elif side == "SHORT":
#             # для шорта цена выше исходной:
#             # indent тоже отрицательный, но для шорта это "вверх"
#             k = 1.0 - indent / 100.0
#         else:
#             return None

#         if k <= 0:
#             return None

#         # ★ ВАЖНО: именно v / k, а НЕ v * k
#         num += v / k

#     # Формула:
#     # entry0 = avg * ( Σ(v_i / k_i) / Σ v_i )
#     entry0 = avg_price * (num / sum_vols)
#     return entry0


# # ============================================================
# #   NICE PRINT
# # ============================================================

# def print_test(side: str, grid: list, progress: int, avg_price: float):
#     print(f"\n===== TEST {side} | progress={progress} =====")

#     entry = reconstruct_entry_price(avg_price, grid, progress, side)
#     print(f"Reconstructed ENTRY: {entry:.8f}")


# # ============================================================
# #   RUN ALL TESTS
# # ============================================================

# if __name__ == "__main__":
#     for p in range(1, 5):
#         print_test("LONG", grid_long, progress=p, avg_price=0.1213)


# # ============================================================
# #   GRID RECONSTRUCT ENTRY — FULL UNIT TEST
# #   Проверка работы формулы через qty, price, notional (как Binance)
# # ============================================================

# from __future__ import annotations
# from typing import List, Literal, Optional
# import math

# Side = Literal["LONG", "SHORT"]

# # ============================================================
# #   INPUT GRID (твой реальный)
# # ============================================================

# grid_long = [
#     {'indent': 0.0, 'volume': 10.52},
#     {'indent': -8.0, 'volume': 11.57},
#     {'indent': -16.0, 'volume': 12.73},
#     {'indent': -24.0, 'volume': 14.0},
#     {'indent': -34.0, 'volume': 15.4},
#     {'indent': -55.0, 'volume': 16.94},
#     {'indent': -89.0, 'volume': 18.63},
# ]

# margin_size = 81.6
# leverage = 10
# avg_price_target = 0.1213


# # ============================================================
# #   RECONSTRUCT ENTRY FUNCTION
# # ============================================================

# def reconstruct_entry_price(
#     avg_price: float,
#     grid_orders: List[dict],
#     progress: int,
#     side: Side
# ) -> Optional[float]:

#     if avg_price <= 0 or progress <= 0:
#         return None

#     used = grid_orders[:min(progress, len(grid_orders))]
#     vols = [float(step["volume"]) for step in used]
#     sum_vols = sum(vols)

#     if sum_vols <= 0:
#         return None

#     num = 0.0

#     for step, v in zip(used, vols):
#         indent = float(step["indent"])

#         if side == "LONG":
#             k = 1.0 + indent / 100.0
#         elif side == "SHORT":
#             k = 1.0 - indent / 100.0
#         else:
#             return None

#         if k <= 0:
#             return None

#         num += v / k

#     entry0 = avg_price * (num / sum_vols)
#     return entry0


# # ============================================================
# #   FULL BINANCE-REALISTIC AVG CHECK
# # ============================================================

# def binance_avg_from_entry(entry0: float, progress: int, side: Side) -> float:
#     """
#     Пересчитывает Binance avg через:
#         price_i = entry0 * k_i
#         notional_i = base_notional * volume_i%
#         qty_i = notional_i / price_i
#     """

#     base_notional = margin_size * leverage

#     used = grid_long[:progress]

#     prices = []
#     notionals = []
#     qtys = []

#     for step in used:
#         indent = float(step["indent"])
#         volume = float(step["volume"]) / 100.0

#         # ============================
#         #   price_i
#         # ============================
#         if side == "LONG":
#             k = 1 + indent / 100.0
#         else:
#             k = 1 - indent / 100.0

#         price_i = entry0 * k

#         # ============================
#         #   notional_i
#         # ============================
#         notional_i = base_notional * volume

#         # ============================
#         #   qty_i
#         # ============================
#         qty_i = notional_i / price_i

#         prices.append(price_i)
#         notionals.append(notional_i)
#         qtys.append(qty_i)

#     # ============================
#     #   Binance weighted avg
#     # ============================

#     total_cost = sum(p * q for p, q in zip(prices, qtys))
#     total_qty = sum(qtys)

#     return total_cost / total_qty


# # ============================================================
# #   RUN TESTS
# # ============================================================

# def run_test(progress: int):
#     print(f"\n===== TEST LONG | progress={progress} =====")

#     entry0 = reconstruct_entry_price(avg_price_target, grid_long, progress, "LONG")
#     print(f"Reconstructed ENTRY: {entry0:.8f}")

#     avg_recalc = binance_avg_from_entry(entry0, progress, "LONG")
#     error = abs(avg_recalc - avg_price_target)

#     # print detailed info
#     print(f"Recalc avg:         {avg_recalc:.10f}")
#     print(f"Target avg:         {avg_price_target:.10f}")
#     print(f"ERROR:              {error:.12f}")
#     print(f"MATCH:              {error < 1e-10}")


# if __name__ == "__main__":
#     for p in range(1, 5):
#         run_test(p)




from typing import List, Literal
from math import isclose

Side = Literal["LONG", "SHORT"]

# ============================================================
#   ТВОЙ REAL GRID
# ============================================================

grid_long = [
    {'indent': 0.0, 'volume': 10.52},
    {'indent': -8.0, 'volume': 11.57},
    {'indent': -16.0, 'volume': 12.73},
    {'indent': -24.0, 'volume': 14.0},
    {'indent': -34.0, 'volume': 15.4},
    {'indent': -55.0, 'volume': 16.94},
    {'indent': -89.0, 'volume': 18.63},
]

# ============================================================
#   CLASS COPIED FROM YOUR PROJECT
# ============================================================

class GridStep:
    def __init__(self, indent: float, volume: float):
        self.indent = indent
        self.volume = volume


class GridMath:
    def __init__(self, margin_size: float, leverage: float, grid_orders: List[dict]):
        self.margin_size = float(margin_size)
        self.leverage = float(leverage)

        self.steps: List[GridStep] = [
            GridStep(indent=float(g["indent"]), volume=float(g["volume"]))
            for g in grid_orders
        ]

        # base notional (банк * плечо)
        self.base_notional = self.margin_size * self.leverage

        # volume% → коэффициенты
        self._shares = [s.volume / 100.0 for s in self.steps]

        # notional_i = base_notional * volume_i%
        self.step_notional: List[float] = [
            self.base_notional * share for share in self._shares
        ]

        # cumulative notionals
        self.cum_notional = []
        acc = 0.0
        for n in self.step_notional:
            acc += n
            self.cum_notional.append(acc)

    # ---------------------------------------------
    def estimate_progress(self, actual_notional: float) -> int:
        """Находит ближайший progress по фактическому notional"""
        if actual_notional <= 0 or not self.cum_notional:
            return 1

        best_p = 1
        best_diff = float("inf")

        for i, expected in enumerate(self.cum_notional, start=1):
            diff = abs(expected - actual_notional)
            if diff < best_diff:
                best_diff = diff
                best_p = i

        return best_p


# ============================================================
#   TEST LOGIC
# ============================================================

def simulate_notional(progress: int, margin_size: float, leverage: float, grid: list) -> float:
    """
    Считает суммарный notional ровно так,
    как будет у Binance (ноtional = Σ(base_notional * volume_i%))
    """
    base_notional = margin_size * leverage
    total = 0.0

    for i in range(progress):
        volume_rate = grid[i]["volume"] / 100.0
        total += base_notional * volume_rate

    return total


def test_progress(progress: int):
    margin = 81.6
    lev = 10

    print(f"\n===== TEST PROGRESS = {progress} =====")

    # сколько должно быть фактически (как на бирже)
    fact_notional = simulate_notional(progress, margin, lev, grid_long)

    print(f"Simulated notional: {fact_notional:.4f} USDT")

    # считаем через наш GridMath
    gm = GridMath(margin, lev, grid_long)
    detected = gm.estimate_progress(fact_notional)

    print(f"Detected progress:  {detected}")
    print(f"Expected progress:  {progress}")
    print("MATCH:", detected == progress)

    return detected == progress


if __name__ == "__main__":
    # прогоняем все 1..7 шагов
    for p in range(1, 8):
        test_progress(p)
