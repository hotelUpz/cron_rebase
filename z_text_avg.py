# """
# Мок-тесты логики усреднения для класса Average.

# Запуск:
#     python test_average.py
# """

# from typing import Dict, Any

# # >>> ПРАВЬ ИМПОРТ ПОД СВОЙ ПРОЕКТ <<<
# # from BUSINESS.risk_orders_control import Average
# from BUSINESS.risk_orders_control import Average


# # ------------------------------
# #   Заглушки под контекст/логгер
# # ------------------------------
# class DummyHandler:
#     def debug_info_notes(self, msg: str, is_print: bool = False):
#         if is_print:
#             print("[DEBUG]", msg)

#     def trades_info_notes(self, msg: str, is_print: bool = False):
#         if is_print:
#             print("[TRADE]", msg)

#     # на всякий случай, если Average через wrap_foreign_methods дергает ещё что-то
#     def wrap_foreign_methods(self, obj):
#         # просто заглушка, ничего не делаем
#         return


# class DummyContext:
#     pass


# # ------------------------------
# #   Вспомогалки
# # ------------------------------
# def make_grid() -> list[Dict[str, Any]]:
#     """
#     Твой типичный grid:
#         indent в %, volume в %
#     """
#     return [
#         {'indent': 0.0,  'volume': 10.52, 'signal': True},
#         {'indent': -8.0, 'volume': 11.57, 'signal': False},
#         {'indent': -16,  'volume': 12.73, 'signal': False},
#         {'indent': -24,  'volume': 14.00, 'signal': False},
#     ]


# def almost_equal(a: float, b: float, eps: float = 1e-9) -> bool:
#     return abs(a - b) <= eps


# # ------------------------------
# #   ТЕСТЫ avg_control_func
# # ------------------------------
# def test_no_grid():
#     avg = Average(DummyContext(), DummyHandler())
#     new_prog, vol = avg.avg_control_func(
#         grid_orders=[],
#         avg_progress_counter=1,
#         normalized_sign=1,
#         nPnl=-10.0,
#         debug_label="[NO_GRID]"
#     )
#     assert new_prog == 1 and vol == 0.0, "При пустом grid усреднения быть не должно"
#     print("✔ test_no_grid OK")


# def test_not_enough_loss():
#     """
#     LONG, progress=1, indent=-8, PnL=-7 → усреднения НЕТ
#     """
#     avg = Average(DummyContext(), DummyHandler())
#     grid = make_grid()

#     new_prog, vol = avg.avg_control_func(
#         grid_orders=grid,
#         avg_progress_counter=1,     # работаем по step с indent=-8
#         normalized_sign=1,          # LONG
#         nPnl=-7.0,                  # -7% ещё не дотянуло
#         debug_label="[NOT_ENOUGH_LOSS]"
#     )

#     assert new_prog == 1 and vol == 0.0, "Не должно усреднять при недостаточном убытке"
#     print("✔ test_not_enough_loss OK")


# def test_exact_indent_trigger():
#     """
#     LONG, progress=1, indent=-8, PnL=-8 → ДОЛЖНО усреднить.
#     """
#     avg = Average(DummyContext(), DummyHandler())
#     grid = make_grid()

#     new_prog, vol = avg.avg_control_func(
#         grid_orders=grid,
#         avg_progress_counter=1,
#         normalized_sign=1,
#         nPnl=-8.0,                  # ровно по indent
#         debug_label="[EXACT_INDENT]"
#     )

#     # Ожидаем переход progress 1 -> 2
#     # volume берётся из step (т.е. grid[1])
#     expected_volume = grid[1]["volume"]

#     assert new_prog == 2, "Должен вырасти progress до 2"
#     assert almost_equal(vol, expected_volume), "Объём усреднения должен соответствовать текущему шагу"
#     print("✔ test_exact_indent_trigger OK")


# def test_deeper_loss_trigger_next():
#     """
#     LONG, уже на progress=2, indent=-16, PnL=-20 → переход 2 -> 3
#     """
#     avg = Average(DummyContext(), DummyHandler())
#     grid = make_grid()

#     new_prog, vol = avg.avg_control_func(
#         grid_orders=grid,
#         avg_progress_counter=2,
#         normalized_sign=1,
#         nPnl=-20.0,                 # убыток больше -16
#         debug_label="[DEEPER_LOSS]"
#     )

#     expected_volume = grid[2]["volume"]  # step для progress=2 → grid[2]

#     assert new_prog == 3, "progress должен стать 3"
#     assert almost_equal(vol, expected_volume), "volume должен быть с текущего шага"
#     print("✔ test_deeper_loss_trigger_next OK")


# def test_progress_limit():
#     """
#     Проверяем, что при достижении верхнего лимита сетки усреднение больше не идёт.
#     len_grid_orders = 4, progress >= 4 → стоп.
#     """
#     avg = Average(DummyContext(), DummyHandler())
#     grid = make_grid()
#     len_grid = len(grid)  # 4

#     new_prog, vol = avg.avg_control_func(
#         grid_orders=grid,
#         avg_progress_counter=len_grid,
#         normalized_sign=1,
#         nPnl=-999.0,
#         debug_label="[LIMIT]"
#     )

#     assert new_prog == len_grid, "progress не должен расти за пределами сетки"
#     assert vol == 0.0, "volume должен быть 0.0 при достижении лимита"
#     print("✔ test_progress_limit OK")


# def test_short_side_logic():
#     """
#     SHORT: normalized_sign = -1.
#     Для шорта убыток по PnL будет +X, но normalized_sign=-1 → avg_nPnl отрицательный.
#     Проверяем, что условие всё так же работает.
#     """
#     avg = Average(DummyContext(), DummyHandler())
#     grid = make_grid()

#     # допустим, по шорту +9% убытка
#     new_prog, vol = avg.avg_control_func(
#         grid_orders=grid,
#         avg_progress_counter=1,
#         normalized_sign=-1,         # SHORT
#         nPnl=9.0,                   # убыток +9% → avg_nPnl = -9
#         debug_label="[SHORT]"
#     )

#     expected_volume = grid[1]["volume"]

#     assert new_prog == 2, "Для SHORT при эквивалентном убытке должен сработать тот же шаг"
#     assert almost_equal(vol, expected_volume), "volume для SHORT аналогичен LONG"
#     print("✔ test_short_side_logic OK")


# # ------------------------------
# #   ТЕСТ check_avg_and_report
# # ------------------------------
# def test_check_avg_and_report_integration():
#     """
#     Интеграционный тест:
#     - symbol_data с progress=1
#     - settings_pos_options с grid_orders
#     - PnL такой, что должен сработать шаг 2
#     Проверяем:
#     - avg_progress_counter обновился
#     - process_volume выставлен
#     - функция вернула True
#     """
#     handler = DummyHandler()
#     ctx = DummyContext()
#     avg = Average(ctx, handler)

#     grid = make_grid()
#     settings_pos_options = {
#         "entry_conditions": {
#             "grid_orders": grid
#         }
#     }

#     symbol_data = {
#         "avg_progress_counter": 1,
#         "process_volume": 0.0
#     }

#     cur_price = 100.0
#     nPnl = -9.0        # убыток > -8 → триггер
#     normalized_sign = 1
#     debug_label = "[INTEGRATION]"

#     res = avg.check_avg_and_report(
#         cur_price=cur_price,
#         symbol_data=symbol_data,
#         nPnl=nPnl,
#         normalized_sign=normalized_sign,
#         settings_pos_options=settings_pos_options,
#         debug_label=debug_label
#     )

#     assert res is True, "Должен вернуться True при срабатывании усреднения"
#     assert symbol_data["avg_progress_counter"] == 2, "progress должен вырасти до 2"
#     assert almost_equal(symbol_data["process_volume"], grid[1]["volume"]), "process_volume должен совпасть с volume шага"
#     print("✔ test_check_avg_and_report_integration OK")


# def run_all_tests():
#     print("=== START AVG TESTS ===")
#     test_no_grid()
#     test_not_enough_loss()
#     test_exact_indent_trigger()
#     test_deeper_loss_trigger_next()
#     test_progress_limit()
#     test_short_side_logic()
#     test_check_avg_and_report_integration()
#     print("=== ALL AVG TESTS PASSED ===")


# if __name__ == "__main__":
#     run_all_tests()




"""
Эмулятор движения цены для тестирования логики усреднения.

Запуск:
    python test_avg_price_emulator.py
"""

from BUSINESS.risk_orders_control import Average

# ------------------------------
# Заглушки под контекст и логи
# ------------------------------
class DummyHandler:
    def debug_info_notes(self, msg: str, is_print: bool = False):
        if is_print:
            print("[DBG]", msg)

    def trades_info_notes(self, msg: str, is_print: bool = False):
        if is_print:
            print("[TRADE]", msg)

    def wrap_foreign_methods(self, obj):
        return


class DummyContext:
    pass


# ------------------------------
# Моковые сеточные уровни
# ------------------------------
def make_grid():
    return [
        {'indent': 0.0, 'volume': 10.52, 'signal': True},
        {'indent': -8.0, 'volume': 11.57, 'signal': False},
        {'indent': -16.0, 'volume': 12.73, 'signal': False},
        {'indent': -24.0, 'volume': 14.0,  'signal': False},
    ]


# ------------------------------
# Вспомогательная функция PnL
# ------------------------------
def pnl_percent(cur_price, entry_price):
    return ((cur_price - entry_price) / entry_price) * 100


# ------------------------------
# Эмулятор движения цены
# ------------------------------
def emulate_price_movements():
    print("=== PRICE MOVEMENT EMULATOR ===")

    handler = DummyHandler()
    ctx = DummyContext()
    avg = Average(ctx, handler)
    grid = make_grid()

    # Конфигурация как в реале
    settings_pos_options = {
        "entry_conditions": {
            "grid_orders": grid
        }
    }

    # Объект позиции
    symbol_data = {
        "avg_progress_counter": 1,
        "process_volume": 0.0
    }

    normalized_sign = 1    # LONG
    entry_price = 100.0

    # Последовательность цен для тестирования крайних сценариев
    price_path = [
        100, 99, 98, 97, 96,     # лёгкое падение
        94, 92,                  # глубокое падение → должны включиться уровни
        85,                      # резкий пробой далеко за сетку
        130,                     # резкий откат назад (должно перестать триггерить)
        120, 110, 90, 80,        # новое глубокое движение
        200, 75, 90, 75, 65, 80, 66, 62,                       # mega-откат вверх
    ]

    print("\nPATH:", price_path, "\n")
    print("STEP | PRICE | PnL% | OLD_PROG → NEW_PROG | VOLUME\n" +
          "-"*65)

    for step_i, price in enumerate(price_path):
        nPnl = pnl_percent(price, entry_price)

        old_prog = symbol_data["avg_progress_counter"]

        new_prog, volume = avg.avg_control_func(
            grid_orders=grid,
            avg_progress_counter=old_prog,
            normalized_sign=normalized_sign,
            nPnl=nPnl,
            debug_label="[EMUL]"
        )

        # Если change, обновляем как в реальной системе
        if new_prog != old_prog and volume > 0:
            symbol_data["avg_progress_counter"] = new_prog
            symbol_data["process_volume"] = volume

        print(
            f"{step_i:>4} | {price:>6.2f} | {nPnl:>6.2f}% | "
            f"{old_prog} → {symbol_data['avg_progress_counter']} | "
            f"{symbol_data['process_volume']}"
        )

    print("\n=== END EMULATOR ===\n")


if __name__ == "__main__":
    emulate_price_movements()
