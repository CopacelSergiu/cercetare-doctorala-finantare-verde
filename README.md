# Instrumente financiare verzi, energie regenerabilă și emisii de carbon — cod de analiză

Cod pentru extragerea, validarea și prelucrarea descriptivă a datelor Eurostat
utilizate în cercetarea doctorală privind relația dintre instrumentele financiare
verzi, energia regenerabilă și emisiile de gaze cu efect de seră în Uniunea Europeană.

**Autor:** Copăcel Sergiu Aurelian
**Licență:** MIT

---

## Ce face acest cod

| Script | Funcție |
|---|---|
| `eurostat_io.py` | Modul comun de citire și validare a fișierelor SDMX-CSV |
| `01_validare_date.py` | Verifică integritatea seturilor: acoperire temporală și geografică, unități de măsură, valori lipsă, dimensiunea panelului echilibrat |
| `02_panel_descriptiv.py` | Construiește panelul unit pentru cele 27 de state membre și calculează statisticile descriptive |
| `03_obligatiuni_verzi.py` | Analizează setul privind obligațiunile verzi guvernamentale și documentează limitările care împiedică utilizarea sa ca regresor principal |
| `05_figuri_capitol5.py` | Generează cele trei figuri, în PNG la 300 dpi și PDF vectorial |
| `08_teza_finala.py` | Construiește documentul Word din capitolele Markdown, cu verificare de integritate |
| `09_audit_cifre.py` | Recalculează fiecare valoare din tabele direct din fișierele sursă și o compară cu textul lucrării |
| `10_genereaza_tabele.py` | Regenerează tabelele din capitole direct din date, eliminând orice etapă manuală |

Întregul lanț se execută printr-o singură comandă:

```bash
bash RULEAZA_TOT.sh
```

Aceasta rulează, în ordine: validarea datelor, regenerarea tabelelor, regenerarea figurilor, auditul cifrelor și construirea documentului.

**Domeniul de aplicare:** extragere, validare și analiză descriptivă.
Codul nu conține estimări econometrice. Acestea fac obiectul etapei următoare
a cercetării și vor fi publicate separat.

---

## Instalare

Necesită Python 3.10 sau ulterior.

```bash
git clone https://github.com/CopacelSergiu/cercetare-doctorala-finantare-verde.git
cd cercetare-doctorala-finantare-verde
pip install -r requirements.txt
```

---

## Obținerea datelor

Fișierele de date **nu sunt incluse** în acest depozit. Se descarcă din
[Eurostat Data Browser](https://ec.europa.eu/eurostat/databrowser/) și se plasează
în `data/raw/`, **fără redenumire** — numele original conține identificatorul extragerii.

| Cod | Denumire | Setări necesare |
|---|---|---|
| `env_air_gge` | Greenhouse gas emissions by source sector | Unitate: `Thousand tonnes` · Sector: `Total (excluding LULUCF and memo items)` · Un singur gaz |
| `nrg_ind_ren` | Share of energy from renewable sources | Indicator: `Renewable energy – overall` |
| `sdg_10_10` | Purchasing power adjusted GDP per capita | Indicator: `EXP_PPS_EU27_2020_HAB` · Categorie: `Gross domestic product` |
| `gov_gb` | Stock of general government debt security liabilities issued as green bonds | — |

**Setări de export pentru toate seturile:**
- Format: `CSV` (SDMX-CSV)
- Data scope: `All selected dimensions`
- `Include non-available data`: **bifat**
- `Compress file (.gzip)`: **debifat**

Codul detectează fișierele după codul setului conținut în numele lor,
deci acceptă orice sufix generat de Data Browser.

---

## Rulare

```bash
python scripts/01_validare_date.py
python scripts/02_panel_descriptiv.py
python scripts/03_obligatiuni_verzi.py
```

Rezultatele se scriu în `output/`.

---

## Structura depozitului

```
├── scripts/
│   ├── eurostat_io.py           modul comun
│   ├── 01_validare_date.py
│   ├── 02_panel_descriptiv.py
│   └── 03_obligatiuni_verzi.py
├── data/raw/                    fișierele Eurostat (nu se editează)
├── output/                      rezultate generate
├── requirements.txt
├── LICENSE
└── CITATION.cff
```

**Regulă de lucru:** fișierele din `data/raw/` nu se modifică niciodată.
Orice transformare se realizează exclusiv prin script.

---

## Avertismente privind datele

**Emisii (`env_air_gge`).** Setul oferă atât `Thousand tonnes`, cât și
`Million tonnes`. Alegerea trebuie menținută constantă pe întreaga analiză.

**PIB (`sdg_10_10`).** Setul conține două agregate ale Uniunii Europene.
Codul folosește exclusiv `European Union - 27 countries (from 2020)`.
Coloana `unit` afișează „Percentage", etichetă eronată în exportul SDMX;
valorile sunt niveluri în standardul puterii de cumpărare.

**Obligațiuni verzi (`gov_gb`).** Statistică experimentală, colectare unică,
neactualizată după iulie 2023. Valorile sunt exprimate în **monedă națională**
și nu sunt comparabile direct între state fără conversie prealabilă.

**Anul 2025.** Provizoriu pentru mai multe seturi. Scriptul `02` îl exclude
implicit prin constanta `AN_MAX`.

---

## Reproductibilitate și verificare

Fiecare valoare raportată în lucrare poate fi regenerată pornind de la
fișierele brute Eurostat prin rularea acestor scripturi. Nu există etape
manuale intermediare.

Scriptul `09_audit_cifre.py` recalculează, din fișierele sursă, fiecare valoare
din tabelele lucrării și o compară cu textul. Auditul acoperă 443 de verificări
și raportează orice nepotrivire, cu indicarea locului exact. Verifică suplimentar
structura tabelelor: număr de coloane, paranteze dezechilibrate, celule anormale.

Scriptul `10_genereaza_tabele.py` permite compararea tabelelor din capitole cu
cele generate din date. Rulat fără argumente, raportează diferențele; rulat cu
`--scrie`, actualizează capitolele.

---

## Citare

```bibtex
@software{copacel_teza_finantare_verde,
  author  = {Copacel, Sergiu Aurelian},
  title   = {Instrumente financiare verzi, energie regenerabilă și emisii
             de carbon: cod de analiză a datelor},
  year    = {2026},
  url     = {https://github.com/CopacelSergiu/cercetare-doctorala-finantare-verde},
  license = {MIT}
}
```

---

## Sursele de date

Datele aparțin instituțiilor emitente și sunt supuse condițiilor de utilizare
ale acestora. Acest depozit conține exclusiv cod.

- **Eurostat** — [ec.europa.eu/eurostat](https://ec.europa.eu/eurostat)
- **Agenția Europeană de Mediu** — indicatorul privind obligațiunile verzi
  din cadrul celui de-al 8-lea Program de Acțiune pentru Mediu
- **Autoritatea Bancară Europeană** — tabloul de bord privind riscurile ESG

Datele Agenției Europene de Mediu privind obligațiunile verzi provin de la un
furnizor comercial și sunt protejate prin drepturi de autor. Ele nu sunt
redistribuite aici și se accesează direct de la sursă.
