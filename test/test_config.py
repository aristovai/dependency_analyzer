import csv
import tempfile
import unittest
from pathlib import Path

from src.config import read_config, validate_config


class TestConfig(unittest.TestCase):
    """Тесты чтения и проверки конфигурации."""

    def setUp(self):
        """Создаёт временный каталог и правильную конфигурацию."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.filename = Path(self.temp_dir.name) / "config.csv"

        self.config = {
            "package_name": "requests",
            "repository": "https://pypi.org",
            "test_mode": "false",
            "output_file": "graph.svg",
            "max_depth": "3",
            "filter_substring": "dev"
        }

    def save_config(self):
        """Записывает текущие параметры в CSV-файл."""
        with open(self.filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["key", "value"])

            for key, value in self.config.items():
                writer.writerow([key, value])

    def test_correct_config(self):
        """Проверяет правильную конфигурацию."""
        self.save_config()

        config = read_config(self.filename)
        result = validate_config(config)

        self.assertEqual(result["package_name"], "requests")
        self.assertEqual(result["max_depth"], 3)
        self.assertFalse(result["test_mode"])

    def test_wrong_package_name(self):
        """Проверяет ошибку в имени пакета."""
        self.config["package_name"] = "bad package!"
        self.save_config()

        with self.assertRaises(ValueError):
            validate_config(read_config(self.filename))

    def test_wrong_repository(self):
        """Проверяет ошибку URL репозитория."""
        self.config["repository"] = "wrong_address"
        self.save_config()

        with self.assertRaises(ValueError):
            validate_config(read_config(self.filename))

    def test_wrong_test_mode(self):
        """Проверяет неправильное значение test_mode."""
        self.config["test_mode"] = "maybe"
        self.save_config()

        with self.assertRaises(ValueError):
            validate_config(read_config(self.filename))

    def test_missing_test_file(self):
        """Проверяет отсутствие тестового репозитория."""
        self.config["test_mode"] = "true"
        self.config["repository"] = "missing_repo.txt"
        self.save_config()

        with self.assertRaises(ValueError):
            validate_config(read_config(self.filename))

    def test_correct_test_mode(self):
        """Проверяет работу с существующим тестовым файлом."""
        test_file = Path(self.temp_dir.name) / "repo.txt"
        test_file.write_text("A: B", encoding="utf-8")

        self.config["test_mode"] = "true"
        self.config["repository"] = str(test_file)
        self.save_config()

        result = validate_config(read_config(self.filename))

        self.assertTrue(result["test_mode"])

    def test_wrong_output_file(self):
        """Проверяет неправильное расширение файла."""
        self.config["output_file"] = "graph.txt"
        self.save_config()

        with self.assertRaises(ValueError):
            validate_config(read_config(self.filename))

    def test_wrong_max_depth(self):
        """Проверяет отрицательную глубину."""
        self.config["max_depth"] = "-5"
        self.save_config()

        with self.assertRaises(ValueError):
            validate_config(read_config(self.filename))

    def test_depth_not_number(self):
        """Проверяет нечисловое значение глубины."""
        self.config["max_depth"] = "abc"
        self.save_config()

        with self.assertRaises(ValueError):
            validate_config(read_config(self.filename))

    def test_wrong_filter_substring(self):
        """Проверяет недопустимый перенос строки в фильтре."""
        self.config["filter_substring"] = "abc\nxyz"
        self.save_config()

        with self.assertRaises(ValueError):
            validate_config(read_config(self.filename))

    def test_empty_filter_substring(self):
        """Проверяет допустимую пустую подстроку."""
        self.config["filter_substring"] = ""
        self.save_config()

        result = validate_config(read_config(self.filename))

        self.assertEqual(result["filter_substring"], "")

    def test_missing_parameter(self):
        """Проверяет отсутствие обязательного параметра."""
        del self.config["package_name"]
        self.save_config()

        with self.assertRaises(ValueError):
            validate_config(read_config(self.filename))

    def test_duplicate_parameter(self):
        """Проверяет повтор параметра в CSV."""
        self.save_config()

        with open(self.filename, "a", encoding="utf-8") as file:
            file.write("package_name,numpy\n")

        with self.assertRaises(ValueError):
            read_config(self.filename)

    def test_wrong_csv_header(self):
        """Проверяет неправильный заголовок CSV."""
        self.filename.write_text(
            "name,value\npackage_name,requests\n",
            encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            read_config(self.filename)

    def test_missing_file(self):
        """Проверяет отсутствие конфигурационного файла."""
        with self.assertRaises(ValueError):
            read_config("missing_config.csv")


if __name__ == "__main__":
    unittest.main()
