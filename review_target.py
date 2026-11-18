"""日本の電話番号の表記を統一するユーティリティ。"""

from __future__ import annotations

import re

# 全角数字・全角ハイフンを半角に変換する対応表
_TO_HALFWIDTH = str.maketrans(
    {**{chr(0xFF10 + i): str(i) for i in range(10)}, "－": "-"}
)

# 区切り（ハイフン・空白）。連続も許容する
_SEP = r"[- ]*"

# 入力全体の表記:
#   [+81 区切り] [(市外局番) 区切り] 数字 (区切り 数字)*
_PHONE_RE = re.compile(
    rf"(?P<intl>\+81{_SEP})?"
    rf"(?:\((?P<area>[0-9]+)\){_SEP})?"
    rf"(?P<rest>[0-9](?:{_SEP}[0-9])*)"
)


def normalize_phone(phone: object) -> str | None:
    """日本の電話番号を XXX-XXXX-XXXX 形式に統一する。

    - 全角数字・全角ハイフンは半角に直してから判定する。
    - 区切りはハイフン・空白を許容する。先頭の市外局番は括弧で囲んでもよい。
    - "+81" で始まる場合は先頭を "0" に置き換える。
    - 0 から始まる10桁または11桁でないもの、入力全体が電話番号の表記で
      ないもの、文字列以外の入力は None を返す。

    11桁は 3-4-4（XXX-XXXX-XXXX）、10桁は 2-4-4（XX-XXXX-XXXX）で区切る。

    >>> normalize_phone("09012345678")
    '090-1234-5678'
    >>> normalize_phone("０９０－１２３４－５６７８")
    '090-1234-5678'
    >>> normalize_phone("(090) 1234 5678")
    '090-1234-5678'
    >>> normalize_phone("+81 90-1234-5678")
    '090-1234-5678'
    >>> normalize_phone("+81 (3) 1234-5678")
    '03-1234-5678'
    >>> normalize_phone("0312345678")
    '03-1234-5678'
    >>> normalize_phone("0901234567")
    '09-0123-4567'
    >>> normalize_phone("090.1234.5678") is None
    True
    >>> normalize_phone("090)1234(5678") is None
    True
    >>> normalize_phone("81312345678") is None
    True
    >>> normalize_phone("+81 0 90 1234 5678") is None
    True
    >>> normalize_phone("電話は090-1234-5678です") is None
    True
    >>> normalize_phone("⓪⑨⓪-①②③④-⑤⑥⑦⑧") is None
    True
    >>> normalize_phone(9012345678) is None
    True
    """
    if not isinstance(phone, str):
        return None

    s = phone.translate(_TO_HALFWIDTH)
    m = _PHONE_RE.fullmatch(s)
    if m is None:
        return None

    digits = (m["area"] or "") + re.sub(r"[- ]", "", m["rest"])
    if m["intl"]:
        digits = "0" + digits

    if not digits.startswith("0") or len(digits) not in (10, 11):
        return None

    if len(digits) == 11:
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"


if __name__ == "__main__":
    import doctest
    import sys

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            print(normalize_phone(arg))
    else:
        result = doctest.testmod()
        print(f"doctest: {result.attempted - result.failed}/{result.attempted} passed")
