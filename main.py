# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from mistralai import Mistral
from faster_whisper import WhisperModel
import torch
import tempfile
import os
import io
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
from scipy.io import wavfile
import base64

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🔄 Загрузка Faster-Whisper...")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
print("✅ Whisper загружен")

print("🔄 Загрузка Silero TTS...")
device = torch.device('cpu')
torch.set_num_threads(4)

model, _ = torch.hub.load(
    repo_or_dir='/silero-models',
    model='silero_tts',
    language='ru',
    speaker='v3_1_ru',
    source='local'
)
model.to(device)
print("✅ Silero TTS загружен")

mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

class AICallCenter:
    def __init__(self):
        self.conversations = {}
    
    def transcribe_audio(self, audio_path: str) -> str:
        try:
            segments, info = whisper_model.transcribe(
                audio_path, 
                language="ru",
                vad_filter=True
            )
            text = " ".join([segment.text for segment in segments])
            return text.strip()
        except Exception as e:
            print(f"❌ Ошибка Whisper: {e}")
            return ""
    
    def get_ai_response(self, user_text: str, call_id: str = "default") -> str:
        if call_id not in self.conversations:
            self.conversations[call_id] = [
                {
                    "role": "system",
                    "content": """Ты вежливый и профессиональный оператор колл-центра. 
                    Твоя задача - помогать клиентам, отвечать на вопросы кратко и по делу.
                    Всегда будь вежлив и дружелюбен. Отвечай на русском языке."""
                }
            ]
        
        self.conversations[call_id].append({
            "role": "user",
            "content": user_text
        })
        
        try:
            response = mistral_client.chat.complete(
                model="mistral-large-latest",
                messages=self.conversations[call_id],
                max_tokens=150
            )
            
            ai_text = response.choices[0].message.content
            
            self.conversations[call_id].append({
                "role": "assistant",
                "content": ai_text
            })
            
            return ai_text
            
        except Exception as e:
            print(f"❌ Ошибка Mistral: {e}")
            return "Извините, произошла ошибка. Попробуйте повторить ваш вопрос."
    
    def synthesize_speech(self, text: str) -> bytes:
        """Возвращает аудио как bytes для стриминга"""
        try:
            audio = model.apply_tts(
                text=text,
                speaker='xenia',
                sample_rate=24000
            )
            
            # Конвертируем в WAV bytes через scipy
            buffer = io.BytesIO()
            
            # Преобразуем tensor в numpy array
            audio_np = audio.cpu().numpy()
            # Нормализуем в int16
            audio_int16 = (audio_np * 32767).astype(np.int16)
            
            # Сохраняем в buffer
            wavfile.write(buffer, 24000, audio_int16)
            buffer.seek(0)
            
            return buffer.read()
            
        except Exception as e:
            print(f"❌ Ошибка TTS: {e}")
            raise

call_center = AICallCenter()

@app.post("/api/voice-message")
async def voice_message(
    audio: UploadFile = File(...),
    call_id: str = "default"
):
    """Обработка голосового сообщения"""
    
    try:
        # Сохраняем аудио во временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        print(f"📞 Обработка сообщения {call_id}")
        
        # 1. Распознавание
        print("🎤 Распознавание речи...")
        user_text = call_center.transcribe_audio(temp_path)
        print(f"👤 Пользователь: {user_text}")
        
        # Удаляем временный файл
        os.remove(temp_path)
        
        if not user_text:
            user_text = "..."
            ai_response = "Извините, я вас не расслышал. Повторите, пожалуйста."
        else:
            # 2. Получение ответа
            print("🤖 Генерация ответа...")
            ai_response = call_center.get_ai_response(user_text, call_id)
            print(f"🤖 AI: {ai_response}")
        
        # 3. Синтез речи
        print("🔊 Синтез речи...")
        audio_bytes = call_center.synthesize_speech(ai_response)
        
        print("✅ Готово!")
        
        # Кодируем текст в base64 для заголовков (чтобы избежать проблем с кириллицей)
        user_text_b64 = base64.b64encode(user_text.encode('utf-8')).decode('ascii')
        ai_response_b64 = base64.b64encode(ai_response.encode('utf-8')).decode('ascii')
        
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={
                "X-User-Text": user_text_b64,
                "X-AI-Response": ai_response_b64,
            }
        )
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/text-only")
async def text_only(data: dict):
    user_text = data.get("text", "")
    call_id = data.get("call_id", "test")
    
    if not user_text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    ai_response = call_center.get_ai_response(user_text, call_id)
    
    return {
        "user_text": user_text,
        "ai_response": ai_response,
        "call_id": call_id
    }

@app.post("/api/end-call/{call_id}")
async def end_call(call_id: str):
    if call_id in call_center.conversations:
        del call_center.conversations[call_id]
    return {"status": "ok", "message": f"Call {call_id} ended"}

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "whisper": "ready",
        "mistral": "ready",
        "silero": "ready"
    }

# Создаем папку static если нет
os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)