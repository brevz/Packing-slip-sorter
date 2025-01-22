import streamlit as st

if "step" not in st.session_state:
    st.session_state.step = "start"

if st.session_state.step == "start":
    if st.button("Go to next step"):
        st.session_state.step = "next"
        st.experimental_rerun()

elif st.session_state.step == "next":
    st.write("You are on the next step!")
    if st.button("Reset"):
        st.session_state.step = "start"
        st.experimental_rerun()
