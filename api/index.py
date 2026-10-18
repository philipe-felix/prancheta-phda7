import os
import json
from fastapi import FastAPI, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Permite que o HTML (frontend) converse com esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração segura de caminhos para a Vercel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCALES_DIR = os.path.join(BASE_DIR, "locales")

LOCALES = {}
SUPPORTED_LANGUAGES = ["en", "pt"]

for lang in SUPPORTED_LANGUAGES:
    filepath = os.path.join(LOCALES_DIR, f"{lang}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            LOCALES[lang] = json.load(file)

def get_translations(accept_language: str = Header(default="en")):
    lang_code = "pt" if "pt" in accept_language.lower() else "en"
    return LOCALES.get(lang_code, LOCALES["en"])

class PlayerData(BaseModel):
    current_ovr: float
    target_ovr: float

@app.get("/api/interface")
def get_ui_text(t: dict = Depends(get_translations)):
    return {"textos": t}

@app.post("/api/calcular")
def calcular_treino(dados: PlayerData, t: dict = Depends(get_translations)):
    if dados.current_ovr >= dados.target_ovr:
        return {"erro": t["error_logic"]}
    
    # Simulação provisória de cálculo (expanda a matemática do Top Eleven aqui depois)
    diff = dados.target_ovr - dados.current_ovr
    maletas_estimadas = int(diff * 20)
    
    return {
        "mensagem": t["success_calc"].format(maletas=maletas_estimadas),
        "maletas": maletas_estimadas
    }