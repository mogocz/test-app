
import streamlit as st

st.title("Moje první webová apka")

name = st.text_input("Jak se jmenuješ?")
if st.button("pozdrav"):
    st.write(f"Ahoj, {name} 👋")
