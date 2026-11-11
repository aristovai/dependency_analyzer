import csv
import re
from pathlib import Path
from urllib.parse import urlparse


REQUIRED_KEYS = [
    "package_name",
    "repository",
    "test_mode",
    "output_file",
    "max_depth",
    "filter_substring"
]


def read_config(filename):
    """Читает конфигурацию из CSV-файла.

    Args:
        filename: Путь к файлу конфигурации.

    Returns:
        Словарь с параметрами конфигурации.

    Raises:
        ValueError: Если файл содержит ошибки.
    """
    config = {}

    try:
        with open(filename, "r", encoding="utf-8-sig") as file:
            reader = csv.reader(file)
            header = next(reader, None)

            if header != ["key", "value"]:
                raise ValueError("Неверный заголовок CSV")

            for row in reader:
                if len(row) != 2:
                    raise ValueError("Неверный формат строки CSV")

                key = row[0].strip()
                value = row[1].strip()

                if key not in REQUIRED_KEYS:
                    raise ValueError(f"Неизвестный параметр: {key}")

                if key in config:
                    raise ValueError(f"Повтор параметра: {key}")

                config[key] = value

    except OSError as error:
        raise ValueError(f"Ошибка чтения файла: {error}") from error

    return config


def check_package_name(name):
    """Проверяет имя Python-пакета.

    Args:
        name: Имя пакета.

    Raises:
        ValueError: Если имя пакета некорректно.
    """
    pattern = r"[A-Za-z0-9]+([._-][A-Za-z0-9]+)*"

    if not re.fullmatch(pattern, name):
        raise ValueError("Некорректное имя пакета")


def check_repository(repository, test_mode):
    """Проверяет адрес репозитория или путь к файлу.

    Args:
        repository: URL или путь к файлу.
        test_mode: Режим тестирования.

    Raises:
        ValueError: Если адрес или путь некорректен.
    """
    if not repository:
        raise ValueError("Репозиторий не указан")

    if test_mode:
        if not Path(repository).is_file():
            raise ValueError("Файл тестового репозитория не найден")
    else:
        url = urlparse(repository)

        if url.scheme not in ("http", "https") or not url.netloc:
            raise ValueError("Некорректный URL репозитория")


def check_output_file(filename):
    """Проверяет имя файла для изображения графа.

    Args:
        filename: Имя выходного файла.

    Raises:
        ValueError: Если имя файла некорректно.
    """
    if not filename:
        raise ValueError("Не указано имя выходного файла")

    if Path(filename).name != filename:
        raise ValueError("Нужно указать только имя файла")

    if not filename.lower().endswith(".svg"):
        raise ValueError("Файл изображения должен иметь формат SVG")


def check_max_depth(value):
    """Проверяет максимальную глубину анализа.

    Args:
        value: Значение глубины из CSV.

    Returns:
        Целое неотрицательное число.

    Raises:
        ValueError: Если глубина некорректна.
    """
    try:
        depth = int(value)
    except ValueError as error:
        raise ValueError("Глубина должна быть целым числом") from error

    if depth < 0:
        raise ValueError("Глубина не может быть отрицательной")

    return depth


def check_filter_substring(value):
    """Проверяет подстроку для фильтрации пакетов.

    Args:
        value: Подстрока из конфигурации.

    Raises:
        ValueError: Если подстрока некорректна.
    """
    if "\n" in value or "\r" in value:
        raise ValueError("Подстрока не должна содержать переносы строк")


def validate_config(config):
    """Проверяет все параметры конфигурации.

    Args:
        config: Словарь параметров.

    Returns:
        Словарь с проверенными значениями.

    Raises:
        ValueError: Если параметры некорректны.
    """
    for key in REQUIRED_KEYS:
        if key not in config:
            raise ValueError(f"Отсутствует параметр: {key}")

    check_package_name(config["package_name"])

    mode = config["test_mode"].lower()

    if mode not in ("true", "false"):
        raise ValueError("test_mode должен быть true или false")

    config["test_mode"] = mode == "true"

    check_repository(config["repository"], config["test_mode"])
    check_output_file(config["output_file"])

    config["max_depth"] = check_max_depth(config["max_depth"])

    check_filter_substring(config["filter_substring"])

    return config
