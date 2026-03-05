
import streamlit as st

st.title("This is a title A")
st.title("_Streamlit_ is :blue[cool] :sunglasses:")
st.title("Moje první webová apka")

name = st.text_input("Jak se jmenuješ?")
if st.button("pozdrav Mě"):
    st.write(f"Ahoj, {name} 👋")



import streamlit as st

uploaded = st.file_uploader("Nahraj soubor", type=["txt", "csv"])

if uploaded is not None:
    with open(uploaded.name, "wb") as f:
        f.write(uploaded.read())

st.markdown("[A025552378N0204](https://drive.google.com/file/d/1YmUETQCNLsxvRr1rdYal_GuBGaz6qvcZ/view?usp=sharing)")
