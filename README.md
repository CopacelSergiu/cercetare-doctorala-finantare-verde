# Corelația dintre instrumentele financiare verzi, energia regenerabilă și emisiile de carbon

Cod de analiză a datelor pentru cercetarea doctorală privind relația dintre instrumentele financiare verzi, energia regenerabilă și emisiile de gaze cu efect de seră în Uniunea Europeană, cu accent asupra poziției României.

**Autor:** Copăcel Sergiu Aurelian
**Universitatea „Lucian Blaga" din Sibiu, Școala Doctorală de Economie**
**Licență:** MIT

---

## Ce face acest cod

Extrage, validează și prelucrează datele Eurostat utilizate în lucrare, generează figurile și recalculează, din fișierele sursă, fiecare valoare raportată în tabele.

| Script | Funcție |
|---|---|
| `eurostat_io.py` | Modul comun: citire și validare a fișierelor SDMX-CSV, filtrare pe UE-27, extragere de metadate |
| `01_validare_date.py` | Verifică integritatea seturilor: acoperire temporală și geografică, unități de măsură, valori lipsă, dimensiunea panelului echilibrat |
| `02_panel_descriptiv.py` | Construiește panelul unit pentru cele 27 de state membre și calculează statisticile descriptive |
| `03_obligatiuni_verzi.py` | Analizează setul privind obligațiunile verzi guvernamentale și documentează limitările care împiedică utilizarea sa ca variabilă explicativă |
| `04_valori_tabele.py` | Recalculează, din fișierele sursă, toate valorile care apar în tabelele lucrării |
| `05_figura_5_1.py` | Ponderea energiei regenerabile, România și UE-27 |
| `06_figura_5_2.py` | Variația ponderii pe cele 27 de state membre |
| `07_figura_5_3.py` | Evoluția relativă a emisiilor și a produsului intern brut, indici cu bază fixă |

**Domeniul de aplicare:** extragere, validare și analiză descriptivă. Codul nu conține estimări econometrice; acestea fac obiectul etapei următoare a cercetării și vor fi publicate separat.

---

## Instalare

Necesită Python 3.10 sau ulterior.

**Descărcare prin browser**, fără alte programe:

1. Butonul verde **`Code`**, din partea de sus a paginii
2. **`Download ZIP`**
3. Dezarhivați într-un folder la alegere

Apoi, din folderul dezarhivat, instalați bibliotecile necesare:

```
pip install pandas matplotlib
```

Pentru utilizatorii care au `git` instalat, depozitul poate fi descărcat și astfel:

```
git clone https://github.com/CopacelSergiu/cercetare-doctorala-finantare-verde.git
```

---

## Obținerea datelor

Fișierele de date **nu sunt incluse** în acest depozit; ele aparțin Eurostat și se descarcă direct de la sursă, din [Data Browser](https://ec.europa.eu/eurostat/databrowser/). Se plasează în `data/raw/`, **fără redenumire** — numele original conține identificatorul extragerii.

| Cod | Denumire | Setări necesare |
|---|---|---|
| `env_air_gge` | Greenhouse gas emissions by source sector | Unitate: `Thousand tonnes` · Sector: `Total (excluding LULUCF and memo items)` · Un singur gaz |
| `nrg_ind_ren` | Share of energy from renewable sources | Indicator: `Renewable energy – overall` |
| `sdg_10_10` | Purchasing power adjusted GDP per capita | Indicator: `EXP_PPS_EU27_2020_HAB` · Categorie: `Gross domestic product` |
| `gov_gb` | Stock of general government debt security liabilities issued as green bonds | — |

**Setări de export, pentru toate seturile:**

- Format: `CSV` (SDMX-CSV)
- Data scope: `All selected dimensions`
- `Include non-available data`: **bifat**
- `Compress file (.gzip)`: **debifat**

Scripturile identifică fișierele după codul setului conținut în numele lor, deci acceptă orice sufix generat de Data Browser.

---

## Rulare

```bash
python scripts/01_validare_date.py
python scripts/02_panel_descriptiv.py
python scripts/03_obligatiuni_verzi.py
python scripts/04_valori_tabele.py
python scripts/05_figura_5_1.py
python scripts/06_figura_5_2.py
python scripts/07_figura_5_3.py
```

Rezultatele se scriu în `output/`: rapoarte în format text, tabele în CSV, figuri în PNG la 300 dpi și PDF vectorial.

---

## Verificarea rezultatelor

Scriptul `04_valori_tabele.py` recalculează, exclusiv din fișierele Eurostat, fiecare valoare publicată în tabelele lucrării, precum și afirmațiile numerice din text. Valorile produse pot fi comparate direct cu cele din document.

Aceasta permite verificarea independentă a rezultatelor, fără a necesita acces la textul lucrării.

---

## Avertismente privind datele

**Emisii (`env_air_gge`).** Setul oferă atât `Thousand tonnes`, cât și `Million tonnes`. Alegerea trebuie menținută constantă pe întreaga analiză.

**PIB (`sdg_10_10`).** Setul conține două agregate ale Uniunii Europene: `European Union - 27 countries (from 2020)` și un agregat istoric `(2007-2013)`. Codul folosește exclusiv primul. O filtrare parțială după „European Union" ar prinde ambele agregate și ar dubla rândurile. Coloana `unit` afișează „Percentage", etichetă eronată în exportul SDMX; valorile sunt niveluri în standardul puterii de cumpărare.

**Obligațiuni verzi (`gov_gb`).** Statistică experimentală, colectare unică, neactualizată după iulie 2023. Valorile sunt exprimate în **monedă națională** și nu sunt comparabile direct între state fără conversie prealabilă. Acoperă exclusiv sectorul administrației publice.

**Anul 2025.** Provizoriu pentru mai multe seturi; scripturile îl exclud implicit.

---

## Structura depozitului

```
├── scripts/          codul de analiză
├── data/raw/         fișierele Eurostat (se descarcă separat)
├── output/           rezultate generate
├── requirements.txt
├── LICENSE
└── CITATION.cff
```

Fișierele din `data/raw/` nu se modifică. Orice transformare se realizează exclusiv prin script.

---

## Citare

```bibtex
@software{copacel_2026_finantare_verde,
  author  = {Copăcel, Sergiu Aurelian},
  title   = {Corelația dintre instrumentele financiare verzi, energia
             regenerabilă și emisiile de carbon: cod de analiză a datelor},
  year    = {2026},
  url     = {https://github.com/CopacelSergiu/cercetare-doctorala-finantare-verde},
  license = {MIT}
}
```

---

## Sursele de date

Datele aparțin instituțiilor emitente și sunt supuse condițiilor de utilizare ale acestora. Acest depozit conține exclusiv cod.

- **Eurostat** — [ec.europa.eu/eurostat](https://ec.europa.eu/eurostat)
- **Agenția Europeană de Mediu** — indicatorul privind obligațiunile verzi din cadrul celui de-al 8-lea Program de Acțiune pentru Mediu
- **Autoritatea Bancară Europeană** — tabloul de bord privind riscurile ESG
- **Autoritatea Europeană pentru Valori Mobiliare și Piețe** — raportul anual privind piețele carbonului

Datele Agenției Europene de Mediu privind obligațiunile verzi provin de la un furnizor comercial și sunt protejate prin drepturi de autor. Ele nu sunt redistribuite aici și se accesează direct de la sursă.
