import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from io import BytesIO
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime


def create_separator_page(address, width=792, height=612):
    """Create a PDF separator page with the given address in landscape orientation."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    c.setFont("Helvetica-Bold", 36)
    x_offset = 50
    y_offset = height / 2
    c.drawString(x_offset, y_offset, address)
    c.showPage()
    c.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def fix_orientation(page):
    """Fix the orientation of the page based on its /Rotate attribute."""
    rotation = int(page.get("/Rotate", 0))
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)

    # Swap dimensions for rotated pages
    if rotation in (90, 270):
        page.mediabox.upper_right = (height, width)
    else:
        page.mediabox.upper_right = (width, height)

    return page


def process_pdf(uploaded_file, addresses):
    """Process the uploaded PDF, group multi-page packing slips, and create PDFs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        reader = PdfReader(uploaded_file)
        master_writer = PdfWriter()
        zip_buffer = BytesIO()  # To store the ZIP file in memory

        # Generate a timestamp for the ZIP file name
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Dictionary to store pages for each address
        address_pages = {address: [] for address in addresses if address}

        # Track current multi-page packing slip
        current_packing_slip = []
        current_address = None
        in_packing_slip = False

        for page_num, page in enumerate(reader.pages):
            page = fix_orientation(page)  # Ensure orientation is correct
            text = page.extract_text()

            # Detect the start of a new multi-page packing slip
            if "Page 1 of" in text:
                if current_packing_slip and current_address:
                    # Save the current slip to the address group
                    address_pages[current_address].extend(current_packing_slip)

                # Start a new packing slip
                current_packing_slip = [page]
                in_packing_slip = True

                # Determine the address for this slip
                for address in addresses:
                    if address in text:
                        current_address = address
                        break
            elif in_packing_slip:
                # Add pages to the current packing slip
                current_packing_slip.append(page)

                # Detect the end of the slip (no explicit marker for now)
                if "Page" not in text:
                    in_packing_slip = False
                    if current_address:
                        address_pages[current_address].extend(current_packing_slip)
                    current_packing_slip = []
            else:
                # Standalone page not part of a multi-page slip
                for address in addresses:
                    if address in text:
                        address_pages[address].append(page)
                        break

        # Finalize any remaining slip
        if current_packing_slip and current_address:
            address_pages[current_address].extend(current_packing_slip)

        # Write individual PDFs and add to ZIP
        for address, pages in address_pages.items():
            if not pages:
                continue

            writer = PdfWriter()
            separator_page = create_separator_page(address, width=792, height=612)
            writer.add_page(separator_page)
            master_writer.add_page(separator_page)

            for page in pages:
                writer.add_page(page)
                master_writer.add_page(page)

            # Save individual PDF
            individual_pdf_path = temp_dir_path / f"{address.replace(' ', '_')}.pdf"
            with open(individual_pdf_path, "wb") as f:
                writer.write(f)

        # Save master PDF
        master_pdf_path = temp_dir_path / "master_output.pdf"
        with open(master_pdf_path, "wb") as f:
            master_writer.write(f)

        # Create a ZIP file of all PDFs
        zip_file_name = f"sorted_pdfs_{timestamp}.zip"
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for file_path in temp_dir_path.iterdir():
                zipf.write(file_path, arcname=file_path.name)

    zip_buffer.seek(0)  # Reset buffer pointer for download
    return zip_buffer, zip_file_name


# Streamlit UI
st.title("Packing Slip Sorter by Ben Revzin")

# Initialize session state for clearing
if "clear_session" not in st.session_state:
    st.session_state.clear_session = False

if st.session_state.clear_session:
    st.experimental_rerun()  # Restart the app

# Password Protection
password = "the-password"  # Set your password here
user_input = st.text_input("Enter Password:", type="password")

if user_input == password:
    # Add a disclaimer
    st.info(
        """
        **Note**: Your uploaded files are processed securely and temporarily. 
        They are deleted automatically after processing and are not stored permanently.
        """
    )

    # File upload
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    # Addresses input
    addresses = st.text_area(
        "Enter addresses to sort by (one per line):",
        value="\n".join([
            "14502 COUNTY RD 15",
            "7421 EAST STREET",
            "2623 ELDAMAIN RD BLDG 221",
            "5103 NORTH TOWN HALL ROAD",
        ]),  # Default addresses
        height=150,
    ).splitlines()

    if uploaded_file and st.button("Sort PDF"):
        if not addresses:
            st.error("Please enter at least one address.")
        else:
            with st.spinner("Processing..."):
                zip_buffer, zip_file_name = process_pdf(uploaded_file, addresses)
                st.success("Processing complete! You can now download your files.")

                # Download ZIP file and clear session after download
                st.download_button(
                    label="Download All PDFs (ZIP)",
                    data=zip_buffer,
                    file_name=zip_file_name,
                    mime="application/zip",
                    on_click=lambda: setattr(st.session_state, "clear_session", True),
                )
elif user_input:
    st.error("Incorrect password. Please try again.")
