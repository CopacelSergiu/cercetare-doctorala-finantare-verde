#!/usr/bin/env python3
"""
04_valori_tabele.py — recalculează, din fișierele sursă, toate valorile care
apar în tabelele lucrării.

Scriptul nu depinde de textul lucrării. El produce valorile de referință,
care pot fi comparate cu cele publicate. Orice terț poate verifica astfel
fiecare cifră raportată, pornind exclusiv de la datele Eurostat.

Rulare:
    python scripts/04_valori_tabele.py

Ieșire:
    output/valori_tabele.txt      raport lizibil
    output/tabel_5_2.csv          România și UE-27, seria anuală
    output/tabel_5_3.csv          indici cu baza 2004 = 100
    output/tabel_5_4.csv          statistici descriptive
    output/tabel_5_5.csv          statele membre în anul final

Autor: Copăcel Sergiu Aurelian
Licență: MIT
"""

from __future__ import annotations

import glob
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import eurostat_io as eio  # noqa: E402

RADACINA = Path(__file__).resolve().parent.parent
BRUTE = RADACINA / "data" / "raw"
IESIRE = RADACINA / "output"

AN_BAZA, AN_FINAL = 2004, 2024
ZONA_EURO = {
    "Austria", "Belgium", "Cyprus", "Estonia", "Finland", "France", "Germany",
    "Greece", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta",
    "Netherlands", "Portugal", "Slovakia", "Slovenia", "Spain",
}

linii: list[str] = []


def spune(s: str = "") -> None:
    print(s)
    linii.append(s)


def ro(x, z=0):
    """Format numeric românesc: punct pentru mii, virgulă pentru zecimale."""
    if pd.isna(x):
        return "—"
    return f"{x:,.{z}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def incarca(cod: str, nume: str) -> pd.DataFrame:
    g = [f for f in glob.glob(str(BRUTE / "*.csv")) if cod in f]
    if not g:
        raise SystemExit(f"Lipsește fișierul pentru setul „{cod}” din data/raw/.")
    d = eio.citeste(g[0])
    d = eio.filtreaza_ue27(d, cu_agregat=True)
    return (d[["geo", "TIME_PERIOD", "OBS_VALUE"]].dropna()
            .rename(columns={"OBS_VALUE": nume}))


def main() -> int:
    IESIRE.mkdir(exist_ok=True)

    ghg = incarca("env_air_gge", "GHG")
    ren = incarca("nrg_ind_ren", "REN")
    gdp = incarca("sdg_10_10", "GDP")
    d = ghg.merge(ren, on=["geo", "TIME_PERIOD"]).merge(gdp, on=["geo", "TIME_PERIOD"])
    d = d[d["TIME_PERIOD"].between(AN_BAZA, AN_FINAL)]

    RO = d[d.geo == "Romania"].set_index("TIME_PERIOD")
    UE = d[d.geo == eio.AGREGAT_UE].set_index("TIME_PERIOD")
    ani = sorted(set(RO.index) & set(UE.index))

    spune("=" * 74)
    spune("  VALORILE DIN TABELELE LUCRĂRII, RECALCULATE DIN FIȘIERELE SURSĂ")
    spune("=" * 74)
    spune(f"\nPanel: {d[d.geo.isin(eio.UE27)].geo.nunique()} state × {len(ani)} ani "
          f"({min(ani)}–{max(ani)}) = {d[d.geo.isin(eio.UE27)].shape[0]} observații")

    # ---------------- Tabelul 5.2 ----------------
    spune("\n" + "-" * 74)
    spune("TABELUL 5.2 — România și Uniunea Europeană")
    spune("-" * 74)
    spune(f"{'An':>5} {'Emisii RO':>12} {'Emisii UE':>13} {'Pond.':>7} "
          f"{'Reg.RO':>7} {'Reg.UE':>7} {'Dif.':>7} {'PIB RO':>8} {'PIB UE':>8} {'RO/UE':>7}")
    t52 = []
    for a in ani:
        p = 100 * RO.loc[a, "GHG"] / UE.loc[a, "GHG"]
        dif = RO.loc[a, "REN"] - UE.loc[a, "REN"]
        g = 100 * RO.loc[a, "GDP"] / UE.loc[a, "GDP"]
        spune(f"{a:>5} {ro(RO.loc[a,'GHG']):>12} {ro(UE.loc[a,'GHG']):>13} "
              f"{ro(p,2):>6}% {ro(RO.loc[a,'REN'],2):>7} {ro(UE.loc[a,'REN'],2):>7} "
              f"{ro(dif,2):>7} {ro(RO.loc[a,'GDP']):>8} {ro(UE.loc[a,'GDP']):>8} {ro(g,1):>6}%")
        t52.append({"An": a, "Emisii_RO": RO.loc[a, "GHG"], "Emisii_UE27": UE.loc[a, "GHG"],
                    "Pondere_RO_pct": p, "Regen_RO": RO.loc[a, "REN"],
                    "Regen_UE27": UE.loc[a, "REN"], "Diferenta_pp": dif,
                    "PIB_RO": RO.loc[a, "GDP"], "PIB_UE27": UE.loc[a, "GDP"],
                    "RO_pct_din_UE": g})
    pd.DataFrame(t52).to_csv(IESIRE / "tabel_5_2.csv", index=False)

    # ---------------- Tabelul 5.3 ----------------
    spune("\n" + "-" * 74)
    spune(f"TABELUL 5.3 — indici ({AN_BAZA} = 100)")
    spune("-" * 74)
    spune(f"{'An':>5} {'Em.RO':>8} {'PIB RO':>8} {'Rap.RO':>8} "
          f"{'Em.UE':>8} {'PIB UE':>8} {'Rap.UE':>8}")
    t53 = []
    for a in [2004, 2008, 2012, 2016, 2020, 2024]:
        if a not in ani:
            continue
        ig_ro = 100 * RO.loc[a, "GHG"] / RO.loc[AN_BAZA, "GHG"]
        ip_ro = 100 * RO.loc[a, "GDP"] / RO.loc[AN_BAZA, "GDP"]
        ig_ue = 100 * UE.loc[a, "GHG"] / UE.loc[AN_BAZA, "GHG"]
        ip_ue = 100 * UE.loc[a, "GDP"] / UE.loc[AN_BAZA, "GDP"]
        spune(f"{a:>5} {ro(ig_ro,1):>8} {ro(ip_ro,1):>8} {ro(100*ig_ro/ip_ro,1):>8} "
              f"{ro(ig_ue,1):>8} {ro(ip_ue,1):>8} {ro(100*ig_ue/ip_ue,1):>8}")
        t53.append({"An": a, "Emisii_RO": ig_ro, "PIB_RO": ip_ro, "Raport_RO": 100*ig_ro/ip_ro,
                    "Emisii_UE27": ig_ue, "PIB_UE27": ip_ue, "Raport_UE27": 100*ig_ue/ip_ue})
    pd.DataFrame(t53).to_csv(IESIRE / "tabel_5_3.csv", index=False)

    # ---------------- Tabelul 5.4 ----------------
    spune("\n" + "-" * 74)
    spune("TABELUL 5.4 — statistici descriptive")
    spune("-" * 74)
    st = d[d.geo.isin(eio.UE27)]
    de = st[["GHG", "REN", "GDP"]].describe().T
    de["cv"] = de["std"] / de["mean"]
    spune("\n  Panel A — variabile cu acoperire completă")
    for v, lab, z in [("GHG", "Emisii GES (mii t echiv. CO2)", 0),
                      ("REN", "Energie regenerabilă (%)", 2),
                      ("GDP", "PIB pe locuitor (PPS)", 0)]:
        r = de.loc[v]
        spune(f"    {lab:<32} N={int(r['count'])}  medie={ro(r['mean'],z)}  "
              f"ab.std={ro(r['std'],z)}  min={ro(r['min'],z)}  max={ro(r['max'],z)}  "
              f"cv={ro(r['cv'],3)}")
    de.to_csv(IESIRE / "tabel_5_4.csv")

    g = [f for f in glob.glob(str(BRUTE / "*.csv")) if "gov_gb" in f]
    if g:
        gb = eio.filtreaza_ue27(eio.citeste(g[0])).dropna(subset=["OBS_VALUE"])
        ze = gb[gb.geo.isin(ZONA_EURO)]
        nule = int((ze.OBS_VALUE == 0).sum())
        spune("\n  Panel B — instrumente financiare verzi (zona euro)")
        spune(f"    Obligațiuni verzi guvernamentale   N={len(ze)}  "
              f"nule={nule} ({ro(100*nule/len(ze),1)}%)  medie={ro(ze.OBS_VALUE.mean(),1)}  "
              f"ab.std={ro(ze.OBS_VALUE.std(),1)}  max={ro(ze.OBS_VALUE.max(),1)}  "
              f"cv={ro(ze.OBS_VALUE.std()/ze.OBS_VALUE.mean(),3)}")
        spune(f"    mediană={ro(ze.OBS_VALUE.median(),1)}")

    # ---------------- Tabelul 5.5 ----------------
    spune("\n" + "-" * 74)
    spune(f"TABELUL 5.5 — statele membre în {AN_FINAL}")
    spune("-" * 74)
    u = d[(d.TIME_PERIOD == AN_FINAL) & (d.geo.isin(eio.UE27))].copy()
    u["pond"] = 100 * u["GHG"] / float(UE.loc[AN_FINAL, "GHG"])
    u = u.sort_values("REN", ascending=False)
    spune(f"{'Stat':<16} {'Emisii':>12} {'Pondere':>9} {'Regen.':>9} {'PIB/loc.':>10}")
    for _, r in u.iterrows():
        spune(f"{r['geo']:<16} {ro(r['GHG']):>12} {ro(r['pond'],2):>8}% "
              f"{ro(r['REN'],2):>8}% {ro(r['GDP']):>10}")
    u[["geo", "GHG", "pond", "REN", "GDP"]].to_csv(IESIRE / "tabel_5_5.csv", index=False)

    # ---------------- afirmații din text ----------------
    spune("\n" + "-" * 74)
    spune("AFIRMAȚII NUMERICE DIN TEXT")
    spune("-" * 74)
    pr = eio.panel(eio.filtreaza_ue27(incarca("nrg_ind_ren", "REN")
                                      .rename(columns={"REN": "OBS_VALUE"})))
    var = (pr.loc[AN_FINAL] - pr.loc[AN_BAZA]).dropna().sort_values()
    perechi = [
        ("reducere emisii RO", 100 * (RO.loc[AN_FINAL, "GHG"] / RO.loc[AN_BAZA, "GHG"] - 1), 1, "%"),
        ("reducere emisii UE-27", 100 * (UE.loc[AN_FINAL, "GHG"] / UE.loc[AN_BAZA, "GHG"] - 1), 1, "%"),
        (f"avans regenerabile {AN_BAZA}", RO.loc[AN_BAZA, "REN"] - UE.loc[AN_BAZA, "REN"], 2, " pp"),
        ("avans regenerabile 2010", RO.loc[2010, "REN"] - UE.loc[2010, "REN"], 2, " pp"),
        (f"avans regenerabile {AN_FINAL}", RO.loc[AN_FINAL, "REN"] - UE.loc[AN_FINAL, "REN"], 2, " pp"),
        (f"PIB RO ca % din UE, {AN_BAZA}", 100 * RO.loc[AN_BAZA, "GDP"] / UE.loc[AN_BAZA, "GDP"], 1, "%"),
        (f"PIB RO ca % din UE, {AN_FINAL}", 100 * RO.loc[AN_FINAL, "GDP"] / UE.loc[AN_FINAL, "GDP"], 1, "%"),
        ("variație regenerabile RO", var["Romania"], 2, " pp"),
        ("variație agregat UE-27", UE.loc[AN_FINAL, "REN"] - UE.loc[AN_BAZA, "REN"], 2, " pp"),
    ]
    for et, v, z, u_ in perechi:
        spune(f"  {et:<34} {ro(v, z)}{u_}")
    poz = list(var.index).index("Romania") + 1
    spune(f"  {'poziția RO la variație':<34} locul {poz} din {len(var)}")
    spune(f"  {'state sub România':<34} {', '.join(var.index[:poz-1])}")

    spune("\n" + "=" * 74)
    spune("  Valorile de mai sus pot fi comparate cu cele publicate în lucrare.")
    spune("=" * 74)

    (IESIRE / "valori_tabele.txt").write_text("\n".join(linii), encoding="utf-8")
    print(f"\n  Raport: {IESIRE / 'valori_tabele.txt'}")
    print(f"  Tabele: {IESIRE}/tabel_5_2.csv … tabel_5_5.csv\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
