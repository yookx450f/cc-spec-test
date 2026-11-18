import unittest

from normalize_postal_code import normalize_postal_code


class NormalizePostalCodeTest(unittest.TestCase):
    def test_digits_only(self):
        self.assertEqual(normalize_postal_code("1234567"), "123-4567")

    def test_already_normalized(self):
        self.assertEqual(normalize_postal_code("123-4567"), "123-4567")

    def test_leading_zero_is_kept(self):
        self.assertEqual(normalize_postal_code("0010001"), "001-0001")

    def test_fullwidth_digits_and_hyphens(self):
        for value in ("１２３４５６７", "１２３－４５６７", "１２３ー４５６７", "123−4567", "123‐4567"):
            with self.subTest(value=value):
                self.assertEqual(normalize_postal_code(value), "123-4567")

    def test_space_separator(self):
        self.assertEqual(normalize_postal_code("123 4567"), "123-4567")
        self.assertEqual(normalize_postal_code("123　4567"), "123-4567")

    def test_postal_mark(self):
        self.assertEqual(normalize_postal_code("〒123-4567"), "123-4567")
        self.assertEqual(normalize_postal_code("〒 1234567"), "123-4567")

    def test_strips_surrounding_spaces(self):
        self.assertEqual(normalize_postal_code("  123-4567　"), "123-4567")

    def test_invalid_returns_none(self):
        for value in (
            "",
            "   ",
            "123456",
            "12345678",
            "12-34567",
            "1234-567",
            "123--4567",
            "123-4567x",
            "abc-defg",
            "123.4567",
            "〒",
            "住所は123-4567です",
            "①②③-④⑤⑥⑦",
            "١٢٣-٤٥٦٧",
        ):
            with self.subTest(value=value):
                self.assertIsNone(normalize_postal_code(value))

    def test_non_string_returns_none(self):
        for value in (None, 1234567, 123.4567, ["123-4567"], b"1234567"):
            with self.subTest(value=value):
                self.assertIsNone(normalize_postal_code(value))


if __name__ == "__main__":
    unittest.main()
