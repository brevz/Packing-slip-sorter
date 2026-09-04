# Packing Slip Sorter

Sort Volume Distributors packing-slip PDFs by address. Upload a multi-page PDF, list the addresses to group by, and download a ZIP of per-address PDFs plus a master file with separator pages.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

You can also run `streamlit run pdfsorter.py` or `streamlit run simple.py` — all three entrypoints start the same app.

## Streamlit Community Cloud

Set the main file to `streamlit_app.py` (preferred). `pdfsorter.py` and `simple.py` are safe fallbacks if Cloud is already pointed at one of those.
