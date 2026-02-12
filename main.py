import streamlit as st
from openai import OpenAI

# Config OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"],
)

SYSTEM_PROMPT = """Sei OasisParam AI, assistente specializzato in arredi urbani verdi parametrici (Nature-Based Solutions).

IMPORTANTE: Rispondi SEMPRE con questo formato ESATTO. Segui gli ESEMPI sotto.

FORMATO OUTPUT:

**CONFIGURAZIONE ARREDO VERDE**
- Elemento 1: [nome preciso] | Q.tà: [numero] | Funzione: [ombra/sociale/permeabile]
- Elemento 2: [nome preciso] | Q.tà: [numero] | Funzione: [ombra/sociale/permeabile]

**PARAMETRI GRASSHOPPER** (copia qui)
nome_arredo_A: L=[valore], W=[valore], H=[valore], moduli=[numero], veg_h=[valore], veg_dens=[numero], perm=[numero]
nome_arredo_B: luce=[valore], passo=[valore], h_tot=[valore], copertura=[numero], veg_h=[valore]

text

**VEGETAZIONE** (specie + manutenzione)
- Specie: [3-5 nomi botanici nativi al clima]
- Manutenzione: [bassa/media]

---

ESEMPIO COMPLETO (clima mediterraneo caldo):

**CONFIGURAZIONE ARREDO VERDE**
- Elemento 1: panchina vegetata modulare | Q.tà: 3 | Funzione: ombra/sociale
- Elemento 2: pergolato ombreggiante | Q.tà: 2 | Funzione: ombra/permeabile
- Elemento 3: planter modulare | Q.tà: 8 | Funzione: permeabile/biodiversità

**PARAMETRI GRASSHOPPER** (copia qui)
panchina_A: L=[2.4], W=[0.6], H=[0.45], moduli=, veg_h=[1.2], veg_dens=, perm=

pergolato_B: luce=[3.0], passo=[1.5], h_tot=[2.8], copertura=, veg_h=[2.5]
planter_C: L=[1.0], W=[0.8], H=[0.7], moduli=, veg_h=[1.5], veg_dens=, perm=
​

text

**VEGETAZIONE** (specie + manutenzione)
- Specie: Rosmarinus officinalis, Pistacia lentiscus, Lavandula angustifolia, Teucrium fruticans
- Manutenzione: bassa

---

REGOLE PARAMETRI:
- TUTTI i parametri devono avere valori numerici (MAI vuoti)
- L, W, H, veg_h in metri (es. 2.4, 0.6)
- moduli sempre ≥ 1
- veg_dens, perm, copertura in % (0-100)
- Ogni riga = 1 arredo con TUTTI i suoi parametri

TIPI ARREDO: panchine vegetate, pergolati, planter modulari, sedute backsplash, bordi rialzati, schermi verticali.

ADATTA A:
- Clima caldo → veg_dens basso (30-50%), specie xerofite
- Ombra richiesta → copertura alta (60-80%)
- Budget basso → moduli semplici (2-4)
- Manutenzione bassa → specie autoctone

Rispondi SOLO con il formato sopra. Nessun testo aggiuntivo."""

def call_model(user_input: str) -> str:
    chat_completion = client.chat.completions.create(
        model="arcee-ai/trinity-large-preview:free",
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
