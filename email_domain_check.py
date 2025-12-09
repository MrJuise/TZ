"""
README — инструкция по запуску
------------------------------

1) Установка зависимости:
       pip install dnspython

2) Запуск со списком email-адресов:
       python3 email_domain_check.py user@gmail.com test@domain.xyz

3) Запуск с файлом (по одному email на строку):
       python3 email_domain_check.py --file emails.txt

4) Запрос помощи:
       python3 email_domain_check.py -h

5) Опциональный вывод в файл:
       python3 email_domain_check.py --file emails.txt --output result.txt

Описание:
Скрипт проверяет домены email-адресов:
- «домен валиден» — MX-записи найдены
- «домен отсутствует» — домен не существует
- «MX-записи отсутствуют или некорректны» — нет MX

Архитектура:
- Легко менять источник входа (stdin, файл, аргументы)
- Есть логирование ошибок
- Есть таймаут для DNS-запросов
"""

import argparse
import logging
import sys
import dns.resolver

# --------------------------------------------------------------
# Настройка логирования
# --------------------------------------------------------------
logging.basicConfig(
    level=logging.ERROR,
    format="[%(levelname)s] %(message)s"
)

# --------------------------------------------------------------
# Проверка MX-записей
# --------------------------------------------------------------
def check_domain(domain: str) -> str:
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2
    resolver.lifetime = 2

    try:
        answers = resolver.resolve(domain, "MX")
        if answers:
            return "домен валиден"
        return "MX-записи отсутствуют или некорректны"
    except dns.resolver.NXDOMAIN:
        return "домен отсутствует"
    except dns.resolver.NoAnswer:
        return "MX-записи отсутствуют или некорректны"
    except dns.exception.Timeout:
        logging.error(f"Таймаут при проверке домена: {domain}")
        return "ошибка проверки (таймаут)"
    except Exception as e:
        logging.error(f"Ошибка при проверке {domain}: {e}")
        return "неизвестная ошибка"


# --------------------------------------------------------------
# Чтение email адресов
# --------------------------------------------------------------
def load_emails(args) -> list[str]:
    emails = []

    # Из файла
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                emails = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logging.error(f"Ошибка при чтении файла: {e}")
            sys.exit(1)

    # Из аргументов
    if args.emails:
        emails.extend(args.emails)

    # На будущее можно добавить stdin
    # if not emails and not sys.stdin.isatty():
    #     emails = [line.strip() for line in sys.stdin if line.strip()]

    return emails


# --------------------------------------------------------------
# Основной блок
# --------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Проверка доменов email на наличие MX-записей."
    )
    parser.add_argument("emails", nargs="*", help="email-адреса")
    parser.add_argument("--file", "-f", help="файл со списком email")
    parser.add_argument("--output", "-o", help="файл вывода результатов")

    args = parser.parse_args()
    emails = load_emails(args)

    if not emails:
        print("Нет email-адресов для проверки. Используйте аргументы или --file.")
        return

    results = []

    for email in emails:
        if "@" not in email:
            results.append(f"{email}: некорректный email")
            continue

        domain = email.split("@")[1]
        status = check_domain(domain)
        results.append(f"{email}: {status}")

    # Вывод в stdout
    for line in results:
        print(line)

    # Опциональный вывод в файл
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write("\n".join(results))
        except Exception as e:
            logging.error(f"Ошибка записи в файл: {e}")


if __name__ == "__main__":
    main()