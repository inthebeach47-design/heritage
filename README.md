# Heritage Mabati local site

This project contains a Python scraper and a local static export of the Heritage Mabati website.

## Preview the current export

```bash
python3 heritage_export/serve.py
```

Open <http://127.0.0.1:8080> in a browser.

## Regenerate the export

```bash
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium
python3 kentank.py
```

The scraper writes the site to `heritage_export/`.
