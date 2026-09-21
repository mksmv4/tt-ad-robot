#!/usr/bin/env python3
"""Замер скорости интернета: десять последовательных скачиваний одного адреса."""

import argparse
import sys
import time
import urllib.error
import urllib.request

REQUESTS = 10
CHUNK = 64 * 1024
TIMEOUT = 30
MEGABYTE = 1_000_000  # мегабайт как 10^6 байт — единица, в которой считают скорость канала
USER_AGENT = "speedtest.py/1.0"  # часть хранилищ (Wikimedia) отвечает 403 на Python-urllib


def download(url: str) -> tuple[float, int]:
    """Одно скачивание: время от запроса до последнего байта и объём принятого тела."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    size = 0
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        while chunk := response.read(CHUNK):
            size += len(chunk)
    return time.perf_counter() - started, size


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Замер скорости интернета: %d последовательных скачиваний указанного адреса." % REQUESTS,
    )
    parser.add_argument("url", nargs="?", help="адрес файла, например тяжёлой картинки")
    url = parser.parse_args().url
    if not url:
        sys.exit("Укажите адрес: python3 speedtest.py https://example.com/image.jpg")

    print(f"Адрес: {url}")
    print(f"Запросов: {REQUESTS}\n")

    times: list[float] = []
    total_size = 0
    number = 0
    try:
        for number in range(1, REQUESTS + 1):
            elapsed, size = download(url)
            times.append(elapsed)
            total_size += size
            print(
                f"  {number:2}/{REQUESTS}  {elapsed:6.2f} с  "
                f"{size / MEGABYTE:8.2f} МБ  {size / MEGABYTE / elapsed:7.2f} МБ/с"
            )
    except urllib.error.HTTPError as error:
        sys.exit(f"Запрос {number}: сервер ответил {error.code} {error.reason}")
    except urllib.error.URLError as error:
        sys.exit(f"Запрос {number}: не удалось соединиться — {error.reason}")
    except TimeoutError:
        sys.exit(f"Запрос {number}: ответ не пришёл за {TIMEOUT} с")
    except ValueError:
        sys.exit("Адрес должен начинаться с http:// или https://")
    except KeyboardInterrupt:
        sys.exit("\nПрервано")

    total_time = sum(times)
    speed = total_size / MEGABYTE / total_time

    print(f"\nСреднее время запроса: {total_time / REQUESTS:.2f} с")
    print(f"Скачано: {total_size / MEGABYTE:.2f} МБ ({total_size} байт)")
    print(f"Скорость: {speed:.2f} МБ/с ({speed * 8:.2f} Мбит/с)")


if __name__ == "__main__":
    main()
