"""
Figura 5.2 — Variația ponderii energiei regenerabile pe state membre (2004–2024).

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
AGREGAT_UE = "European Union - 27 countries (from 2020)"
AN_START, AN_FINAL = 2004, 2024
TARA_EVIDENTIATA = "Romania"

COLOR_RO = "#801A1E"
COLOR_UE = "#1D4E75"
COLOR_ALT = "#4A5568"
COLOR_TXT = "#2C3E50"
COLOR_AX = "#7F8C8D"

UE27 = {
    "Austria": "Austria", "Belgium": "Belgia", "Bulgaria": "Bulgaria",
    "Croatia": "Croația", "Cyprus": "Cipru", "Czechia": "Cehia",
    "Denmark": "Danemarca", "Estonia": "Estonia", "Finland": "Finlanda",
    "France": "Franța", "Germany": "Germania", "Greece": "Grecia",
    "Hungary": "Ungaria", "Ireland": "Irlanda", "Italy": "Italia",
    "Latvia": "Letonia", "Lithuania": "Lituania", "Luxembourg": "Luxemburg",
    "Malta": "Malta", "Netherlands": "Țările de Jos", "Poland": "Polonia",
    "Portugal": "Portugalia", "Romania": "România", "Slovakia": "Slovacia",
    "Slovenia": "Slovenia", "Spain": "Spania", "Sweden": "Suedia",
}

plt.rcParams["font.family"] = "serif"
plt.rcParams["mathtext.fontset"] = "dejavuserif"


def ro_num(x, zecimale=2):
    return f"{x:+.{zecimale}f}".replace(".", ",")


# ---------------------------------------------------------------- date

df = pd.read_csv(FISIER)

start = (df[df["TIME_PERIOD"] == AN_START][["geo", "OBS_VALUE"]]
         .rename(columns={"OBS_VALUE": "v_start"}))
final = (df[df["TIME_PERIOD"] == AN_FINAL][["geo", "OBS_VALUE"]]
         .rename(columns={"OBS_VALUE": "v_final"}))
d = start.merge(final, on="geo")
d["variatie"] = d["v_final"] - d["v_start"]

# media UE-27 se calculează din agregatul oficial, nu se scrie manual
ue = d[d["geo"] == AGREGAT_UE]
if ue.empty:
    raise SystemExit(f"Agregatul „{AGREGAT_UE}” lipsește din fișier.")
var_ue = float(ue["variatie"].iloc[0])

t = d[d["geo"].isin(UE27)].copy()
if len(t) != 27:
    lipsa = sorted(set(UE27) - set(t["geo"]))
    print(f"Atenție: {len(t)} state în loc de 27. Lipsesc: {', '.join(lipsa)}")

t["tara"] = t["geo"].map(UE27)
t = t.sort_values("variatie")

# ---------------------------------------------------------------- figura

fig, ax = plt.subplots(figsize=(10, 8.5), dpi=300)

culori = [COLOR_RO if g == TARA_EVIDENTIATA else COLOR_ALT for g in t["geo"]]
bare = ax.barh(t["tara"], t["variatie"], color=culori, height=0.68, edgecolor="none")

ax.axvline(var_ue, color=COLOR_UE, linestyle="--", lw=1.5, zorder=0, alpha=0.85,
           label=f"Media UE-27 ({ro_num(var_ue)} pp)")

# etichete de valoare, cu evidențierea statului analizat
for bara, geo, v in zip(bare, t["geo"], t["variatie"]):
    ro = geo == TARA_EVIDENTIATA
    ax.text(v + 0.25, bara.get_y() + bara.get_height() / 2, ro_num(v),
            va="center", ha="left", fontsize=9,
            color=COLOR_RO if ro else COLOR_TXT,
            fontweight="bold" if ro else "normal", zorder=5,
            bbox=dict(boxstyle="square,pad=0.12", fc="white", ec="none", alpha=0.75))

# poziția statului evidențiat în clasament
poz = list(t["geo"]).index(TARA_EVIDENTIATA) + 1
ax.text(0.985, 0.045,
        f"{UE27[TARA_EVIDENTIATA]}: locul {poz} din {len(t)}, "
        f"sub media UE-27 cu {abs(var_ue - float(t.loc[t['geo'] == TARA_EVIDENTIATA, 'variatie'].iloc[0])):.2f} pp".replace(".", ","),
        transform=ax.transAxes, fontsize=9, color=COLOR_RO,
        ha="right", va="bottom")

ax.set_xlabel(f"Variația ponderii energiei regenerabile, {AN_START}–{AN_FINAL} "
              "(puncte procentuale)", fontsize=10.5, labelpad=10, color=COLOR_TXT)
ax.set_xlim(0, t["variatie"].max() * 1.12)
ax.grid(axis="x", linestyle=":", alpha=0.35, color="#BDC3C7")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color(COLOR_AX)
ax.spines["bottom"].set_color(COLOR_AX)
ax.tick_params(colors=COLOR_TXT, labelsize=9.5)
ax.legend(loc="lower right", frameon=True, facecolor="#FFFFFF",
          edgecolor="none", fontsize=10, bbox_to_anchor=(1.0, 0.10))

fig.tight_layout()
fig.savefig(IESIRE / "figura_5_2.png", dpi=300, bbox_inches="tight")
fig.savefig(IESIRE / "figura_5_2.pdf", bbox_inches="tight")
print("Generat: figura_5_2.png (300 dpi) și figura_5_2.pdf")
print(f"State: {len(t)}. Media UE-27: {ro_num(var_ue)} pp. "
      f"{UE27[TARA_EVIDENTIATA]}: locul {poz}.")
