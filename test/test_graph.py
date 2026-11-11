import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.graph import build_graph, read_test_repository


class TestGraph(unittest.TestCase):
    """Проверяет построение и обработку графов."""

    def setUp(self):
        """Создаёт тестовый граф и конфигурацию."""
        self.graph = {
            "A": ["B", "C"],
            "B": ["D", "E"],
            "C": ["F"],
            "D": [],
            "E": ["F"],
            "F": []
        }

        self.config = {
            "package_name": "A",
            "repository": "test_repository.csv",
            "test_mode": True,
            "output_file": "graph.svg",
            "max_depth": 5,
            "filter_substring": ""
        }

    def test_full_graph(self):
        """Проверяет построение полного графа."""
        result = build_graph(self.config, self.graph)

        self.assertEqual(result, self.graph)

    def test_max_depth_zero(self):
        """Проверяет нулевую глубину."""
        self.config["max_depth"] = 0

        result = build_graph(self.config, self.graph)

        self.assertEqual(result, {"A": []})

    def test_max_depth_one(self):
        """Проверяет ограничение глубины до одного."""
        self.config["max_depth"] = 1

        result = build_graph(self.config, self.graph)

        self.assertEqual(result["A"], ["B", "C"])
        self.assertEqual(result["B"], [])
        self.assertEqual(result["C"], [])
        self.assertNotIn("D", result)

    def test_filter(self):
        """Проверяет исключение пакетов по подстроке."""
        self.config["filter_substring"] = "B"

        result = build_graph(self.config, self.graph)

        self.assertNotIn("B", result)
        self.assertEqual(result["A"], ["C"])
        self.assertNotIn("D", result)

    def test_cycle(self):
        """Проверяет обработку циклических зависимостей."""
        self.graph["F"] = ["A"]

        result = build_graph(self.config, self.graph)

        self.assertEqual(result["F"], ["A"])
        self.assertIn("A", result)

    def test_self_cycle(self):
        """Проверяет зависимость пакета от самого себя."""
        self.graph["A"] = ["A"]

        result = build_graph(self.config, self.graph)

        self.assertEqual(result, {"A": ["A"]})

    def test_unknown_package(self):
        """Проверяет отсутствие начального пакета."""
        self.config["package_name"] = "Z"

        with self.assertRaises(ValueError):
            build_graph(self.config, self.graph)

    def test_shorter_path(self):
        """Проверяет повторный обход по более короткому пути."""
        self.graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["E"],
            "D": ["E"],
            "E": ["F"],
            "F": []
        }

        self.config["max_depth"] = 3

        result = build_graph(self.config, self.graph)

        self.assertIn("F", result)
        self.assertEqual(result["E"], ["F"])

    def test_duplicate_dependencies(self):
        """Проверяет удаление повторяющихся рёбер."""
        self.graph["A"] = ["B", "B", "C"]

        result = build_graph(self.config, self.graph)

        self.assertEqual(result["A"], ["B", "C"])

    @patch("src.graph.get_direct_dependencies")
    def test_real_repository(self, mock_dependencies):
        """Проверяет обход с имитацией реального репозитория."""
        self.config["test_mode"] = False

        mock_dependencies.side_effect = lambda repo, package: (
            self.graph[package]
        )

        result = build_graph(self.config)

        self.assertEqual(result, self.graph)
        self.assertTrue(mock_dependencies.called)


class TestRepositoryFile(unittest.TestCase):
    """Проверяет чтение тестового репозитория."""

    def setUp(self):
        """Создаёт временный CSV-файл."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.filename = Path(self.temp_dir.name) / "repository.csv"

    def save_rows(self, rows):
        """Записывает строки в тестовый CSV.

        Args:
            rows: Список строк CSV.
        """
        with open(self.filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    def test_correct_file(self):
        """Проверяет чтение правильного файла."""
        self.save_rows([
            ["package", "dependencies"],
            ["A", "B C"],
            ["B", ""],
            ["C", ""]
        ])

        result = read_test_repository(self.filename)

        self.assertEqual(result["A"], ["B", "C"])

    def test_wrong_header(self):
        """Проверяет неправильный заголовок."""
        self.save_rows([
            ["name", "dependencies"],
            ["A", "B"]
        ])

        with self.assertRaises(ValueError):
            read_test_repository(self.filename)

    def test_wrong_package_name(self):
        """Проверяет недопустимое имя пакета."""
        self.save_rows([
            ["package", "dependencies"],
            ["A1", ""]
        ])

        with self.assertRaises(ValueError):
            read_test_repository(self.filename)

    def test_unknown_dependency(self):
        """Проверяет ссылку на неизвестный пакет."""
        self.save_rows([
            ["package", "dependencies"],
            ["A", "B"]
        ])

        with self.assertRaises(ValueError):
            read_test_repository(self.filename)

    def test_duplicate_package(self):
        """Проверяет повторное описание пакета."""
        self.save_rows([
            ["package", "dependencies"],
            ["A", ""],
            ["A", ""]
        ])

        with self.assertRaises(ValueError):
            read_test_repository(self.filename)

    def test_missing_file(self):
        """Проверяет отсутствие файла репозитория."""
        with self.assertRaises(ValueError):
            read_test_repository("missing_repository.csv")


if __name__ == "__main__":
    unittest.main()
