#!/usr/bin/env python3
"""
03_obligatiuni_verzi.py — analiza setului gov_gb si diagnosticul de fezabilitate.

Documenteaza cele patru limitari care impiedica utilizarea obligatiunilor verzi
ca regresor principal intr-un panel anual: acoperire temporala, statut
experimental, unitate in moneda nationala, sfera restransa la sectorul public.

Rulare:
    python scripts/03_obligatiuni_verzi.py

Iesire:
    output/03_obligatiuni_verzi.csv
    output/03_diagnostic.txt

Autor: Copacel Sergiu Aurelian
Licenta: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import eurostat_io as eio  # noqa: E402

RADACINA = Path(__file__).resolve().parent.parent
BRUTE = RADACINA / "data" / "raw"
IESIRE = RADACINA / "output"

# State membre din zona euro la data colectarii (2019-2022).
# Doar pentru acestea valorile in "moneda nationala" sunt exprimate in euro.
ZONA_EURO = {
    "Austria", "Belgium", "Cyprus", "Estonia", "Finland", "France", "Germany",
    "Greece", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta",
    "Netherlands", "Portugal", "Slovakia", "Slovenia", "Spain",
}


def gaseste(cod: str) -> Path | None:
    for f in sorted(BRUTE.glob("*.csv")):
        if cod in f.name:
            return f
    return None


def main() -> int:
    IESIRE.mkdir(exist_ok=True)
    cale = gaseste("gov_gb")
    if cale is None:
        print("Setul gov_gb lipseste din data/raw/.", file=sys.stderr)
        return 1

    df = eio.citeste(cale)
    linii: list[str] = []

    def spune(s: str = "") -> None:
        print(s)
        linii.append(s)

    spune("\n" + "=" * 68)
    spune("  OBLIGATIUNI VERZI GUVERNAMENTALE — DIAGNOSTIC")
    spune("=" * 68)

    ani = sorted(df["TIME_PERIOD"].dropna().unique())
    unit = df["unit"].dropna().unique().tolist() if "unit" in df.columns else []
    upd = df["LAST UPDATE"].dropna().unique().tolist() if "LAST UPDATE" in df.columns else []

    spune(f"\n  Fisier              : {cale.name}")
    spune(f"  Acoperire temporala : {min(ani)}–{max(ani)} ({len(ani)} ani)")
    spune(f"  Unitate             : {'; '.join(map(str, unit))}")
    spune(f"  Ultima actualizare  : {'; '.join(map(str, upd))}")

    d = eio.filtreaza_ue27(df)
    p = eio.panel(d).reindex(columns=eio.UE27)

    an_ref = max(ani)
    emitenti = p.loc[an_ref][p.loc[an_ref] > 0].sort_values(ascending=False)
    zero = sorted(p.columns[(p.fillna(0) == 0).all(axis=0)])

    spune(f"\n  --- State cu stoc pozitiv in {an_ref} ---")
    spune("  ATENTIE: valorile sunt in MONEDA NATIONALA. Comparabile direct")
    spune("  doar intre statele din zona euro.")
    for tara, val in emitenti.items():
        marca = "EUR" if tara in ZONA_EURO else "moneda nationala"
        spune(f"    {tara:16s} {val:>14,.0f}   [{marca}]")

    spune(f"\n  --- State cu zero pe intreaga perioada ({len(zero)}) ---")
    spune("    " + ", ".join(zero))

    if "Romania" in p.columns:
        spune("\n  --- Romania ---")
        for an in ani:
            v = p.loc[an, "Romania"]
            spune(f"    {an}: {0 if pd.isna(v) else v:,.0f}")
        spune("    Zero real, nu valoare lipsa.")

    spune("\n" + "=" * 68)
    spune("  CONSECINTA METODOLOGICA")
    spune("=" * 68)
    spune(f"  1. Acoperire de {len(ani)} ani — insuficienta pentru panel anual.")
    spune("  2. Statistica experimentala, colectare unica, neactualizata.")
    spune("  3. Unitate in moneda nationala — necesita conversie prealabila.")
    spune("  4. Doar sectorul administratiei publice; exclude emitentii corporativi,")
    spune("     care concentrau 58,8% din valoarea emisiunilor verzi din UE in 2024.")
    spune("")
    spune("  Variabila NU poate sustine rolul de regresor principal.")
    spune("  Se utilizeaza descriptiv si ca test de robustete pe subesantion.")

    p.to_csv(IESIRE / "03_obligatiuni_verzi.csv")
    (IESIRE / "03_diagnostic.txt").write_text("\n".join(linii), encoding="utf-8")

    print(f"\n  Scris: {IESIRE / '03_obligatiuni_verzi.csv'}")
    print(f"  Scris: {IESIRE / '03_diagnostic.txt'}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
