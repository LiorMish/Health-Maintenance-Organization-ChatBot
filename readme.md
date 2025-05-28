# 🏥 Medical Chatbot

A two-tier RAG (**R**etrieval-**A**ugmented **G**eneration) chatbot for Israeli
HMOs.  
It combines:

* **FastAPI** – REST backend, validates profiles, calls the LLM.
* **Streamlit** – lightweight front-end chat UI.
* **Azure OpenAI** – both for answer generation and profile extraction.
* **Semantic search** over HTML knowledge-base snippets.

---

## ✨ Features

| Phase | What happens |
|-------|--------------|
| **Info-collection** | Chatbot extracts user profile fields (name, age. HMO, tier etc.,) from free-text and asks follow-up questions until complete. |
| **Q & A** | Bot uses the profile + semantic-search snippets to answer questions regarding HMO services. |

---

## ⚙️ Environment variables

Create **`.env`** in the repo app folder and add these fields (loaded automatically by `python-dotenv`):

```dotenv
# Document Intelligence
FORM_RECOGNIZER_ENDPOINT=
FORM_RECOGNIZER_KEY=

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_EMBEDDING=
AZURE_OPENAI_API_VERSION=2024-02-15-preview 
```

---

## 🔧 Quick-start

```bash
# 1 · Clone
git clone https://github.com/LiorMish/Health-Maintenance-Organization-ChatBot.git
cd Health-Maintenance-Organization-ChatBot

# 2.1 Optional - If you're on a system without direct package manager access:
conda create -n chatbot python=3.10 -y
conda activate chatbot

# 2.2 · Create Python 3.10 venv
python3.10 -m venv .venv
source .venv/bin/activate

# 3 · Install deps
pip install -r requirements.txt

# 4 · Supply API keys
cp .env.example .env  # copy the env file you created into Health-Maintenance-Organization-ChatBot directory
```

Now launch back-end and front-end in different terminals.
```bash
# 5 · Launch back-end
python app/main.py                 # http://localhost:8000  (hot-reloading: uvicorn main:app --reload)

# 6 · Launch front-end (new terminal) (cd Health-Maintenance-Organization-ChatBot)
streamlit run frontend/ui.py # --server.address 0.0.0.0 --server.port 8501
```
