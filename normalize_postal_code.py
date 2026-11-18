"""日本の郵便番号の表記を統一するユーティリティ。"""

from __future__ import annotations

import re

# 全角数字・全角/長音系ハイフンを半角へ
_ZEN2HAN = str.maketrans("０１２３４５６７８９－ー−‐", "0123456789----")

# 「〒」記号（任意）+ 3桁 + 区切り（ハイフン1つ・空白1つ・なし）+ 4桁
_POSTAL_RE = re.compile(r"(?:〒[ 　]*)?([0-9]{3})[- 　]?([0-9]{4})")


def normalize_postal_code(postal_code: object) -> str | None:
    """日本の郵便番号を 123-4567 形式に統一する。

    - 全角数字・全角ハイフン（－ ー − ‐）は半角に直してから判定する
    - 3桁と4桁の間の区切りは、ハイフン・空白（半角/全角）1文字またはなし
    - 先頭の「〒」記号と前後の空白は無視する
    - 7桁の郵便番号として解釈できない入力、文字列以外の入力は None を返す

    >>> normalize_postal_code("1234567")
    '123-4567'
    >>> normalize_postal_code("〒１２３－４５６７")
    '123-4567'
    >>> normalize_postal_code("12-34567") is None
    True
    """
    if not isinstance(postal_code, str):
        return None

    s = postal_code.translate(_ZEN2HAN).strip(" 　")
    m = _POSTAL_RE.fullmatch(s)
    if m is None:
        return None

    return f"{m[1]}-{m[2]}"
