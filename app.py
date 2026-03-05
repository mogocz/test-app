
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


import streamlit as st

url = st.text_input("URL", value="https://drive.google.com/file/d/1YmUETQCNLsxvRr1rdYal_GuBGaz6qvcZ/view?usp=sharing")
label = st.text_input("Text odkazu", value="Otevřít soubor")

if url:
    st.link_button(label, url)  # label je proměnná [1](https://docs.streamlit.io/develop/api-reference/widgets/st.link_button)
