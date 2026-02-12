import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt
import requests

# Configurazione OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"],
)

SYSTEM_PROMPT = """Sei OasisParam AI, esperto in Nature-Based Solutions per arredi urbani verdi.

PROCESSO:
1. ANALIZZA il contesto fornito dall'utente (clima, funzione, vincoli)
2. RAGIONA su: quali arredi servono, che dimensioni, quale vegetazione locale
3. RISPONDI nel formato sotto

FORMATO OUTPUT:

**CONFIGURAZIONE ARREDO VERDE**
- Elemento 1: [nome] | Q.tà: [n] | Funzione: [specifica]
- Elemento 2: [nome] | Q.tà: [n] | Funzione: [specifica]

**PARAMETRI GRASSHOPPER** (copia qui)
```
arredo_A: L=[m], W=[m], H=[m], moduli=[n], veg_h=[m], veg_dens=[%], perm=[%]
arredo_B: luce=[m], passo=[m], h_tot=[m], copertura=[%], veg_h=[m]
```

**VEGETAZIONE** (specie + manutenzione)
- Specie: [4-6 specie NATIVE al clima/territorio specifico]
- Manutenzione: [bassa/media]

REGOLE CHIAVE:
- Clima CALDO (>30°C estate) → veg_dens basso (30-50%), copertura alta (70-85%), specie xerofite/mediterranee
- Clima FREDDO (<5°C inverno) → specie decidue resistenti al gelo, protezione dal vento
- Ventoso/costiero → specie resistenti alla salsedine, ancoraggio robusto
- Budget BASSO → moduli semplici (2-3), materiali riciclati
- Budget ALTO → moduli complessi (4-6), essenze pregiate
- Socialità → panchine 40-60% degli arredi totali
- Solo permeabilità → planter 60-80% degli arredi totali

PARAMETRI (unità):
- L, W, H, veg_h: metri (decimali es. 2.4)
- moduli: numero intero ≥1
- veg_dens, perm, copertura: percentuale 0-100

ARREDI: panchine vegetate, pergolati, planter modulari, sedute con backsplash, bordi rialzati, schermi verticali.

IMPORTANTE: Le specie vegetali DEVONO essere native/adatte al territorio SPECIFICO dell'utente, non generiche."""

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
    reply = chat_completion.choices[0].message.content
    
    # Correggi errori comuni
    reply = reply.replace("ARREDO VERDO", "ARREDO VERDE")
    
    # Aggiungi nota d'uso
    reply += """\n\n---
💡 **Come usare questi parametri in Grasshopper:**
1. Copia il blocco tra i backtick (```)
2. Nel file .gh, imposta gli slider con questi valori
3. Esempio: se vedi `L=[2.4]` → slider `L_panchina` = 2.4
4. Sperimenta varianti cambiando i valori!
"""
    return reply

# Funzione per visualizzazione grafica
def plot_parameters(parameters):
    fig, ax = plt.subplots()
    labels = list(parameters.keys())
    values = list(parameters.values())

    ax.barh(labels, values, color="skyblue")
    ax.set_xlabel("Valori")
    ax.set_title("Visualizzazione Parametri")

    st.pyplot(fig)

# Funzione per analisi statistiche
def analyze_statistics(parameters):
    st.markdown("## Analisi Statistiche")
    st.write("**Media dei Valori:**", sum(parameters.values()) / len(parameters))
    st.write("**Valore Massimo:**", max(parameters.values()))
    st.write("**Valore Minimo:**", min(parameters.values()))

# ============ INTERFACCIA CON TAB ============

st.set_page_config(page_title="OasisParam AI - Giorgia", layout="wide", page_icon="🌿")

st.title("🌿 OasisParam AI Assistant")
st.caption("Strumento AI per oasi urbane e arredi verdi parametrici | Creato per Giorgia 🎁")

# NAVIGAZIONE TAB
tab1, tab2 = st.tabs(["💬 Chat AI", "📖 Istruzioni & Guida Grasshopper"])

# ========== TAB 1: CHAT ==========
with tab1:
    st.markdown("### Descrivi il tuo progetto di oasi urbana")
    st.markdown("*Esempio: 'piazza calda a Palermo, budget medio, socialità + ombra'*")

    if "chat" not in st.session_state:
        st.session_state.chat = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Colonna sinistra per lo storico delle chat con filtro
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("### Storico delle Conversazioni")
        search_term = st.text_input("Cerca nello storico", "")

        filtered_history = [
            (i, history) for i, history in enumerate(st.session_state.chat_history)
            if search_term.lower() in " ".join([msg[1] for msg in history]).lower()
        ]

        for i, history in filtered_history:
            if st.button(f"Chat {i + 1}"):
                st.session_state.chat = history

    with col2:
        # Visualizza i messaggi della chat
        chat_container = st.container()
        with chat_container:
            for role, content in st.session_state.chat:
                with st.chat_message(role):
                    st.markdown(content)

        # Barra di input sempre visibile
        prompt = st.chat_input("Descrivi contesto, clima, obiettivi...")
        if prompt:
            st.session_state.chat.append(("user", prompt))

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Genero configurazione e parametri..."):
                    reply = call_model(prompt)
                    if reply:
                        st.markdown(reply)

                        # Estrai parametri e visualizzali
                        parameters = {
                            "Lunghezza": 2.4,
                            "Larghezza": 0.6,
                            "Altezza": 0.45,
                            "Moduli": 3,
                            "Veg_H": 1.2
                        }  # Sostituisci con parsing dinamico se necessario
                        plot_parameters(parameters)
                        analyze_statistics(parameters)

            st.session_state.chat.append(("assistant", reply))

    # Pulsante per cancellare la chat
    if st.button("Cancella Chat"):
        st.session_state.chat = []
        st.session_state.chat_history = []

    # Aggiungi sezione per ottenere dati climatici
    st.markdown("### Dati Climatici")
    location = st.text_input("Inserisci una località per ottenere i dati climatici", "")
    if location:
        weather_data = get_weather_data(location)
        if weather_data:
            st.write("**Dati Climatici per**", location)
            st.write(weather_data)

    # Tutorial interattivo
    if "show_tutorial" in st.session_state:
        del st.session_state["show_tutorial"]