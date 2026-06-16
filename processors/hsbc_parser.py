from __future__ import annotations

import re
from typing import List, Dict, Any, Optional


MONEY_RE = re.compile(r"(?P<amount>-?\$?\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})|-?\$?\s?\d+\.\d{2})")


def clean_money(value: str | None) -> Optional[float]:
    if not value:
        return None
    value = value.replace("$", "").replace(",", "").replace(" ", "").strip()
    try:
        return float(value)
    except ValueError:
        return None


def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def looks_like_movement(line: str) -> bool:
    line = normalize_text(line)
    if not re.match(r"^\d{1,2}\s+", line):
        return False
    return len(MONEY_RE.findall(line)) >= 1


def split_reference_description(text_before_amounts: str) -> tuple[str, str]:
    tokens = text_before_amounts.split()
    if not tokens:
        return "", ""

    ref_tokens = []
    while tokens and len(ref_tokens) < 4:
        clean = re.sub(r"\D", "", tokens[-1])
        if len(clean) >= 4:
            ref_tokens.insert(0, tokens.pop())
        else:
            break

    descripcion = " ".join(tokens)
    referencia = " ".join(ref_tokens)
    return normalize_text(descripcion), normalize_text(referencia)


def parse_line_to_movement(line: str, page: int) -> Optional[Dict[str, Any]]:
    line = normalize_text(line)

    if not looks_like_movement(line):
        return None

    day_match = re.match(r"^(?P<day>\d{1,2})\s+(?P<rest>.+)$", line)
    if not day_match:
        return None

    day = int(day_match.group("day"))
    rest = day_match.group("rest")

    amount_matches = list(MONEY_RE.finditer(rest))
    amounts = [clean_money(m.group("amount")) for m in amount_matches]
    amounts = [a for a in amounts if a is not None]

    if not amounts:
        return None

    first_amount_pos = amount_matches[0].start()
    before_amounts = rest[:first_amount_pos].strip()

    descripcion, referencia = split_reference_description(before_amounts)

    movimiento = amounts[-2] if len(amounts) >= 2 else amounts[-1]
    saldo = amounts[-1] if len(amounts) >= 2 else None

    desc_upper = descripcion.upper()

    cargo_keywords = [
        "PAGO", "CGO", "CARGO", "RETIRO", "TDC", "GAST", "TARJ",
        "SEGURO", "POLIZA", "COMISION"
    ]
    abono_keywords = [
        "PRESTAMO", "DEP", "ABONO", "MINISTRACION", "TRANSFER REC",
        "SPEI REC"
    ]

    cargo = None
    abono = None

    if any(k in desc_upper for k in abono_keywords) and "PAGO TDC" not in desc_upper:
        abono = movimiento
    elif any(k in desc_upper for k in cargo_keywords):
        cargo = movimiento
    else:
        cargo = movimiento

    return {
        "Dia": day,
        "Descripcion": descripcion,
        "Referencia/Serial": referencia,
        "Cargo": cargo,
        "Abono": abono,
        "Saldo": saldo,
        "Pagina": page,
        "Observacion": "",
        "Linea OCR": line,
    }


def parse_hsbc_movements(ocr_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    movements: List[Dict[str, Any]] = []

    for page in ocr_pages:
        text = page.get("text", "")
        page_no = page.get("page", None)

        for raw_line in text.splitlines():
            mov = parse_line_to_movement(raw_line, page_no)
            if mov:
                movements.append(mov)

    return movements
