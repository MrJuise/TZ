#!/usr/bin/env python3
"""
README (инструкция):

1) Получите токен бота:
      - Откройте @BotFather
      - Создайте бота → получите TOKEN

2) Узнайте chat_id:
      - Напишите что-либо боту @userinfobot
      - Возьмите поле "id"

3) Установите зависимости:
      pip install requests

4) Запуск:
      python send_to_telegram.py --file text.txt --token YOUR_TOKEN --chat_id CHAT_ID

Параметры:
- Текст берётся из .txt файла
- Сообщения автоматически разбиваются на части, если длина > 4096 символов
- В консоль выводится статус (успех / ошибка)
- Можно легко поменять:
      • путь к файлу
      • токен бота
      • chat_id
      через аргументы или переменные окружения
"""

import argparse
import os
import requests


TELEGRAM_API_URL = "https://api.telegram.org/bot{}/sendMessage"
MAX_LEN = 4096


def read_text(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def split_message(text, limit=MAX_LEN):
    return [text[i:i + limit] for i in range(0, len(text), limit)]


def send_message(token, chat_id, text):
    url = TELEGRAM_API_URL.format(token)

    for chunk in split_message(text):
        r = requests.post(url, data={"chat_id": chat_id, "text": chunk})

        if r.status_code != 200 or not r.json().get("ok"):
            raise RuntimeError(f"Ошибка Telegram API: {r.text}")


def main():
    parser = argparse.ArgumentParser(description="Отправка .txt файла в Telegram-чат")
    parser.add_argument("--file", required=True, help="Путь к .txt файлу")
    parser.add_argument("--token", help="Токен Telegram-бота")
    parser.add_argument("--chat_id", help="ID чата")
    args = parser.parse_args()

    token = args.token or os.getenv("TG_BOT_TOKEN")
    chat_id = args.chat_id or os.getenv("TG_CHAT_ID")

    if not token or not chat_id:
        print("Ошибка: требуется токен (--token) и chat_id (--chat_id).")
        return

    try:
        text = read_text(args.file)
        send_message(token, chat_id, text)
        print("Успех: сообщение отправлено.")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
