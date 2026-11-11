
import argparse

from src.config import read_config, validate_config


def print_config(config):
    print("Параметры конфигурации:")

    for key, value in config.items():
        print(f"{key}: {value}")


def main():
    parser = argparse.ArgumentParser(
        description="Анализатор зависимостей Python-пакетов"
    )

    parser.add_argument(
        "--config",
        default="config.csv",
        help="Путь к CSV-файлу конфигурации"
    )

    args = parser.parse_args()

    try:
        config = read_config(args.config)
        config = validate_config(config)

        print_config(config)
        return 0

    except ValueError as error:
        print(f"Ошибка: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
