import asyncio
import random
from typing import Optional

from MANAGERS.online import WS_HotPrice_Stream
from b_context import BotContext
from c_log import ErrorHandler
from c_utils import get_proxy_list


# ============================================================
#  ЛОГГЕР
# ============================================================
class DummyLogger(ErrorHandler):
    def debug_error_notes(self, msg, *args, **kwargs):
        print(msg)

    def debug_info_notes(self, msg, *args, **kwargs):
        print(msg)


# ============================================================
#  CONTEXT
# ============================================================
class DummyContext(BotContext):
    def __init__(self):
        super().__init__()
        self.ws_price_data = {}


# ============================================================
#  "ПОРЧА" ПРОКСИ
# ============================================================
def break_proxy_url(url: Optional[str]) -> Optional[str]:
    if url is None:
        return None
    return "http://0.0.0.0:9999"


# ============================================================
#  ТЕСТ WS с прокси-циклом
# ============================================================
async def ws_proxy_test_loop():

    print("\n========== WS ПРОКСИ-ПЕРЕКЛЮЧЕНИЕ (БОЕВОЙ ТЕСТ) ==========\n")

    base_cfg = [
        {
            "enable": True,
            "proxy_address": '154.222.214.132',
            "proxy_port": '62890',
            "proxy_login": '1FDJcwJR',
            "proxy_password": 'U2yrFg4a'
        },
        {
            "enable": True,
            "proxy_address": '154.218.20.43',
            "proxy_port": '64630',
            "proxy_login": '1FDJcwJR',
            "proxy_password": 'U2yrFg4a'
        },
        {
            "enable": True,
            "proxy_address": '45.192.135.214',
            "proxy_port": '59100',
            "proxy_login": 'nikolassmsttt0Icgm',
            "proxy_password": 'agrYpvDz7D'
        },
        None
    ]

    # БАЗОВЫЙ ЭТАЛОННЫЙ СПИСОК (не трогаем!)
    original_list = get_proxy_list(base_cfg)

    logger = DummyLogger()
    ctx = DummyContext()

    # Стример получает СОБСТВЕННУЮ копию списка
    ws = WS_HotPrice_Stream(
        context=ctx,
        error_handler=logger,
        proxy_list=original_list.copy()
    )

    await ws.sync_ws_streams(["BTCUSDT"])
    await asyncio.sleep(4)

    idx = 0

    while True:

        print("\n---------------------------------------------------------")
        print(f"[WS-TEST] ТЕСТ ПРОКСИ #{idx}")
        print(f"[WS-TEST] ОРИГИНАЛ proxy = {original_list[idx]}")
        print(f"[WS-TEST] WS proxy_list[{idx}] = {ws.proxy_list[idx]}")
        print("---------------------------------------------------------")

        await asyncio.sleep(4)

        # ===== 1) проверка работоспособности =====
        if ws.is_connected:
            print(f"[WS-TEST] ✓ Подключение OK через {ws.proxy_url}")
        else:
            print(f"[WS-TEST] ❌ Нет подключения! last_error = {ws.last_error}")

        # ===== 2) Ждём =====
        delay = random.randint(4, 8)
        print(f"[WS-TEST] Ждём {delay} сек перед порчей...")
        await asyncio.sleep(delay)

        # ===== 3) ПОРТИТЬ ТОЛЬКО ВНУТРЕННИЙ СПИСОК =====
        print("[WS-TEST] ⚠ ПОРЧУ текущий прокси...")
        ws.proxy_list[idx] = break_proxy_url(ws.proxy_list[idx])

        # ===== 4) Закрыть WS, чтобы вызвать реконнект =====
        if ws.websocket:
            print("[WS-TEST] Закрываю WebSocket (форсируем reconnect)...")
            await ws.websocket.close()

        # ===== 5) Ждать реконнекта =====
        wait_time = random.randint(5, 10)
        print(f"[WS-TEST] Ждём {wait_time} сек для reconnect...")
        await asyncio.sleep(wait_time)

        # ===== 6) Вывод состояния =====
        print(f"[WS-TEST] Результат reconnect:")
        print(f"    is_connected = {ws.is_connected}")
        print(f"    last_connect_status = {ws.last_connect_status}")
        print(f"    proxy_url = {ws.proxy_url}")
        print(f"    last_error = {ws.last_error}")

        # ===== 7) ПЕРЕХОД К СЛЕДУЮЩЕМУ =====
        idx = (idx + 1) % len(original_list)

        # ===== 8) ВОССТАНОВИТЬ ОРИГИНАЛЬНЫЕ ПРОКСИ ДЛЯ СТРИМЕРА =====
        # чтобы каждый цикл начался корректно
        if idx == 0:
            ws.proxy_list = original_list.copy()
            print("[WS-TEST] 🔄 Полное восстановление proxy_list стримера")


if __name__ == "__main__":
    try:
        asyncio.run(ws_proxy_test_loop())
    except KeyboardInterrupt:
        print("\nWS тест остановлен пользователем.")
