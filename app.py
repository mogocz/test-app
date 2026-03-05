
import streamlit as st

st.title("This is a title A")
st.title("_Streamlit_ is :blue[cool] :sunglasses:")
st.title("Moje první webová apka")

name = st.text_input("Jak se jmenuješ?")
if st.button("pozdrav Mě hned"):
    st.write(f"Ahoj, {name} 👋")


from pathlib import Path

Path("data").mkdir(exist_ok=True)
Path("data/pozdrav.txt").write_text("Ahoj!", encoding="utf-8")
text = Path("data/pozdrav.txt").read_text(encoding="utf-8")
print(text)


