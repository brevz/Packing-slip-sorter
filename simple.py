import streamlit as st

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = "password"

# Define the password
password = "your-new-password"

# Password Screen
if st.session_state.step == "password":
    st.title("Packing Slip Sorter by Ben Revzin")
    user_input = st.text_input("Enter Password:", type="password")

    if user_input == password:
        st.session_state.step = "main"
    elif user_input:
        st.error("Incorrect password. Please try again.")

# Main App Screen
if st.session_state.step == "main":
    st.title("Welcome to the Packing Slip Sorter!")
    st.info(
        """
        **Note**: Your uploaded files are processed securely and temporarily. 
        They are deleted automatically after processing and are not stored permanently.
        """
    )

    # Example main app functionality
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_file:
        st.success("File uploaded successfully!")
        # Add your PDF processing logic here

    # Logout Button
    if st.button("Logout"):
        st.session_state.step = "password"
        st.experimental_rerun()  # Force app to rerun after logout
