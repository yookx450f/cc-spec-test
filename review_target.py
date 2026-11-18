"""日本の電話番号の表記を統一するユーティリティ。"""

from __future__ import annotations

import re
import unicodedata

# 2桁市外局番（この番号帯はすべて 0X-XXXX-XXXX）
_AREA_CODES_2 = {"03", "06"}

# 同じ先頭3桁を持つ4桁市外局番が存在しない3桁市外局番
# （例: 045 横浜, 052 名古屋）。ここにない固定電話は 0XXX-XX-XXXX とみなす。
_AREA_CODES_3 = {"011", "044", "045", "052", "075", "078"}

# 非地理的番号: (先頭, 区切り位置)
_SPECIAL_PREFIXES = [
    ("0120", (4, 7)),  # フリーダイヤル 0120-XXX-XXX
    ("0570", (4, 7)),  # ナビダイヤル   0570-XXX-XXX
    ("0800", (4, 7)),  # フリーダイヤル 0800-XXX-XXXX
    ("050", (3, 7)),   # IP電話        050-XXXX-XXXX
    ("070", (3, 7)),   # 携帯電話
    ("080", (3, 7)),
    ("090", (3, 7)),
    ("020", (3, 7)),   # M2M など
]

_STYLES = ("hyphen", "digits", "e164")


def normalize_phone(phone: str, style: str = "hyphen") -> str:
    """日本の電話番号を統一された表記に変換する。

    全角数字・各種ハイフン/空白/括弧・国番号(+81, 81)を受け付ける。

    Args:
        phone: 入力文字列（例: "０９０（１２３４）５６７８", "+81 90-1234-5678"）
        style: 出力形式
            - "hyphen": ハイフン区切りの国内表記（既定） 例: 090-1234-5678
            - "digits": 数字のみ                         例: 09012345678
            - "e164":   国際表記                         例: +819012345678

    Returns:
        正規化した電話番号文字列。

    Raises:
        ValueError: 電話番号として解釈できない場合、または style が不正な場合。

    Note:
        固定電話の市外局番の桁数は総務省の番号表に依存する。本関数は
        03/06 と一部の3桁局番のみを判定し、それ以外は4桁局番として区切る。
        厳密な区切りが必要な場合は "digits" か "e164" を使うこと。

    >>> normalize_phone("09012345678")
    '090-1234-5678'
    >>> normalize_phone("+81 (90) 1234-5678")
    '090-1234-5678'
    >>> normalize_phone("０３ー１２３４ー５６７８")
    '03-1234-5678'
    >>> normalize_phone("0120.123.456")
    '0120-123-456'
    >>> normalize_phone("045 123 4567")
    '045-123-4567'
    >>> normalize_phone("0466-12-3456")
    '0466-12-3456'
    >>> normalize_phone("090-1234-5678", style="e164")
    '+819012345678'
    >>> normalize_phone("+81-3-1234-5678", style="digits")
    '0312345678'
    """
    if style not in _STYLES:
        raise ValueError(f"style は {_STYLES} のいずれかを指定してください: {style!r}")
    if not isinstance(phone, str):
        raise ValueError(f"文字列を指定してください: {phone!r}")

    # 全角→半角（数字・記号・空白）
    s = unicodedata.normalize("NFKC", phone).strip()

    # 区切り文字として許容するもの以外が含まれていたらエラー
    if not re.fullmatch(r"\+?[0-9\s\-‐‑‒–—―−ー().]+", s):
        raise ValueError(f"電話番号として解釈できない文字が含まれています: {phone!r}")

    has_plus = s.startswith("+")
    digits = re.sub(r"\D", "", s)

    # 国番号 81 を国内表記の 0 に変換
    if has_plus or (digits.startswith("81") and len(digits) in (11, 12)):
        if not digits.startswith("81"):
            raise ValueError(f"日本(+81)以外の国番号には対応していません: {phone!r}")
        digits = digits[2:]
        if digits.startswith("0"):  # "+81 (0)90..." のような表記
            digits = digits[1:]
        digits = "0" + digits

    _validate(digits, phone)

    if style == "digits":
        return digits
    if style == "e164":
        return "+81" + digits[1:]
    return _hyphenate(digits)


def _validate(digits: str, original: str) -> None:
    if not digits.startswith("0") or digits.startswith("00"):
        raise ValueError(f"日本の電話番号として不正です: {original!r}")
    if digits.startswith("0800"):
        expected = 11
    elif digits.startswith(("0120", "0570")):
        expected = 10
    elif digits.startswith(("020", "050", "070", "080", "090")):
        expected = 11
    else:
        expected = 10
    if len(digits) != expected:
        raise ValueError(
            f"桁数が不正です（{expected}桁のはずが{len(digits)}桁）: {original!r}"
        )


def _split(digits: str, cuts: tuple[int, int]) -> str:
    a, b = cuts
    return f"{digits[:a]}-{digits[a:b]}-{digits[b:]}"


def _hyphenate(digits: str) -> str:
    for prefix, cuts in _SPECIAL_PREFIXES:
        if digits.startswith(prefix):
            return _split(digits, cuts)
    # 固定電話（10桁）: 市外局番 + 市内局番 = 6桁、加入者番号 = 4桁
    if digits[:2] in _AREA_CODES_2:
        return _split(digits, (2, 6))
    if digits[:3] in _AREA_CODES_3:
        return _split(digits, (3, 6))
    return _split(digits, (4, 6))


if __name__ == "__main__":
    import doctest
    import sys

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            print(normalize_phone(arg))
    else:
        result = doctest.testmod()
        print(f"doctest: {result.attempted - result.failed}/{result.attempted} passed")
