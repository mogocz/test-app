
import streamlit as st

st.title("This is a title A")
st.title("_Streamlit_ is :blue[cool] :sunglasses:")
st.title("Moje první webová apka")

name = st.text_input("Jak se jmenuješ?")
if st.button("pozdrav Mě hned"):
    st.write(f"Ahoj, {name} 👋")



import streamlit as st

uploaded = st.file_uploader("Nahraj soubor", type=["txt", "csv"])
if uploaded is not None:
    data = uploaded.read()   # bytes [8](https://deepwiki.com/streamlit/streamlit/10-file-handling-and-uploads)
    st.write("Velikost:", len(data), "B")
