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

# Клонируем Silero через git (git-протокол, без GitHub REST API — нет rate limit)
RUN git clone --depth 1 https://github.com/snakers4/silero-models /silero-models

# Скачиваем веса модели во время сборки (source='local' — пропускает API валидацию)
RUN python -c "\
import torch; \
model, _ = torch.hub.load('/silero-models', 'silero_tts', language='ru', speaker='v3_1_ru', source='local'); \
print('Silero TTS ready')"

# Копируем код
COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
