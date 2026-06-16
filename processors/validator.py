from __future__ import annotations

from typing import List, Dict, Any


def validate_balances(movements: List[Dict[str, Any]], tolerance: float = 0.05) -> List[Dict[str, Any]]:
    prev_saldo = None

    for mov in movements:
        saldo = mov.get("Saldo")
        cargo = mov.get("Cargo") or 0
        abono = mov.get("Abono") or 0
        obs = mov.get("Observacion", "")

        if saldo is None:
            mov["Observacion"] = (obs + " Sin saldo detectado.").strip()
            continue

        if prev_saldo is not None:
            expected = prev_saldo - cargo + abono

            if abs(expected - saldo) > tolerance:
                expected_inverted = prev_saldo - abono + cargo
                if abs(expected_inverted - saldo) <= tolerance:
                    mov["Observacion"] = (obs + " Posible cargo/abono invertido; revisar.").strip()
                else:
                    mov["Observacion"] = (
                        obs + f" No cuadra saldo. Esperado {expected:,.2f}; OCR {saldo:,.2f}."
                    ).strip()

        prev_saldo = saldo

    return movements
