"""
eurostat_io.py — citirea si validarea fisierelor Eurostat in format SDMX-CSV.

Modul comun folosit de toate scripturile din acest depozit.

Autor: Copacel Sergiu Aurelian
Licenta: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# Cele 27 de state membre ale UE, denumiri exact cum apar in exporturile Eurostat
UE27 = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia",
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece",
    "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg",
    "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia",
    "Slovenia", "Spain", "Sweden",
]

# ATENTIE: setul sdg_10_10 contine doua agregate UE. Se foloseste EXCLUSIV acesta.
AGREGAT_UE = "European Union - 27 countries (from 2020)"

COLOANE_OBLIGATORII = {"geo", "TIME_PERIOD", "OBS_VALUE"}


def citeste(cale: str | Path) -> pd.DataFrame:
    """Citeste un fisier Eurostat SDMX-CSV si verifica structura minima."""
    cale = Path(cale)
    if not cale.exists():
        raise FileNotFoundError(
            f"Fisierul nu exista: {cale}\n"
            "Descarca-l din Eurostat Data Browser si pune-l in data/raw/."
        )

    df = pd.read_csv(cale)
    lipsa = COLOANE_OBLIGATORII - set(df.columns)
    if lipsa:
        raise ValueError(
            f"{cale.name}: lipsesc coloanele {sorted(lipsa)}. "
            "Verifica daca exportul este in format SDMX-CSV, nu tabelar."
        )

    df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce").astype("Int64")
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    return df


def metadate(df: pd.DataFrame) -> dict:
    """Extrage metadatele necesare notei de sursa (cod, unitate, filtre, actualizare)."""
    meta: dict[str, object] = {}
    for col in ("DATAFLOW", "LAST UPDATE", "freq", "unit"):
        if col in df.columns and df[col].notna().any():
            meta[col] = sorted(df[col].dropna().unique().tolist())

    # dimensiunile specifice fiecarui set (gaz, sector, indicator etc.)
    tehnice = COLOANE_OBLIGATORII | {
        "DATAFLOW", "LAST UPDATE", "freq", "unit", "OBS_FLAG", "CONF_STATUS",
    }
    for col in df.columns:
        if col in tehnice:
            continue
        val = df[col].dropna().unique()
        if 0 < len(val) <= 5:
            meta[col] = sorted(val.tolist())
    return meta


def filtreaza_ue27(df: pd.DataFrame, cu_agregat: bool = False) -> pd.DataFrame:
    """Pastreaza doar cele 27 de state membre; optional si agregatul UE27."""
    tinte = list(UE27) + ([AGREGAT_UE] if cu_agregat else [])
    out = df[df["geo"].isin(tinte)].copy()

    gasite = set(out["geo"]) & set(UE27)
    if len(gasite) < 27:
        lipsa = sorted(set(UE27) - gasite)
        print(f"  ATENTIE: lipsesc {len(lipsa)} state: {', '.join(lipsa)}", file=sys.stderr)
    return out


def panel(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma in matrice ani x tari."""
    return df.pivot_table(index="TIME_PERIOD", columns="geo", values="OBS_VALUE")


def ani_compleți(df: pd.DataFrame) -> list[int]:
    """Anii in care toate cele 27 de state au observatie valida."""
    p = panel(filtreaza_ue27(df))
    p = p.reindex(columns=UE27)
    return p.dropna(axis=0, how="any").index.tolist()


def raport(df: pd.DataFrame, eticheta: str) -> dict:
    """Raport de acoperire pentru un set de date."""
    d = df.dropna(subset=["OBS_VALUE"])
    ani = ani_compleți(df)
    info = {
        "set": eticheta,
        "randuri": len(df),
        "observatii_valide": len(d),
        "valori_lipsa": int(df["OBS_VALUE"].isna().sum()),
        "entitati": int(df["geo"].nunique()),
        "an_min": int(d["TIME_PERIOD"].min()) if len(d) else None,
        "an_max": int(d["TIME_PERIOD"].max()) if len(d) else None,
        "ani_panel_echilibrat": len(ani),
        "interval_echilibrat": (min(ani), max(ani)) if ani else None,
        "metadate": metadate(df),
    }
    return info


def afiseaza_raport(info: dict) -> None:
    print(f"\n{'=' * 68}")
    print(f"  {info['set']}")
    print(f"{'=' * 68}")
    print(f"  Randuri              : {info['randuri']:,}")
    print(f"  Observatii valide    : {info['observatii_valide']:,}")
    print(f"  Valori lipsa         : {info['valori_lipsa']:,}")
    print(f"  Entitati geografice  : {info['entitati']}")
    print(f"  Interval temporal    : {info['an_min']}–{info['an_max']}")
    print(f"  Panel echilibrat UE27: {info['ani_panel_echilibrat']} ani", end="")
    if info["interval_echilibrat"]:
        a, b = info["interval_echilibrat"]
        print(f" ({a}–{b}) → {info['ani_panel_echilibrat'] * 27} observatii")
    else:
        print()
    print("  Metadate:")
    for k, v in info["metadate"].items():
        text = "; ".join(str(x)[:70] for x in v) if isinstance(v, list) else str(v)
        print(f"    {k:16s}: {text}")
