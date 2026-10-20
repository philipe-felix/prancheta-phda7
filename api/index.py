import os
import json
import asyncio
import httpx
from fastapi import FastAPI, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# =====================================================================
# 1. MIDDLEWARES E CONFIGURAÇÕES DA CALCULADORA (SEU CÓDIGO ORIGINAL)
# =====================================================================
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


# =====================================================================
# 2. CONFIGURAÇÕES DA API DO WHATSAPP (BOT NOVO)
# =====================================================================
# Substitua pelos seus dados reais
API_BASE_URL = "https://sua-api-evolution.com" 
API_KEY = "SUA_API_KEY_AQUI"            
INSTANCE_NAME = "NOME_DA_SUA_INSTANCIA"        

HEADERS = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}


# =====================================================================
# 3. FUNÇÕES ASSÍNCRONAS DO BOT
# =====================================================================
async def send_typing_presence(remote_jid: str):
    """Envia o evento de 'digitando...' (composing)"""
    url = f"{API_BASE_URL}/chat/sendPresence/{INSTANCE_NAME}"
    payload = {"number": remote_jid, "presence": "composing", "delay": 10000}
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, headers=HEADERS)
        except Exception as e:
            print(f"Erro presença: {e}")

async def send_text_message(remote_jid: str, text: str):
    """Envia a mensagem de texto final"""
    url = f"{API_BASE_URL}/message/sendText/{INSTANCE_NAME}"
    payload = {"number": remote_jid, "text": text}
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, headers=HEADERS)
        except Exception as e:
            print(f"Erro mensagem: {e}")

async def reject_call(remote_jid: str, call_id: str):
    """Lógica para rejeitar chamada (se aplicável via API)"""
    print(f"[{remote_jid}] Chamada rejeitada. ID: {call_id}")

async def process_and_reply(remote_jid: str, text_reply: str):
    """Executa a Regra 3 (Simulação de Digitação) compatível com Vercel"""
    await send_typing_presence(remote_jid)
    
    # Delay otimizado: 1s para cada 50 caracteres, min de 1s.
    delay_seconds = max(1.0, len(text_reply) / 50.0)
    await asyncio.sleep(delay_seconds)
    
    await send_text_message(remote_jid, text_reply)

def get_menu_response(incoming_text: str) -> str:
    """Árvore de decisão baseada em texto simples."""
    text_clean = incoming_text.strip().lower()
    
    if text_clean == "1":
        return "🛠️ *Pacote Trator (Farm de Maletas)* selecionado.\n\nPara iniciar, preciso que me confirme a quantidade de maletas que deseja farmar. Responda com a quantidade desejada."
    elif text_clean == "2":
        return "🧬 *Pacote Mutante (Evolução de 1% a 180%)* selecionado.\n\nÓtima escolha! Por favor, informe a posição do jogador que vamos transformar num mutante."
    elif text_clean == "3":
        return "👤 Certo! Vou transferir o seu atendimento para o *PHDA7*. Por favor, aguarde um momento que ele já irá assumir a conversa."
    else:
        return (
            "Olá! Sou o assistente virtual do *PHDA7*. 🤖⚽\n\n"
            "Qual serviço de Top Eleven você precisa automatizar hoje? Digite o número da opção desejada:\n\n"
            "1️⃣ Pacote Trator (Farm de Maletas)\n"
            "2️⃣ Pacote Mutante (Evolução de Jogadores de 1% a 180%)\n"
            "3️⃣ Falar com o PHDA7"
        )


# =====================================================================
# 4. ROTAS DA CALCULADORA (MANTIDAS INTACTAS)
# =====================================================================
@app.get("/api/interface")
def get_ui_text(t: dict = Depends(get_translations)):
    return {"textos": t}

@app.post("/api/calcular")
def calcular_treino(dados: PlayerData, t: dict = Depends(get_translations)):
    if dados.current_ovr >= dados.target_ovr:
        return {"erro": t["error_logic"]}
    
    diff = dados.target_ovr - dados.current_ovr
    maletas_estimadas = int(diff * 20)
    
    return {
        "mensagem": t["success_calc"].format(maletas=maletas_estimadas),
        "maletas": maletas_estimadas
    }


# =====================================================================
# 5. ROTA DO WEBHOOK DO BOT DE WHATSAPP
# =====================================================================
@app.post("/webhook")
async def webhook_receiver(request: Request):
    """Endpoint principal para receber os eventos do WhatsApp"""
    try:
        payload = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON"}

    event_type = payload.get("event")
    
    # -----------------------------------------------------------------
    # REGRA 2: BARREIRA ANTI-CHAMADAS
    # -----------------------------------------------------------------
    if event_type == "call.received":
        call_data = payload.get("data", [])[0] if payload.get("data") else {}
        remote_jid = call_data.get("from")
        call_id = call_data.get("id")
        
        if remote_jid:
            await reject_call(remote_jid, call_id)
            reply = "Este canal é automatizado e exclusivo para atendimento via texto. Não recebemos ligações. Como posso ajudar com a sua conta?"
            await process_and_reply(remote_jid, reply)
            
        return {"status": "ok"}

    # -----------------------------------------------------------------
    # PROCESSAMENTO DE MENSAGENS
    # -----------------------------------------------------------------
    if event_type == "messages.upsert":
        data = payload.get("data", {})
        message_info = data.get("message", {})
        
        # Ignora mensagens do bot ou de status
        if data.get("key", {}).get("fromMe") or "status@broadcast" in data.get("key", {}).get("remoteJid", ""):
            return {"status": "ignored"}

        remote_jid = data.get("key", {}).get("remoteJid")
        message_type = data.get("messageType")
        
        # -------------------------------------------------------------
        # REGRA 1: FILTRO RESTRITO A TEXTO
        # -------------------------------------------------------------
        blocked_media_types = ["audioMessage", "imageMessage", "videoMessage", "stickerMessage", "documentMessage", "pttMessage", "audio", "ptt", "video", "image"]
        
        if message_type in blocked_media_types:
            reply = "Desculpe, o meu sistema de atendimento é focado exclusivamente em texto para garantir rapidez e registo correto dos pedidos. Por favor, escreva a sua dúvida ou o pacote que deseja."
            await process_and_reply(remote_jid, reply)
            return {"status": "ok"}
        
        # -------------------------------------------------------------
        # FLUXO NORMAL (Texto)
        # -------------------------------------------------------------
        if message_type in ["conversation", "extendedTextMessage"]:
            incoming_text = message_info.get("conversation") or message_info.get("extendedTextMessage", {}).get("text", "")
            reply = get_menu_response(incoming_text)
            
            await process_and_reply(remote_jid, reply)
            
        return {"status": "ok"}

    return {"status": "unhandled_event"}