#!/usr/bin/env python3
"""
02_panel_descriptiv.py — construirea panelului si statistici descriptive.

Uneste seturile Eurostat intr-un panel echilibrat pentru cele 27 de state
membre si produce statisticile descriptive si comparatia Romania — UE27.

Rulare:
    python scripts/02_panel_descriptiv.py

Iesire:
    output/02_panel_ue27.csv          panelul unit, format lung
    output/02_statistici.csv          statistici descriptive pe variabila
    output/02_romania_vs_ue27.csv     comparatia pe ani

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

VARIABILE = {
    "env_air_gge": ("GHG", "Emisii GES, mii tone echiv. CO2"),
    "nrg_ind_ren": ("REN", "Energie regenerabila, % consum final"),
    "sdg_10_10": ("GDPPC", "PIB/locuitor, PPS"),
}

AN_MAX = 2024  # 2025 este provizoriu pentru mai multe seturi; se exclude


def gaseste(cod: str) -> Path | None:
    for f in sorted(BRUTE.glob("*.csv")):
        if cod in f.name:
            return f
    return None


def serie(cod: str, nume: str) -> pd.DataFrame | None:
    cale = gaseste(cod)
    if cale is None:
        print(f"  [{cod}] lipseste", file=sys.stderr)
        return None
    df = eio.citeste(cale)
    df = eio.filtreaza_ue27(df, cu_agregat=True)
    out = df[["geo", "TIME_PERIOD", "OBS_VALUE"]].dropna()
    return out.rename(columns={"OBS_VALUE": nume})


def main() -> int:
    IESIRE.mkdir(exist_ok=True)

    print("\nCONSTRUIREA PANELULUI")

    serii = {}
    for cod, (nume, _) in VARIABILE.items():
        s = serie(cod, nume)
        if s is not None:
            serii[nume] = s
            print(f"  {nume:6s}: {len(s):,} observatii")

    if len(serii) < 2:
        print("Prea putine seturi disponibile.", file=sys.stderr)
        return 1

    # ---- unirea ----------------------------------------------------------
    panel = None
    for s in serii.values():
        panel = s if panel is None else panel.merge(s, on=["geo", "TIME_PERIOD"], how="inner")

    panel = panel[panel["TIME_PERIOD"] <= AN_MAX].sort_values(["geo", "TIME_PERIOD"])

    state = panel[panel["geo"].isin(eio.UE27)]
    n_tari = state["geo"].nunique()
    ani = sorted(state["TIME_PERIOD"].unique())
    echilibrat = state.groupby("TIME_PERIOD")["geo"].nunique().eq(27)
    ani_e = echilibrat[echilibrat].index.tolist()

    print(f"\n  Panel: {n_tari} state × {len(ani)} ani ({min(ani)}–{max(ani)})")
    if ani_e:
        print(f"  Echilibrat: {min(ani_e)}–{max(ani_e)} = "
              f"{len(ani_e)} ani × 27 = {len(ani_e) * 27} observatii")

    panel.to_csv(IESIRE / "02_panel_ue27.csv", index=False)

    # ---- statistici descriptive ------------------------------------------
    print(f"\n{'=' * 68}\n  STATISTICI DESCRIPTIVE (27 state membre)\n{'=' * 68}")
    num = [n for n, _ in VARIABILE.values() if n in state.columns]
    st = state[num].describe().T
    st["cv"] = st["std"] / st["mean"]
    print(st[["count", "mean", "std", "min", "max", "cv"]].to_string(
        float_format=lambda x: f"{x:,.3f}"))
    st.to_csv(IESIRE / "02_statistici.csv")

    # ---- Romania vs UE27 -------------------------------------------------
    print(f"\n{'=' * 68}\n  ROMANIA vs UE27\n{'=' * 68}")
    ro = panel[panel["geo"] == "Romania"].set_index("TIME_PERIOD")
    ue = panel[panel["geo"] == eio.AGREGAT_UE].set_index("TIME_PERIOD")

    if ro.empty or ue.empty:
        print("  Romania sau agregatul UE27 lipsesc din panel.", file=sys.stderr)
        return 0

    cmp_ = pd.DataFrame(index=sorted(set(ro.index) & set(ue.index)))
    for v in num:
        cmp_[f"{v}_RO"] = ro[v]
        cmp_[f"{v}_UE"] = ue[v]
        if v == "GHG":
            cmp_["GHG_pondere_RO_%"] = 100 * ro[v] / ue[v]
        elif v == "GDPPC":
            cmp_["GDPPC_RO_%_din_UE"] = 100 * ro[v] / ue[v]
        elif v == "REN":
            cmp_["REN_diferenta_pp"] = ro[v] - ue[v]

    print(cmp_.to_string(float_format=lambda x: f"{x:,.2f}"))
    cmp_.to_csv(IESIRE / "02_romania_vs_ue27.csv")

    print(f"\n  Scris: {IESIRE / '02_panel_ue27.csv'}")
    print(f"  Scris: {IESIRE / '02_statistici.csv'}")
    print(f"  Scris: {IESIRE / '02_romania_vs_ue27.csv'}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
