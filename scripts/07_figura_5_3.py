"""
Figura 5.3 — Evoluția relativă a emisiilor și a produsului intern brut
pe locuitor, România și UE-27, indici (2004 = 100).

Generează PNG la 300 dpi și PDF vectorial.

Fișiere de intrare necesare, în același director:
    env_air_gge__custom_22483513_linear.csv   (Eurostat, emisii GES)
    sdg_10_10__custom_22483888_linear.csv     (Eurostat, PIB/locuitor PPS)

Autor: Copăcel Sergiu Aurelian
Licență: MIT
"""

import glob
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
BRUTE, IESIRE = RADACINA / "data" / "raw", RADACINA / "output"
IESIRE.mkdir(exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------- parametri

AGREGAT_UE = "European Union - 27 countries (from 2020)"   # egalitate exactă:
# setul sdg_10_10 conține și agregatul istoric (2007-2013); o căutare parțială
# după „European Union" ar prinde ambele și ar dubla rândurile
AN_BAZA, AN_FINAL = 2004, 2024

COLOR_RO = "#801A1E"
COLOR_UE = "#1D4E75"
COLOR_TXT = "#2C3E50"
COLOR_AX = "#7F8C8D"

plt.rcParams["font.family"] = "serif"
plt.rcParams["mathtext.fontset"] = "dejavuserif"


def ro_num(x, zecimale=1):
    return f"{x:.{zecimale}f}".replace(".", ",")


def incarca(cod, nume):
    """Citește setul Eurostat al cărui nume de fișier conține codul dat."""
    gasite = [f for f in glob.glob(str(BRUTE / "*.csv")) if cod in f]
    if not gasite:
        raise SystemExit(f"Lipsește fișierul pentru setul „{cod}”.")
    d = pd.read_csv(gasite[0])
    d = d[d["geo"].isin(["Romania", AGREGAT_UE])]
    return (d[["geo", "TIME_PERIOD", "OBS_VALUE"]].dropna()
            .rename(columns={"OBS_VALUE": nume}))


# ---------------------------------------------------------------- date

ghg = incarca("env_air_gge", "GHG")
gdp = incarca("sdg_10_10", "GDP")

d = ghg.merge(gdp, on=["geo", "TIME_PERIOD"])
d = d[d["TIME_PERIOD"].between(AN_BAZA, AN_FINAL)].sort_values("TIME_PERIOD")

RO = d[d["geo"] == "Romania"].set_index("TIME_PERIOD")
UE = d[d["geo"] == AGREGAT_UE].set_index("TIME_PERIOD")

ani = sorted(set(RO.index) & set(UE.index))
asteptat = AN_FINAL - AN_BAZA + 1
if len(ani) != asteptat:
    print(f"Atenție: {len(ani)} ani în loc de {asteptat}.")


def indice(serie, coloana):
    """Indice cu bază fixă: valoarea din anul de bază devine 100."""
    baza = serie.loc[AN_BAZA, coloana]
    return [100 * serie.loc[a, coloana] / baza for a in ani]


i_ghg_ro, i_gdp_ro = indice(RO, "GHG"), indice(RO, "GDP")
i_ghg_ue, i_gdp_ue = indice(UE, "GHG"), indice(UE, "GDP")

# ---------------------------------------------------------------- figura

fig, ax = plt.subplots(figsize=(9.5, 6.5), dpi=300)

ax.plot(ani, i_gdp_ro, color=COLOR_RO, ls="-", lw=2.2, marker="o", ms=4,
        label="PIB/locuitor, România", zorder=3)
ax.plot(ani, i_gdp_ue, color=COLOR_UE, ls="-", lw=2.2, marker="s", ms=4,
        label="PIB/locuitor, UE-27", zorder=3)
ax.plot(ani, i_ghg_ro, color=COLOR_RO, ls="--", lw=1.8, marker="^", ms=4,
        alpha=0.9, label="Emisii GES, România", zorder=3)
ax.plot(ani, i_ghg_ue, color=COLOR_UE, ls="--", lw=1.8, marker="D", ms=3.5,
        alpha=0.9, label="Emisii GES, UE-27", zorder=3)

ax.axhline(100, color=COLOR_AX, ls=":", lw=1.0, alpha=0.7, zorder=0)
ax.text(AN_FINAL - 0.3, 104, f"nivelul din {AN_BAZA}", fontsize=8,
        color=COLOR_AX, va="bottom", ha="right", zorder=4,
        bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=0.8))

# adnotări calculate din date, nu scrise manual
v_gdp_ro, v_gdp_ue = i_gdp_ro[-1], i_gdp_ue[-1]
v_ghg_ro, v_ghg_ue = i_ghg_ro[-1], i_ghg_ue[-1]

ax.annotate(f"{ro_num(v_gdp_ro)}\n(PIB România)",
            xy=(AN_FINAL, v_gdp_ro), xytext=(AN_FINAL - 3.4, v_gdp_ro * 0.93),
            arrowprops=dict(arrowstyle="->", color=COLOR_RO, lw=1.0),
            color=COLOR_RO, fontsize=8.5, fontweight="bold", ha="center", zorder=5)
ax.annotate(f"{ro_num(v_gdp_ue)}\n(PIB UE-27)",
            xy=(AN_FINAL, v_gdp_ue), xytext=(AN_FINAL - 3.6, v_gdp_ue * 1.30),
            arrowprops=dict(arrowstyle="->", color=COLOR_UE, lw=1.0),
            color=COLOR_UE, fontsize=8.5, fontweight="bold", ha="center", zorder=5)
ax.annotate(f"Emisii: {ro_num(v_ghg_ro)} (RO) și {ro_num(v_ghg_ue)} (UE-27)\n"
            f"reduceri practic identice",
            xy=(AN_FINAL, (v_ghg_ro + v_ghg_ue) / 2),
            xytext=(AN_FINAL - 6.0, 22),
            arrowprops=dict(arrowstyle="->", color=COLOR_TXT, lw=1.0),
            color=COLOR_TXT, fontsize=8.5, fontweight="bold", ha="center", zorder=5)

ax.set_xlabel("Anul", fontsize=10.5, color=COLOR_TXT, labelpad=8)
ax.set_ylabel(f"Indice ({AN_BAZA} = 100)", fontsize=10.5, color=COLOR_TXT)
ax.set_xlim(AN_BAZA - 0.6, AN_FINAL + 0.8)
ax.set_ylim(0, max(i_gdp_ro) * 1.10)
pas = 2
ax.set_xticks(list(range(AN_BAZA, AN_FINAL + 1, pas)))
ax.set_xticklabels([str(a) for a in range(AN_BAZA, AN_FINAL + 1, pas)])
ax.grid(axis="y", ls=":", alpha=0.35, color="#BDC3C7")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color(COLOR_AX)
ax.spines["bottom"].set_color(COLOR_AX)
ax.tick_params(colors=COLOR_TXT, labelsize=9.5)
ax.legend(loc="upper left", frameon=True, facecolor="#FFFFFF",
          edgecolor="none", fontsize=9.5)

fig.tight_layout()
fig.savefig(IESIRE / "figura_5_3.png", dpi=300, bbox_inches="tight")
fig.savefig(IESIRE / "figura_5_3.pdf", bbox_inches="tight")
print("Generat: figura_5_3.png (300 dpi) și figura_5_3.pdf")
print(f"Serie {AN_BAZA}–{AN_FINAL}, {len(ani)} ani. "
      f"În {AN_FINAL}: PIB RO {ro_num(v_gdp_ro)}, PIB UE {ro_num(v_gdp_ue)}, "
      f"emisii RO {ro_num(v_ghg_ro)}, emisii UE {ro_num(v_ghg_ue)}.")
