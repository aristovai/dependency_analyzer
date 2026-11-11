import json


def read_pip_report(filename):
    """Читает список пакетов из отчёта pip.

    Args:
        filename: Путь к JSON-отчёту pip.

    Returns:
        Отсортированный список имён пакетов.
    """
    with open(filename, encoding="utf-8") as file:
        report = json.load(file)

    packages = []

    for item in report["install"]:
        name = item["metadata"]["name"]
        packages.append(name)

    return sorted(packages, key=str.lower)


def main():
    packages = read_pip_report("pip_report.json")

    print("Пакеты, выбранные pip для установки:")

    for package in packages:
        print(package)


if __name__ == "__main__":
    main()
