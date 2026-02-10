FROM python:3.11-slim

WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# CPU-версия torch
RUN pip install --no-cache-dir \
    torch==2.5.1 \
    torchaudio==2.5.1 \
    --index-url https://download.pytorch.org/whl/cpu

# Остальные зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Скачиваем Silero TTS во время сборки (кэшируется в слое) ---
RUN python -c "\
import torch; \
torch.hub.load('snakers4/silero-models', 'silero_tts', language='ru', speaker='v3_1_ru', trust_repo=True); \
print('Silero TTS downloaded OK')"

# Копируем код
COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
