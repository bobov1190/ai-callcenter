# 🚀 КОПИРУЙ И ВСТАВЛЯЙ

## Шаг 1: Загрузить на GitHub

```bash
cd D:\telephoneApi

git init
git add .
git commit -m "Ready for deploy"

# Создай новый репозиторий на github.com
# Потом выполни (замени YOUR_USERNAME):

git remote add origin https://github.com/YOUR_USERNAME/ai-callcenter.git
git branch -M main
git push -u origin main
```

## Шаг 2: Получить Mistral API ключ

1. Открыть: https://console.mistral.ai
2. Создать аккаунт
3. API Keys → Create new
4. Скопировать ключ

## Шаг 3: Деплой на Render

1. https://render.com → Sign up (через GitHub)
2. New + → Web Service
3. Connect Repository → ai-callcenter
4. Настройки подтянутся автоматом из render.yaml
5. Environment Variables → Add:
   ```
   MISTRAL_API_KEY = вставь_свой_ключ
   ```
6. Create Web Service
7. Жди 5-10 минут

## Готово!

Твое приложение: https://ai-callcenter-XXXX.onrender.com

---

## Обновление после изменений

```bash
git add .
git commit -m "Update"
git push
```

Render автоматом обновит за 2-3 минуты.
