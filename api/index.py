import os
import json
from fastapi import FastAPI, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Blindagem de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dicionários embutidos na RAM (Anti-Falha)
DEFAULT_PT = {
  "app_title": "Sindicato FC - Calculadora",
  "label_current": "GRL Atual (%)",
  "label_target": "GRL Desejado (%)",
  "btn_calc": "Calcular Evolução",
  "error_logic": "O GRL Desejado deve ser maior que o Atual.",
  "success_calc": "Você precisará de aproximadamente {maletas} maletas."
}
DEFAULT_EN = {
  "app_title": "Sindicato FC - Calculator",
  "label_current": "Current OVR (%)",
  "label_target": "Target OVR (%)",
  "btn_calc": "Calculate Growth",
  "error_logic": "Target OVR must be higher than Current.",
  "success_calc": "You will need approximately {maletas} rests."
}

LOCALES = {"pt": DEFAULT_PT, "en": DEFAULT_EN}

# Tenta carregar ficheiros físicos de forma segura
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOCALES_DIR = os.path.join(BASE_DIR, "locales")
    for lang in ["en", "pt"]:
        filepath = os.path.join(LOCALES_DIR, f"{lang}.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as file:
                LOCALES[lang] = json.load(file)
except Exception:
    pass

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
    
    # Motor de Cálculo Base
    diff = dados.target_ovr - dados.current_ovr
    maletas_estimadas = int(diff * 20)
    
    return {
        "mensagem": t["success_calc"].format(maletas=maletas_estimadas),
        "maletas": maletas_estimadas
    }