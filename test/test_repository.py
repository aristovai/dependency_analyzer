import json
import unittest
from io import BytesIO
from unittest.mock import patch

from src.repository import (
    get_direct_dependencies,
    get_package_info,
    parse_dependencies
)


class TestRepository(unittest.TestCase):
    """Тесты работы с метаданными Python-пакетов."""

    def setUp(self):
        """Создаёт пример метаданных пакета."""
        self.package_info = {
            "info": {
                "name": "example",
                "requires_dist": [
                    "requests>=2.0",
                    "numpy>=1.20",
                    "urllib3<3"
                ]
            }
        }

    def test_parse_dependencies(self):
        """Проверяет получение имён зависимостей."""
        result = parse_dependencies(self.package_info)

        self.assertEqual(
            result,
            ["numpy", "requests", "urllib3"]
        )

    def test_empty_dependencies(self):
        """Проверяет пакет без зависимостей."""
        self.package_info["info"]["requires_dist"] = []

        result = parse_dependencies(self.package_info)

        self.assertEqual(result, [])

    def test_null_dependencies(self):
        """Проверяет отсутствие списка зависимостей."""
        self.package_info["info"]["requires_dist"] = None

        result = parse_dependencies(self.package_info)

        self.assertEqual(result, [])

    def test_duplicate_dependencies(self):
        """Проверяет удаление повторяющихся зависимостей."""
        self.package_info["info"]["requires_dist"] = [
            "requests>=2.0",
            "requests<3",
            "numpy>=1.20"
        ]

        result = parse_dependencies(self.package_info)

        self.assertEqual(result, ["numpy", "requests"])

    def test_extra_dependencies(self):
        """Проверяет зависимости с дополнительными условиями."""
        self.package_info["info"]["requires_dist"] = [
            "requests>=2.0",
            'pytest>=7; extra == "test"'
        ]

        result = parse_dependencies(self.package_info)

        self.assertEqual(result, ["pytest", "requests"])

    def test_missing_info(self):
        """Проверяет отсутствие поля info."""
        with self.assertRaises(ValueError):
            parse_dependencies({})

    def test_wrong_requirements(self):
        """Проверяет неверный тип поля requires_dist."""
        self.package_info["info"]["requires_dist"] = "requests"

        with self.assertRaises(ValueError):
            parse_dependencies(self.package_info)

    def test_wrong_requirement_item(self):
        """Проверяет неверный тип отдельной зависимости."""
        self.package_info["info"]["requires_dist"] = [123]

        with self.assertRaises(ValueError):
            parse_dependencies(self.package_info)

    @patch("src.repository.urlopen")
    def test_get_package_info(self, mock_urlopen):
        """Проверяет получение JSON из репозитория."""
        response = json.dumps(self.package_info).encode("utf-8")

        mock_urlopen.return_value.__enter__.return_value = (
            BytesIO(response)
        )

        result = get_package_info(
            "https://pypi.org",
            "example"
        )

        self.assertEqual(result, self.package_info)

    @patch("src.repository.get_package_info")
    def test_get_direct_dependencies(self, mock_get_info):
        """Проверяет получение прямых зависимостей."""
        mock_get_info.return_value = self.package_info

        result = get_direct_dependencies(
            "https://pypi.org",
            "example"
        )

        self.assertEqual(
            result,
            ["numpy", "requests", "urllib3"]
        )

    @patch("src.repository.urlopen")
    def test_invalid_json(self, mock_urlopen):
        """Проверяет обработку неправильного JSON."""
        mock_urlopen.return_value.__enter__.return_value = (
            BytesIO(b"invalid json")
        )

        with self.assertRaises(ValueError):
            get_package_info("https://pypi.org", "example")

    @patch("src.repository.urlopen")
    def test_http_error(self, mock_urlopen):
        """Проверяет обработку ошибки HTTP."""
        from urllib.error import HTTPError

        mock_urlopen.side_effect = HTTPError(
            "https://pypi.org",
            404,
            "Not Found",
            None,
            None
        )

        with self.assertRaises(ValueError):
            get_package_info("https://pypi.org", "unknown")

    @patch("src.repository.urlopen")
    def test_connection_error(self, mock_urlopen):
        """Проверяет обработку ошибки подключения."""
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError(
            "Connection failed"
        )

        with self.assertRaises(ValueError):
            get_package_info("https://pypi.org", "example")


if __name__ == "__main__":
    unittest.main()
