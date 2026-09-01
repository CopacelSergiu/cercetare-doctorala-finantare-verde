#!/usr/bin/env python3
"""
01_validare_date.py — validarea integritatii seturilor de date Eurostat.

Verifica pentru fiecare set: acoperirea temporala si geografica, unitatile de
masura, valorile lipsa si dimensiunea panelului echilibrat pentru UE27.

Rulare:
    python scripts/01_validare_date.py

Iesire:
    output/01_validare_date.csv
    output/01_metadate.txt

Autor: Copacel Sergiu Aurelian
Licenta: MIT
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import eurostat_io as eio  # noqa: E402

RADACINA = Path(__file__).resolve().parent.parent
BRUTE = RADACINA / "data" / "raw"
IESIRE = RADACINA / "output"

# Tiparele de nume ale fisierelor descarcate din Eurostat Data Browser.
# Numele original se pastreaza — contine identificatorul extragerii.
SETURI = {
    "env_air_gge": "Emisii de gaze cu efect de sera pe sector-sursa",
    "nrg_ind_ren": "Ponderea energiei din surse regenerabile",
    "sdg_10_10": "PIB pe locuitor ajustat la puterea de cumparare",
    "gov_gb": "Obligatiuni verzi emise de administratiile publice",
}


def gaseste(cod: str) -> Path | None:
    """Cauta fisierul care incepe cu codul setului de date."""
    for f in sorted(BRUTE.glob("*.csv")):
        if cod in f.name:
            return f
    return None


def main() -> int:
    IESIRE.mkdir(exist_ok=True)
    rapoarte: list[dict] = []
    ani_pe_set: dict[str, set[int]] = {}
    lipsa: list[str] = []

    print("\nVALIDAREA SETURILOR DE DATE EUROSTAT")
    print(f"Director: {BRUTE}")

    for cod, descriere in SETURI.items():
        cale = gaseste(cod)
        if cale is None:
            lipsa.append(cod)
            print(f"\n  [{cod}] LIPSESTE — descarca-l in data/raw/", file=sys.stderr)
            continue

        df = eio.citeste(cale)
        info = eio.raport(df, f"[{cod}] {descriere}")
        info["fisier"] = cale.name
        eio.afiseaza_raport(info)
        rapoarte.append(info)
        ani_pe_set[cod] = set(eio.ani_compleți(df))

    if lipsa:
        print(f"\nSeturi lipsa: {', '.join(lipsa)}", file=sys.stderr)

    # ---- panelul comun ----------------------------------------------------
    if len(ani_pe_set) >= 2:
        print(f"\n{'=' * 68}")
        print("  PANELUL COMUN")
        print(f"{'=' * 68}")

        baza = {k: v for k, v in ani_pe_set.items() if k != "gov_gb"}
        if baza:
            comun = set.intersection(*baza.values())
            if comun:
                print(f"  Fara obligatiuni verzi : {min(comun)}–{max(comun)} = "
                      f"{len(comun)} ani × 27 = {len(comun) * 27} observatii")

            if "gov_gb" in ani_pe_set:
                tot = comun & ani_pe_set["gov_gb"]
                if tot:
                    print(f"  Cu obligatiuni verzi   : {min(tot)}–{max(tot)} = "
                          f"{len(tot)} ani × 27 = {len(tot) * 27} observatii")
                    pierdere = 100 * (1 - len(tot) / len(comun)) if comun else 0
                    print(f"\n  Includerea obligatiunilor verzi elimina "
                          f"{pierdere:.0f}% dintre observatii.")
                    print("  Consecinta metodologica: aceasta variabila nu poate")
                    print("  sustine rolul de regresor principal in panel.")

    # ---- salvare ----------------------------------------------------------
    if rapoarte:
        tabel = pd.DataFrame([
            {k: v for k, v in r.items() if k != "metadate"} for r in rapoarte
        ])
        tabel.to_csv(IESIRE / "01_validare_date.csv", index=False)

        with open(IESIRE / "01_metadate.txt", "w", encoding="utf-8") as fh:
            for r in rapoarte:
                fh.write(f"{r['set']}\n  fisier: {r['fisier']}\n")
                fh.write(json.dumps(r["metadate"], indent=2, ensure_ascii=False))
                fh.write("\n\n")

        print(f"\n  Scris: {IESIRE / '01_validare_date.csv'}")
        print(f"  Scris: {IESIRE / '01_metadate.txt'}\n")

    return 1 if lipsa else 0


if __name__ == "__main__":
    raise SystemExit(main())
