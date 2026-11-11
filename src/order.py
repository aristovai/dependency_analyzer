import heapq


def get_load_order(graph):
    """Определяет порядок загрузки пакетов.

    Args:
        graph: Словарь с зависимостями пакетов.

    Returns:
        Список пакетов в порядке загрузки.

    Raises:
        ValueError: Если граф содержит цикл или ошибку.
    """
    remaining = {}
    dependents = {}

    for package in graph:
        remaining[package] = 0
        dependents[package] = []

    for package, dependencies in graph.items():
        for dependency in set(dependencies):
            if dependency not in graph:
                raise ValueError(
                    f"Неизвестная зависимость: {dependency}"
                )

            remaining[package] += 1
            dependents[dependency].append(package)

    queue = []

    for package, count in remaining.items():
        if count == 0:
            heapq.heappush(queue, package)

    order = []

    while queue:
        package = heapq.heappop(queue)
        order.append(package)

        for dependent in dependents[package]:
            remaining[dependent] -= 1

            if remaining[dependent] == 0:
                heapq.heappush(queue, dependent)

    if len(order) != len(graph):
        raise ValueError(
            "Невозможно определить порядок: найден цикл"
        )

    return order


def print_load_order(order):
    """Выводит порядок загрузки пакетов.

    Args:
        order: Список пакетов в порядке загрузки.
    """
    print("\nПорядок загрузки зависимостей:")

    for number, package in enumerate(order, start=1):
        print(f"{number}. {package}")
