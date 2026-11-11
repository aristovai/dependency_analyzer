import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


def get_package_info(repository, package_name):
    """Получает информацию о пакете из репозитория.

    Args:
        repository: URL репозитория.
        package_name: Имя Python-пакета.

    Returns:
        Словарь с метаданными пакета.

    Raises:
        ValueError: Если запрос завершился ошибкой.
    """
    url = urlparse(repository)

    if url.scheme not in ("http", "https") or not url.netloc:
        raise ValueError("Некорректный URL репозитория")

    address = (
        f"{repository.rstrip('/')}/pypi/"
        f"{quote(package_name, safe='')}/json"
    )

    request = Request(
        address,
        headers={"Accept": "application/json"}
    )

    try:
        with urlopen(request, timeout=10) as response:
            data = json.load(response)

    except HTTPError as error:
        raise ValueError(
            f"Ошибка HTTP: {error.code}"
        ) from error

    except (URLError, TimeoutError, OSError) as error:
        raise ValueError(
            f"Ошибка подключения: {error}"
        ) from error

    except (ValueError, UnicodeError) as error:
        raise ValueError(
            "Ошибка чтения JSON"
        ) from error

    if not isinstance(data, dict):
        raise ValueError("Неверный формат ответа репозитория")

    return data


def parse_dependencies(package_info):
    """Извлекает имена прямых зависимостей пакета.

    Args:
        package_info: Метаданные пакета.

    Returns:
        Отсортированный список имён зависимостей.

    Raises:
        ValueError: Если метаданные имеют неверный формат.
    """
    info = package_info.get("info")

    if not isinstance(info, dict):
        raise ValueError("В ответе отсутствует поле info")

    requirements = info.get("requires_dist")

    if requirements is None:
        return []

    if not isinstance(requirements, list):
        raise ValueError("Поле requires_dist должно быть списком")

    dependencies = set()
    pattern = r"^\s*([A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*)"

    for requirement in requirements:
        if not isinstance(requirement, str):
            raise ValueError("Неверная запись зависимости")

        match = re.match(pattern, requirement)

        if match is None:
            raise ValueError("Не удалось прочитать зависимость")

        dependencies.add(match.group(1))

    return sorted(dependencies, key=str.lower)


def get_direct_dependencies(repository, package_name):
    """Получает список прямых зависимостей пакета.

    Args:
        repository: URL репозитория.
        package_name: Имя анализируемого пакета.

    Returns:
        Список имён прямых зависимостей.
    """
    package_info = get_package_info(repository, package_name)

    return parse_dependencies(package_info)
