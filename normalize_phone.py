"""日本の電話番号の表記を統一するユーティリティ。"""

from __future__ import annotations

import re

# 全角数字・全角ハイフン・全角括弧を半角へ
_ZEN2HAN = str.maketrans("０１２３４５６７８９－（）", "0123456789-()")

# 区切り文字: ハイフン・半角空白・全角空白
_SEP = r"[- 　]"

# 入力全体が電話番号表記であることを確認するパターン
#   先頭グループは "(03)" のような括弧囲みも可
_PHONE_RE = re.compile(
    rf"(?:\(\d+\){_SEP}?\d+|\d+)(?:{_SEP}\d+)*"
)


def normalize_phone(phone: object) -> str | None:
    """日本の電話番号を XXX-XXXX-XXXX 形式に統一する。

    - 全角数字・全角ハイフン・全角括弧は半角に直してから判定する
    - 区切りはハイフン・空白を許容し、市外局番の括弧囲みも許容する
    - "+81" で始まる場合は先頭を "0" に置き換える
    - 0 始まりの 10 桁または 11 桁のみ受け付ける

    11 桁は 3-4-4（例: 090-1234-5678）、10 桁は 2-4-4（例: 03-1234-5678）で返す。
    ただし 0120 / 0800 で始まる 10 桁は 4-3-3（例: 0120-123-456）で返す。
    電話番号として解釈できない入力、文字列以外の入力は None を返す。
    """
    if not isinstance(phone, str):
        return None

    s = phone.translate(_ZEN2HAN).strip(" 　")

    if s.startswith("+81"):
        s = "0" + s[3:].lstrip(" 　-")

    if not _PHONE_RE.fullmatch(s):
        return None

    digits = re.sub(r"\D", "", s)
    if not digits.startswith("0") or len(digits) not in (10, 11):
        return None

    if len(digits) == 10 and digits.startswith(("0120", "0800")):
        return f"{digits[:4]}-{digits[4:7]}-{digits[7:]}"

    return f"{digits[:-8]}-{digits[-8:-4]}-{digits[-4:]}"
