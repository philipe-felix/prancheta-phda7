import os
import json
import asyncio
import httpx
from fastapi import FastAPI, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

def get_translations(accept_language: str = Header(default="en")):
    lang_code = "pt" if "pt" in accept_language.lower() else "en"
    return LOCALES.get(lang_code, LOCALES["en"])

class PlayerData(BaseModel):
    current_ovr: float
    target_ovr: float

API_BASE_URL = "https://sua-api-evolution.com" 
API_KEY = "SUA_API_KEY_AQUI"            
INSTANCE_NAME = "NOME_DA_SUA_INSTANCIA"        

HEADERS = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

async def send_typing_presence(remote_jid: str):
    url = f"{API_BASE_URL}/chat/sendPresence/{INSTANCE_NAME}"
    payload = {"number": remote_jid, "presence": "composing", "delay": 10000}
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, headers=HEADERS)
        except Exception:
            pass

async def send_text_message(remote_jid: str, text: str):
    url = f"{API_BASE_URL}/message/sendText/{INSTANCE_NAME}"
    payload = {"number": remote_jid, "text": text}
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, headers=HEADERS)
        except Exception:
            pass

async def reject_call(remote_jid: str, call_id: str):
    print(f"[{remote_jid}] Chamada rejeitada. ID: {call_id}")

async def process_and_reply(remote_jid: str, text_reply: str):
    await send_typing_presence(remote_jid)
    delay_seconds = max(1.0, len(text_reply) / 50.0)
    await asyncio.sleep(delay_seconds)
    await send_text_message(remote_jid, text_reply)

def get_menu_response(incoming_text: str) -> str:
    text_clean = incoming_text.strip().lower()
    if text_clean == "1":
        return "🛠️ *Pacote Trator (Farm de Maletas)* selecionado.\n\nPara iniciar, preciso que me confirme a quantidade de maletas que deseja farmar."
    elif text_clean == "2":
        return "🧬 *Pacote Mutante (Evolução de 1% a 180%)* selecionado.\n\nPor favor, informe a posição do jogador que vamos transformar num mutante."
    elif text_clean == "3":
        return "👤 Certo! Vou transferir o seu atendimento para o *PHDA7*."
    else:
        return "Olá! Sou o assistente virtual do *PHDA7*. 🤖⚽\n\nQual serviço de Top Eleven você precisa automatizar hoje? Digite o número:\n\n1️⃣ Pacote Trator\n2️⃣ Pacote Mutante\n3️⃣ Falar com o PHDA7"

@app.get("/api/interface")
def get_ui_text(t: dict = Depends(get_translations)):
    return {"textos": t}

@app.post("/api/calcular")
def calcular_treino(dados: PlayerData, t: dict = Depends(get_translations)):
    if dados.current_ovr >= dados.target_ovr:
        return {"erro": t["error_logic"]}
    diff = dados.target_ovr - dados.current_ovr
    return {"mensagem": t["success_calc"].format(maletas=int(diff * 20)), "maletas": int(diff * 20)}

@app.post("/webhook")
async def webhook_receiver(request: Request):
    try:
        payload = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON"}

    event_type = payload.get("event")
    
    if event_type == "call.received":
        call_data = payload.get("data", [])[0] if payload.get("data") else {}
        if remote_jid := call_data.get("from"):
            await reject_call(remote_jid, call_data.get("id"))
            await process_and_reply(remote_jid, "Este canal é automatizado e exclusivo para atendimento via texto. Não recebemos ligações.")
        return {"status": "ok"}

    if event_type == "messages.upsert":
        data = payload.get("data", {})
        if data.get("key", {}).get("fromMe") or "status@broadcast" in data.get("key", {}).get("remoteJid", ""):
            return {"status": "ignored"}

        remote_jid = data.get("key", {}).get("remoteJid")
        message_type = data.get("messageType")
        
        if message_type in ["audioMessage", "imageMessage", "videoMessage", "stickerMessage", "documentMessage", "pttMessage", "audio", "ptt", "video", "image"]:
            await process_and_reply(remote_jid, "Desculpe, o meu sistema é focado exclusivamente em texto. Por favor, escreva a sua dúvida.")
            return {"status": "ok"}
        
        if message_type in ["conversation", "extendedTextMessage"]:
            incoming_text = data.get("message", {}).get("conversation") or data.get("message", {}).get("extendedTextMessage", {}).get("text", "")
            await process_and_reply(remote_jid, get_menu_response(incoming_text))
            
        return {"status": "ok"}

    return {"status": "unhandled_event"}