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
        st.markdown("### Storico Chat")
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

            st.session_state.chat.append(("assistant", reply))

    # Pulsante per cancellare la chat
    if st.button("Cancella Chat"):
        st.session_state.chat_history.append(st.session_state.chat)
        st.session_state.chat = []

# ========== TAB 2: ISTRUZIONI ==========
with tab2:
    st.markdown("""
# 🎁 Benvenuta Giorgia!

Questo strumento AI è stato creato appositamente per aiutarti con la tua tesi su **oasi urbane e arredi verdi parametrici**.

---

## 🚀 Come Usare il Chatbot

### 1. Vai al tab "Chat AI"

### 2. Descrivi il tuo contesto
Più dettagli fornisci, migliore sarà il ragionamento dell'AI! Includi:

- **Luogo/clima**: "piazza a Milano, inverno freddo" / "waterfront Genova"
- **Funzioni**: "socialità + ombra" / "solo permeabilità" / "bambini 6-10 anni"
- **Vincoli**: "budget basso" / "manutenzione bassa" / "vento forte"
- **Dimensioni**: "cortile 200m²" / "parcheggio grande"

### 3. Ricevi 3 output:

✅ **Configurazione Arredo Verde**: quali elementi e quanti (panchine, pergolati, planter)

✅ **Parametri Grasshopper**: valori numerici pronti per i tuoi slider

✅ **Vegetazione**: specie native adatte al clima specifico

---

## 🛠️ Integrazione con Grasshopper

### Metodo Base (Manuale - 2 minuti)

1. **Copia i parametri** dal blocco ``` ```
2. **Apri il tuo file Grasshopper**
3. **Imposta gli slider** con i valori dell'AI:

   Esempio output AI:
```
   panchina_A: L=[2.4], W=[0.6], H=[0.45], moduli=[3], veg_h=[1.2]
```
   
   Nel tuo file .gh:
```
   Slider "L_panchina" → 2.4
   Slider "W_panchina" → 0.6
   Slider "H_panchina" → 0.45
   Slider "moduli_panchina" → 3
   Slider "veg_h_panchina" → 1.2
```

4. **La geometria si aggiorna automaticamente!**

### Metodo Avanzato (File Template .gh)

Puoi creare un file Grasshopper con questi 3 arredi parametrici:

---

#### 🪑 **Arredo 1: Panchina Vegetata Modulare**

**Sliders necessari:**
- `L_panchina` (lunghezza, m): 0.5 → 5.0
- `W_panchina` (larghezza, m): 0.3 → 1.5
- `H_panchina` (altezza seduta, m): 0.3 → 0.8
- `moduli_panchina` (numero): 1 → 6 (integer)
- `veg_h_panchina` (altezza vegetazione, m): 0.5 → 2.5
- `veg_dens_panchina` (densità %, 0-100): 0 → 100
- `perm_panchina` (permeabilità %, non usato visivamente): 0 → 100

**Script Python** (componente Python in GH):
```python
import Rhino.Geometry as rg

sedute = []
planter = []
vegetazione = []

modulo_L = L / moduli

for i in range(moduli):
    x = i * modulo_L
    
    # Seduta
    base_pt = rg.Point3d(x, 0, 0)
    seduta = rg.Box(
        rg.Plane(base_pt, rg.Vector3d.ZAxis),
        rg.Interval(0, modulo_L * 0.6),
        rg.Interval(0, W),
        rg.Interval(0, H)
    ).ToBrep()
    sedute.append(seduta)
    
    # Planter + vegetazione
    if veg_dens > 0:
        planter_pt = rg.Point3d(x + modulo_L * 0.65, 0, 0)
        planter_box = rg.Box(
            rg.Plane(planter_pt, rg.Vector3d.ZAxis),
            rg.Interval(0, modulo_L * 0.3),
            rg.Interval(0, W),
            rg.Interval(0, H * 1.2)
        ).ToBrep()
        planter.append(planter_box)
        
        veg_center = rg.Point3d(planter_pt.X + modulo_L * 0.15, W / 2, H * 1.2)
        veg_radius = (modulo_L * 0.3) * (veg_dens / 100.0) * 0.5
        veg = rg.Cylinder(rg.Circle(veg_center, veg_radius), veg_h).ToBrep(True, True)
        vegetazione.append(veg)

a = sedute
b = planter
c = vegetazione
```

---

#### 🏛️ **Arredo 2: Pergolato Ombreggiante**

**Sliders:**
- `luce_pergolato` (luce tra pilastri, m): 2.0 → 5.0
- `passo_pergolato` (spaziatura pilastri, m): 1.0 → 3.0
- `h_tot_pergolato` (altezza totale, m): 2.0 → 4.0
- `copertura_pergolato` (% ombra, 0-100): 0 → 100
- `veg_h_pergolato` (altezza vegetazione, m): 1.5 → 3.5

**Script Python:**
```python
import Rhino.Geometry as rg
import math

pilastri = []
travi = []
copertura_veg = []

n_pilastri = int(math.ceil(luce / passo)) + 1

for i in range(n_pilastri):
    x = i * passo
    base = rg.Point3d(x, 0, 0)
    pilastro = rg.Cylinder(rg.Circle(base, 0.075), h_tot).ToBrep(True, True)
    pilastri.append(pilastro)
    
    if i < n_pilastri - 1:
        trave_start = rg.Point3d(x, 0, h_tot)
        trave_end = rg.Point3d(x + passo, 0, h_tot)
        trave_line = rg.Line(trave_start, trave_end)
        trave = rg.Cylinder(rg.Circle(trave_start, 0.05), trave_line.Length).ToBrep(True, True)
        travi.append(trave)

if copertura > 0:
    rect = rg.Rectangle3d(
        rg.Plane(rg.Point3d(0, -0.3, h_tot + 0.2), rg.Vector3d.ZAxis),
        (n_pilastri - 1) * passo, 0.6
    ).ToNurbsCurve()
    copertura_srf = rg.Surface.CreateExtrusion(rect, rg.Vector3d(0, 0, veg_h * (copertura / 100.0)))
    copertura_veg.append(copertura_srf.ToBrep())

a = pilastri
b = travi
c = copertura_veg
```

---

#### 🪴 **Arredo 3: Planter Modulare**

**Sliders:**
- `L_planter` (lunghezza, m): 0.5 → 3.0
- `W_planter` (larghezza, m): 0.5 → 2.0
- `H_planter` (altezza, m): 0.3 → 1.2
- `moduli_planter` (numero): 1 → 8 (integer)
- `veg_h_planter` (altezza vegetazione, m): 0.5 → 2.5
- `veg_dens_planter` (densità %, 0-100): 0 → 100

**Script Python:**
```python
import Rhino.Geometry as rg

contenitori = []
vegetazione = []

for i in range(moduli):
    x = i * (L + 0.2)
    base = rg.Point3d(x, 0, 0)
    planter = rg.Box(
        rg.Plane(base, rg.Vector3d.ZAxis),
        rg.Interval(0, L),
        rg.Interval(0, W),
        rg.Interval(0, H)
    ).ToBrep()
    contenitori.append(planter)
    
    if veg_dens > 0:
        veg_center = rg.Point3d(x + L/2, W/2, H)
        veg_radius = min(L, W) * 0.4 * (veg_dens / 100.0)
        veg = rg.Cylinder(rg.Circle(veg_center, veg_radius), veg_h).ToBrep(True, True)
        vegetazione.append(veg)

a = contenitori
b = vegetazione
```

---

## 💡 Idee per la Tesi

### 1. **Varianti Multiple Rapidissime**
Genera 5 contesti diversi nel chatbot → 5 set di parametri → 5 progetti 3D in minuti

### 2. **Documentazione NbS**
Usa le specie vegetali suggerite dall'AI per:
- Schede botaniche
- Calcoli benefici ecosistemici (ombra, permeabilità)
- Giustificazioni delle scelte progettuali

### 3. **Confronti Parametrici**
"Stesso sito, 3 budget diversi" → l'AI si adatta automaticamente

### 4. **Adattabilità Territoriale**
Dimostra come lo stesso sistema si adatta a: Milano, Palermo, Bologna

---

## 📩 Supporto

Creato con ❤️ per la tua tesi sulle oasi urbane.

Per domande tecniche su Grasshopper, consulta: [McNeel Forum](https://discourse.mcneel.com/c/grasshopper)

**Buon lavoro Giorgia! 🌿🎓**
    """)