# test_proxy_switcher.py

import asyncio
import random

from z_test import NetworkManager, PROXY_LIST, get_proxy_list
from c_log import ErrorHandler


class DummyLogger(ErrorHandler):
    """Простой логгер вместо ErrorHandler."""
    def debug_error_notes(self, msg, *args, **kwargs):
        print(msg)


def break_proxy_url(url: str) -> str:
    """
    Делает из нормального proxy_url заведомо битый.
    Не парсим логин/пароль, просто отправляем на 0.0.0.0:9999.
    """
    return "http://0.0.0.0:9999"


async def proxy_test_loop():
    print("\n========== ТЕСТ ПРОКСИ-ПЕРЕКЛЮЧЕНИЙ ==========\n")

    # из твоего PROXY_LIST делаем список URL + None, уникальные
    proxy_urls = get_proxy_list(PROXY_LIST)

    logger = DummyLogger()

    manager = NetworkManager(
        info_handler=logger,
        proxy_list=proxy_urls,
        user_label="TEST_PROXY_ROTATION"
    )

    await manager.initialize_session()

    idx = 0

    while True:
        url = proxy_urls[idx]

        print(f"\n[TEST] Прокси #{idx}")
        print(f"[TEST] URL: {url}")

        print("[TEST] Проверка соединения (до поломки)...")
        ok, rec, status = await manager.validate_session()

        if ok:
            print(f"[TEST] ✓ Успех. status={status}")
        else:
            print(f"[TEST] ❌ FAIL. status={status}")

        delay = random.randint(10, 15)
        print(f"[TEST] Ждём {delay} сек...")
        await asyncio.sleep(delay)

        # ломаем текущий proxy_url, если он не None
        if url is not None:
            print(f"[TEST] ⚠ Порчу proxy_url для #{idx}")
            broken = break_proxy_url(url)
            proxy_urls[idx] = broken
            manager.proxy_list[idx] = broken
            manager.proxy_index = idx
            manager.proxy_url = broken

            # закрываем текущую сессию, чтобы следующая validate создала сессию уже с битым прокси
            if manager.session and not manager.session.closed:
                await manager.session.close()
                manager.session = None
        else:
            print(f"[TEST] ⚠ Ломать нечего: локальное соединение (None)")

        print("[TEST] 🔄 validate_session() после поломки...")
        ok, rec, status = await manager.validate_session()

        if ok:
            print(f"[TEST] ✓ После поломки удалось переключиться, итоговый status={status}")
        else:
            print(f"[TEST] ❌ После поломки не найден рабочий прокси, last_status={status}")

        idx = (idx + 1) % len(proxy_urls)
        print("------------------------------------------")


if __name__ == "__main__":
    try:
        asyncio.run(proxy_test_loop())
    except KeyboardInterrupt:
        print("\nТест остановлен пользователем")
