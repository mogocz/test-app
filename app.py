
import streamlit as st

st.title("This is a title")
st.title("_Streamlit_ is :blue[cool] :sunglasses:")
st.title("Moje první webová apka")

name = st.text_input("Jak se jmenuješ?")
if st.button("pozdrav Mě hned"):
    st.write(f"Ahoj, {name} 👋")

