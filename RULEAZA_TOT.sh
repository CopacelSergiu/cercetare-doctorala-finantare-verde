#!/usr/bin/env bash
# Reconstruieste integral rezultatele lucrarii, pornind de la fisierele CSV.
# Rulare:  bash RULEAZA_TOT.sh
set -e
cd "$(dirname "$0")"
echo "== 1/5  validarea datelor ==============================="
python3 scripts/01_validare_date.py
echo "== 2/5  regenerarea tabelelor din date =================="
python3 scripts/10_genereaza_tabele.py --scrie
echo "== 3/5  regenerarea figurilor =========================="
python3 scripts/05_figuri_capitol5.py
echo "== 4/5  auditul cifrelor ==============================="
python3 scripts/09_audit_cifre.py
echo "== 5/5  construirea documentului Word =================="
python3 scripts/08_teza_finala.py
echo
echo "GATA. Rezultatele sunt in output/"
