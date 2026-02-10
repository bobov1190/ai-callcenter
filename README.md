# AI Call Center 🤖

Голосовой AI ассистент на русском языке.

**Stack:** FastAPI, Faster-Whisper, Mistral AI, Silero TTS

## 🚀 Быстрый деплой на Render

1. Fork этот репозиторий
2. Зарегистрируйтесь на [render.com](https://render.com)
3. New → Web Service → Выберите репозиторий
4. Добавьте переменную окружения: `MISTRAL_API_KEY` (получить на [console.mistral.ai](https://console.mistral.ai))
5. Deploy!

Готово! Приложение будет доступно на `https://your-app.onrender.com`

## 📋 Локальный запуск

```bash
# Клонирование
git clone <url>
cd telephoneApi

# Установка
python -m venv env
env\Scripts\activate  # Windows
pip install -r requirements.txt

# Настройка
copy .env.example .env
# Добавьте MISTRAL_API_KEY в .env

# Запуск
python main.py
```

Откройте: `http://localhost:8000`

## 📁 Структура

```
telephoneApi/
├── main.py              # Backend
├── static/index.html    # Frontend
├── requirements.txt     # Зависимости
├── render.yaml          # Конфиг Render
└── .env                 # Ключи (не в git!)
```

## ⚙️ API

- `GET /` - Веб-интерфейс
- `GET /api/health` - Статус
- `POST /api/voice-message` - Голосовой запрос
- `POST /api/text-only` - Текстовый запрос

## 📝 License

MIT
