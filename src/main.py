import argparse

from src.config import read_config, validate_config
from src.repository import get_direct_dependencies


def print_config(config):
    """Выводит параметры конфигурации.

    Args:
        config: Словарь с параметрами программы.
    """
    print("Параметры конфигурации:")

    for key, value in config.items():
        print(f"{key}: {value}")


def print_dependencies(package_name, dependencies):
    """Выводит прямые зависимости пакета.

    Args:
        package_name: Имя анализируемого пакета.
        dependencies: Список прямых зависимостей.
    """
    print(f"\nПрямые зависимости пакета {package_name}:")

    if not dependencies:
        print("Зависимости не найдены")
        return

    for dependency in dependencies:
        print(f"- {dependency}")


def main():
    """Запускает программу анализа зависимостей.

    Returns:
        Код завершения программы.
    """
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

        if config["test_mode"]:
            print("\nТестовый режим будет реализован на этапе 3")
            return 0

        dependencies = get_direct_dependencies(
            config["repository"],
            config["package_name"]
        )

        print_dependencies(config["package_name"], dependencies)

        return 0

    except ValueError as error:
        print(f"Ошибка: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
