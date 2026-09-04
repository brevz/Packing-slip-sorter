"""Legacy entrypoint — redirects to the real packing slip sorter.

Kept so an old Streamlit Cloud "Main file path = simple.py" setting still works.
"""

from pdfsorter import run_app

run_app()
