import csv
import re

from src.repository import get_direct_dependencies


def read_test_repository(filename):
    """Читает тестовый репозиторий из CSV-файла.

    Args:
        filename: Путь к тестовому файлу.

    Returns:
        Словарь с зависимостями пакетов.

    Raises:
        ValueError: Если тестовый файл некорректен.
    """
    graph = {}

    try:
        with open(filename, encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file)

            if next(reader, None) != ["package", "dependencies"]:
                raise ValueError("Неверный заголовок тестового CSV")

            for row in reader:
                if len(row) != 2:
                    raise ValueError("Неверная строка тестового CSV")

                package = row[0].strip()
                dependencies = row[1].split()

                if not re.fullmatch(r"[A-Z]+", package):
                    raise ValueError("Неверное имя тестового пакета")

                if package in graph:
                    raise ValueError("Повтор пакета в тестовом файле")

                for dependency in dependencies:
                    if not re.fullmatch(r"[A-Z]+", dependency):
                        raise ValueError("Неверное имя зависимости")

                graph[package] = dependencies

    except OSError as error:
        raise ValueError(
            f"Ошибка чтения тестового репозитория: {error}"
        ) from error

    for dependencies in graph.values():
        for dependency in dependencies:
            if dependency not in graph:
                raise ValueError(
                    f"Неизвестный пакет: {dependency}"
                )

    return graph


def get_dependencies(package, config, test_graph=None):
    """Получает прямые зависимости одного пакета.

    Args:
        package: Имя пакета.
        config: Параметры конфигурации.
        test_graph: Словарь тестовых зависимостей.

    Returns:
        Список прямых зависимостей.

    Raises:
        ValueError: Если пакет отсутствует.
    """
    if config["test_mode"]:
        if test_graph is None or package not in test_graph:
            raise ValueError(f"Пакет {package} не найден")

        return test_graph[package]

    return get_direct_dependencies(
        config["repository"],
        package
    )


def build_graph(config, test_graph=None):
    """Строит граф зависимостей алгоритмом DFS без рекурсии.

    Args:
        config: Параметры конфигурации.
        test_graph: Тестовый репозиторий или None.

    Returns:
        Словарь с найденными зависимостями.
    """
    start = config["package_name"]
    max_depth = config["max_depth"]
    substring = config["filter_substring"].lower()

    graph = {}
    best_depth = {}
    stack = [(start, 0)]

    while stack:
        package, depth = stack.pop()

        if substring and substring in package.lower():
            continue

        if depth >= best_depth.get(package, float("inf")):
            continue

        best_depth[package] = depth
        graph.setdefault(package, [])

        if depth >= max_depth:
            continue

        dependencies = get_dependencies(
            package, config, test_graph
        )

        filtered = [
            name for name in dependencies
            if not substring or substring not in name.lower()
        ]

        graph[package] = list(dict.fromkeys(filtered))

        for name in reversed(graph[package]):
            if depth + 1 < best_depth.get(name, float("inf")):
                stack.append((name, depth + 1))

    return graph


def print_graph(graph):
    """Выводит граф зависимостей на экран.

    Args:
        graph: Словарь зависимостей пакетов.
    """
    print("\nГраф зависимостей:")

    for package, dependencies in graph.items():
        if dependencies:
            print(f"{package}: {', '.join(dependencies)}")
        else:
            print(f"{package}: нет зависимостей")
