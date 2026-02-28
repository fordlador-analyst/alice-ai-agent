# Alice AI Agent

AI-агент для Яндекс Алисы на базе n8n + Claude API.

Алиса → n8n (webhook) → Claude API + поиск → ответ → Алиса

## Быстрый старт

### 1. Подготовка сервера (Ubuntu 22.04+)

```bash
# Установить Docker
curl -fsSL https://get.docker.com | sh

# Клонировать репозиторий
git clone https://github.com/fordlador-analyst/alice-ai-agent.git
cd alice-ai-agent
```

### 2. Настройка

```bash
cp .env.example .env
nano .env
```

Заполните:
- `N8N_HOST` — ваш домен (например, n8n.mysite.com)
- `N8N_ENCRYPTION_KEY` — сгенерируйте: `openssl rand -hex 32`
- `ANTHROPIC_API_KEY` — ключ из console.anthropic.com

### 3. Запуск

```bash
docker compose up -d
```

Откройте `https://ВАШ_ДОМЕН` — создайте аккаунт n8n.

### 4. Импорт флоу

Импортируйте `n8n-flows/alice-agent.json` через n8n UI.

### 5. Регистрация навыка Алисы

1. Перейдите на https://dialogs.yandex.ru
2. Создайте новый навык
3. Укажите webhook URL: `https://ВАШ_ДОМЕН/webhook/alice`
