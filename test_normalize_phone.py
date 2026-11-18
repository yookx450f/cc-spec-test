import unittest

from normalize_phone import normalize_phone


class ExistingBehaviorTest(unittest.TestCase):
    """既存の合格条件（変更で壊さないこと）。"""

    def test_mobile_11_digits_3_4_4(self):
        self.assertEqual(normalize_phone("09012345678"), "090-1234-5678")
        self.assertEqual(normalize_phone("090-1234-5678"), "090-1234-5678")

    def test_landline_10_digits_2_4_4(self):
        self.assertEqual(normalize_phone("0312345678"), "03-1234-5678")
        self.assertEqual(normalize_phone("03 1234 5678"), "03-1234-5678")

    def test_fullwidth_digits_and_hyphen(self):
        self.assertEqual(normalize_phone("０９０－１２３４－５６７８"), "090-1234-5678")

    def test_fullwidth_space_separator(self):
        self.assertEqual(normalize_phone("03　1234　5678"), "03-1234-5678")

    def test_halfwidth_parentheses(self):
        self.assertEqual(normalize_phone("(03)1234-5678"), "03-1234-5678")
        self.assertEqual(normalize_phone("(03) 1234-5678"), "03-1234-5678")

    def test_plus81(self):
        self.assertEqual(normalize_phone("+81-90-1234-5678"), "090-1234-5678")
        self.assertEqual(normalize_phone("+81 3 1234 5678"), "03-1234-5678")

    def test_strips_surrounding_spaces(self):
        self.assertEqual(normalize_phone("  09012345678　"), "090-1234-5678")

    def test_invalid_returns_none(self):
        for value in (
            "",
            "12345678901",
            "031234567",
            "090123456789",
            "090-1234-5678x",
            "03)1234-5678",
            "03-(1234)-5678",
            "090--1234-5678",
        ):
            with self.subTest(value=value):
                self.assertIsNone(normalize_phone(value))

    def test_non_string_returns_none(self):
        for value in (None, 9012345678, b"09012345678"):
            with self.subTest(value=value):
                self.assertIsNone(normalize_phone(value))


class TollFreeTest(unittest.TestCase):
    """0120 / 0800 で始まる 10 桁は 4-3-3。"""

    def test_0120_4_3_3(self):
        self.assertEqual(normalize_phone("0120123456"), "0120-123-456")
        self.assertEqual(normalize_phone("012-012-3456"), "0120-123-456")

    def test_0800_4_3_3(self):
        self.assertEqual(normalize_phone("0800123456"), "0800-123-456")
        self.assertEqual(normalize_phone("0800 123 456"), "0800-123-456")

    def test_fullwidth_and_plus81(self):
        self.assertEqual(normalize_phone("０１２０－１２３－４５６"), "0120-123-456")
        self.assertEqual(normalize_phone("+81 120 123 456"), "0120-123-456")

    def test_parenthesized(self):
        self.assertEqual(normalize_phone("(0120)123-456"), "0120-123-456")
        self.assertEqual(normalize_phone("（０８００）１２３－４５６"), "0800-123-456")

    def test_similar_prefixes_unchanged(self):
        self.assertEqual(normalize_phone("0121234567"), "01-2123-4567")
        self.assertEqual(normalize_phone("0801234567"), "08-0123-4567")

    def test_11_digits_unchanged(self):
        self.assertEqual(normalize_phone("08001234567"), "080-0123-4567")
        self.assertEqual(normalize_phone("01201234567"), "012-0123-4567")

    def test_invalid_length_returns_none(self):
        self.assertIsNone(normalize_phone("012012345"))


class FullwidthParenthesesTest(unittest.TestCase):
    """全角括弧は半角に直してから判定する。"""

    def test_fullwidth_parentheses(self):
        self.assertEqual(normalize_phone("（03）1234-5678"), "03-1234-5678")
        self.assertEqual(normalize_phone("（０３）　１２３４－５６７８"), "03-1234-5678")

    def test_mixed_width_parentheses(self):
        self.assertEqual(normalize_phone("（03)1234-5678"), "03-1234-5678")
        self.assertEqual(normalize_phone("(03）1234-5678"), "03-1234-5678")

    def test_invalid_fullwidth_parentheses(self):
        for value in ("03）1234-5678", "03-（1234）-5678", "（03）（1234）5678"):
            with self.subTest(value=value):
                self.assertIsNone(normalize_phone(value))


if __name__ == "__main__":
    unittest.main()
