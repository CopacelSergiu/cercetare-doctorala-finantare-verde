"""
Figura 5.1 — Ponderea energiei din surse regenerabile în consumul final brut,
România și UE-27 (2004–2024).

Generează PNG la 300 dpi și PDF vectorial.

Fișier de intrare necesar, în același director:
    nrg_ind_ren__custom_22483738_linear.csv   (Eurostat, Data Browser)

Autor: Copăcel Sergiu Aurelian
Licență: MIT
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------- parametri

RADACINA = Path(__file__).resolve().parent.parent
BRUTE, IESIRE = RADACINA / "data" / "raw", RADACINA / "output"
IESIRE.mkdir(exist_ok=True)
FISIER = str(BRUTE / "nrg_ind_ren__custom_22483738_linear.csv")
AGREGAT_UE = "European Union - 27 countries (from 2020)"   # egalitate exactă:
# setul sdg_10_10 conține și agregatul istoric (2007-2013); o căutare parțială
# după „European Union" ar prinde ambele și ar dubla rândurile
AN_MIN, AN_MAX = 2004, 2024

COLOR_RO = "#801A1E"     # România
COLOR_UE = "#1D4E75"     # UE-27
COLOR_FILL = "#F2E8E8"   # zona dintre curbe
COLOR_BAR = "#A85252"    # bare
COLOR_TXT = "#2C3E50"
COLOR_AX = "#7F8C8D"

plt.rcParams["font.family"] = "serif"
plt.rcParams["mathtext.fontset"] = "dejavuserif"


def ro_num(x, zecimale=2):
    """Format numeric românesc: virgulă ca separator zecimal."""
    return f"{x:+.{zecimale}f}".replace(".", ",")


# ---------------------------------------------------------------- date

df = pd.read_csv(FISIER)

ro = df[df["geo"] == "Romania"][["TIME_PERIOD", "OBS_VALUE"]]
ue = df[df["geo"] == AGREGAT_UE][["TIME_PERIOD", "OBS_VALUE"]]

if ro.empty or ue.empty:
    raise SystemExit(
        "Nu s-au găsit seriile. Verifică denumirile din coloana 'geo': "
        "exportul SDMX-CSV folosește denumiri complete, nu coduri."
    )

d = (ro.merge(ue, on="TIME_PERIOD", suffixes=("_RO", "_UE"))
       .query("@AN_MIN <= TIME_PERIOD <= @AN_MAX")
       .sort_values("TIME_PERIOD")
       .dropna())
d["DIF"] = d["OBS_VALUE_RO"] - d["OBS_VALUE_UE"]

asteptat = AN_MAX - AN_MIN + 1
if len(d) != asteptat:
    print(f"Atenție: {len(d)} ani în loc de {asteptat}. Verifică acoperirea seriilor.")

ani = d["TIME_PERIOD"].tolist()
an_varf = int(d.loc[d["DIF"].idxmax(), "TIME_PERIOD"])   # anul avansului maxim


def val(an, col):
    return float(d.loc[d["TIME_PERIOD"] == an, col].iloc[0])


# ---------------------------------------------------------------- figura

fig, (sus, jos) = plt.subplots(
    2, 1, figsize=(9, 8), dpi=300,
    gridspec_kw={"height_ratios": [2.5, 1]}, sharex=True,
)

sus.plot(ani, d["OBS_VALUE_RO"], color=COLOR_RO, lw=2.2,
         marker="o", ms=4, label="România", zorder=3)
sus.plot(ani, d["OBS_VALUE_UE"], color=COLOR_UE, lw=2.2,
         marker="s", ms=4, label="UE-27", zorder=3)
sus.fill_between(ani, d["OBS_VALUE_RO"], d["OBS_VALUE_UE"],
                 color=COLOR_FILL, alpha=0.7, zorder=1)

sus.set_ylabel("% din consumul final brut", fontsize=10.5, color=COLOR_TXT)
sus.legend(loc="upper left", frameon=False, fontsize=10.5)

# limite calculate din date, nu fixate manual
minim = min(d["OBS_VALUE_RO"].min(), d["OBS_VALUE_UE"].min())
maxim = max(d["OBS_VALUE_RO"].max(), d["OBS_VALUE_UE"].max())
marja = (maxim - minim) * 0.12
# spațiu suplimentar sus și jos, pentru ca adnotările să încapă în cadru
sus.set_ylim(minim - marja * 2.6, maxim + marja * 2.4)
sus.set_xlim(AN_MIN - 1.0, AN_MAX + 0.7)

# trei momente-cheie: începutul seriei, vârful avansului, finalul seriei
# poziția etichetelor este aleasă în zone libere ale graficului:
# sub curba UE-27 la stânga și la mijloc, deasupra curbei României la dreapta
adnotari = [
    (AN_MIN, "", 2.1, -0.34),
    (an_varf, "\n(vârf al avansului)", 2.9, -0.42),
    (AN_MAX, "\n(echivalență)", -4.6, 0.16),
]
for an, sufix, dx, dy_rel in adnotari:
    y_ro, y_ue = val(an, "OBS_VALUE_RO"), val(an, "OBS_VALUE_UE")
    mij = (y_ro + y_ue) / 2
    # săgeată dublă între curbe: arată vizual ce se măsoară
    sus.annotate("", xy=(an, y_ro), xytext=(an, y_ue),
                 arrowprops=dict(arrowstyle="<->", color=COLOR_RO, lw=1.2),
                 zorder=4)
    sus.annotate(
        f"România − UE-27\n{ro_num(y_ro - y_ue)} pp{sufix}",
        xy=(an, mij), xytext=(an + dx, mij + dy_rel * (maxim - minim)),
        arrowprops=dict(arrowstyle="->", color=COLOR_RO, lw=1.0),
        color=COLOR_RO, fontsize=8.5, fontweight="bold", ha="center", zorder=5,
    )

jos.bar(ani, d["DIF"], color=COLOR_BAR, width=0.65)
jos.set_xlabel("Anul", fontsize=10.5, color=COLOR_TXT)
jos.set_ylabel("România − UE-27\n(puncte procentuale)", fontsize=9.5, color=COLOR_TXT)
jos.set_ylim(0, d["DIF"].max() * 1.18)
jos.text(0.985, 0.90, "Avansul României față de media UE-27",
         transform=jos.transAxes, fontsize=8.5, color="#444444",
         va="top", ha="right")

for ax in (sus, jos):
    ax.grid(axis="y", linestyle=":", alpha=0.35, color="#BDC3C7")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLOR_AX)
    ax.spines["bottom"].set_color(COLOR_AX)

pas = 2
jos.set_xticks(list(range(AN_MIN, AN_MAX + 1, pas)))
jos.set_xticklabels([str(a) for a in range(AN_MIN, AN_MAX + 1, pas)])

fig.tight_layout()
fig.savefig(IESIRE / "figura_5_1.png", dpi=300, bbox_inches="tight")
fig.savefig(IESIRE / "figura_5_1.pdf", bbox_inches="tight")
print("Generat: figura_5_1.png (300 dpi) și figura_5_1.pdf")
print(f"Serie: {AN_MIN}–{AN_MAX}, {len(d)} ani. Vârful avansului: {an_varf} "
      f"({ro_num(d['DIF'].max())} pp).")
