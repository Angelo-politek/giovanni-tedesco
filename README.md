# giovannitedesco.it

Sito di Giovanni Esteban Tedesco, astrofotografo di Brindisi. Pubblicato con GitHub Pages.

- `index.html` (inglese) e `it/index.html` (italiano): pagina principale con portfolio, viaggio nel tempo ed edizioni.
- `works/<opera>/` e `it/opere/<opera>/`: una pagina dedicata per ogni opera.
- `img/`: le immagini. Per sostituire una foto con l'originale in alta risoluzione, carica il nuovo file con lo stesso nome.
- `_build/`: il generatore. I testi delle opere sono in `_build/src/works.py`, la pagina principale in `_build/src/main.html`, le traduzioni in `_build/src/i18n_en.py`. Dopo una modifica: `python3 _build/build.py`.

Le pagine HTML sono generate: modifica i file in `_build/src/`, non quelli generati.
