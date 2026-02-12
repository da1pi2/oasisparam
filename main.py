import streamlit as st
from openai import OpenAI

# Config OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"],
)

SYSTEM_PROMPT = """
Sei OasisParam AI, assistente per ARREDO URBANO VERDE parametrico (Nature-Based Solutions).

REGOLA RIGIDA: Rispondi SEMPRE con questo formato ESATTO:

**CONFIGURAZIONE ARREDO VERDE**
- Elemento 1: [nome] | Q.tà: [n] | Funzione: [ombra/sociale/permeabile/etc]
- Elemento 2: [nome] | Q.tà: [n] | Funzione: [ombra/sociale/permeabile/etc]

**PARAMETRI GRASSHOPPER** (copia qui)
panchina_A: L=[2.4], W=[0.6], H=[0.45], moduli=, veg_h=[1.2], veg_dens=, perm=
pergolato_B: luce=[3.0], passo=[1.5], h_tot=[2.8], copertura=, veg_h=[2.5]

**VEGETAZIONE** (specie + manutenzione)
- Specie: [3-5 specie native al clima indicato]
- Manutenzione: [bassa/media]

Arredi possibili: panchine vegetate, pergolati, planter modulari, sedute backsplash, bordi rialzati, schermi verticali.
Parametri: L=lunghezza(m), W=larghezza, H=altezza, moduli=n°, veg_h=altezza vegetazione(m), veg_dens=%copertura, perm=%suolo permeabile, luce=apertura(m), passo=spaziatura(m), copertura=%ombra.

Rispondi SOLO con questo formato, niente testo extra.
"""

def call_model(user_input: str) -> str:
    chat_completion = client.chat.completions.create(
        model="meta-llama/llama-3.1-8b-instruct:free",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
        temperature=0.35,
        max_tokens=700,
    )
    return chat_completion.choices[0].message.content

st.set_page_config(page_title="OasisParam AI", layout="wide")
st.title("🌿 OasisParam AI Assistant")
st.caption("Generatore di parametri per arredi urbani verdi (Grasshopper-ready)")

if "chat" not in st.session_state:
    st.session_state.chat = []

for role, content in st.session_state.chat:
    with st.chat_message(role):
        st.markdown(content)

prompt = st.chat_input("Descrivi il contesto (es. 'piazza calda a Livorno, budget medio, bassa manutenzione')")
if prompt:
    st.session_state.chat.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Genero configurazione e parametri..."):
            reply = call_model(prompt)
            st.markdown(reply)
    st.session_state.chat.append(("assistant", reply))
