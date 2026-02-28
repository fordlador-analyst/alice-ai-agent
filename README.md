# Alice AI Agent

AI-ассистент для Яндекс Алисы на базе **n8n** + **Claude API (Anthropic)**.

Голосовой навык для Яндекс Колонки, который использует Claude как мозг — отвечает на вопросы умнее стандартной Алисы.

## Архитектура

```
Пользователь → Яндекс Колонка → Алиса → Webhook → n8n → Claude API → ответ → Алиса → Колонка
```

### Компоненты

| Компонент | Назначение |
|-----------|-----------|
| **Яндекс Колонка** | Голосовой ввод/вывод, распознавание и синтез речи |
| **Яндекс Диалоги** | Платформа навыков Алисы, маршрутизирует запросы на webhook |
| **Caddy** | Реверс-прокси с автоматическим HTTPS (Let's Encrypt) |
| **n8n** | Обработка запросов, AI Agent, инструменты (поиск, погода и др.) |
| **Claude API** | LLM от Anthropic — генерация ответов |

### Стек

- **Сервер:** VPS Ubuntu 22.04+
- **Контейнеризация:** Docker Compose
- **Реверс-прокси:** Caddy 2 (авто-HTTPS)
- **Оркестрация:** n8n (визуальный workflow)
- **LLM:** Claude Haiku 4.5 (Anthropic API)
- **Навык:** Яндекс Диалоги

## Структура проекта

```
alice-ai-agent/
├── docker-compose.yml      # Docker-сервисы: n8n + Caddy
├── Caddyfile               # Конфигурация реверс-прокси
├── Dockerfile              # Сборка Python-сервера (для локальной разработки)
├── server.py               # Автономный сервер для тестирования без n8n
├── requirements.txt        # Python-зависимости
├── .env.example            # Шаблон переменных окружения
├── .env                    # Секреты (не в git)
├── .gitignore              # Исключения для git
├── n8n-flows/
│   └── alice-agent.json    # Экспорт n8n workflow для импорта
└── README.md
```

## Быстрый старт

### 1. Подготовка сервера (Ubuntu 22.04+)

```bash
# Установить Docker
curl -fsSL https://get.docker.com | sh

# Склонировать репозиторий
git clone https://github.com/fordlador-analyst/alice-ai-agent.git /opt/alice
cd /opt/alice
```

### 2. Настройка окружения

```bash
# Создать .env с ключом шифрования n8n
echo "N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)" > .env
```

> Anthropic API ключ настраивается внутри n8n через UI (Credentials).

### 3. Настройка домена

В файле `docker-compose.yml` и `Caddyfile` замените домен на свой.

Если домена нет — используйте nip.io: `YOUR-IP.nip.io` (замените точки на дефисы).

Направьте A-запись домена на IP сервера.

### 4. Запуск

```bash
docker compose up -d
```

Откройте `https://ваш-домен` — создайте аккаунт n8n (первый пользователь становится админом).

### 5. Импорт workflow

1. В n8n: **New Workflow** → **...** (меню) → **Import from URL**
2. URL: `https://raw.githubusercontent.com/fordlador-analyst/alice-ai-agent/main/n8n-flows/alice-agent.json`
3. Откройте нод **Anthropic Chat Model** → создайте credential с API ключом из [console.anthropic.com](https://console.anthropic.com)
4. Активируйте workflow (тумблер вверху справа)

### 6. Регистрация навыка Алисы

1. Перейдите на [dialogs.yandex.ru](https://dialogs.yandex.ru)
2. Создайте новый навык → **Навык в Алисе**
3. Webhook URL: `https://ваш-домен/webhook/alice`
4. Заполните название, описание, выберите голос
5. Включите тестирование на устройствах

### 7. Проверка

На колонке скажите:

> «Алиса, запусти навык [название вашего навыка]»

## n8n Workflow

Workflow состоит из следующих нодов:

```
[Alice Webhook] → [New Session?] → true  → [Greeting] (приветствие)
                                  → false → [AI Agent] → [AI Response]
                                               ↕
                                    [Anthropic Chat Model]
```

| Нод | Тип | Назначение |
|-----|-----|-----------|
| Alice Webhook | Webhook (POST /alice) | Принимает запросы от Алисы |
| New Session? | If | Проверяет: новая сессия или продолжение |
| Greeting | Respond to Webhook | Отправляет приветствие при запуске навыка |
| AI Agent | LangChain Agent | Обрабатывает вопрос через Claude |
| Anthropic Chat Model | LLM | Модель Claude Haiku 4.5 |
| AI Response | Respond to Webhook | Формирует ответ в формате Алисы |

### Формат ответа Алисе

```json
{
  "response": {
    "text": "Текст ответа",
    "tts": "Текст для озвучивания",
    "end_session": false
  },
  "version": "1.0"
}
```

## Локальная разработка

Для тестирования без n8n можно использовать автономный Python-сервер:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python server.py
```

Тест:
```bash
curl -X POST http://localhost:5001/alice \
  -H "Content-Type: application/json" \
  -d '{"session":{"new":false},"request":{"command":"Привет"},"version":"1.0"}'
```

## Деплой обновлений

```bash
# На сервере
cd /opt/alice
git pull
docker compose up -d --build
```

## Roadmap

- [x] Фаза 1: Базовый ассистент (Claude отвечает на вопросы)
- [ ] Фаза 2: Поиск в интернете, погода, курсы валют
- [ ] Фаза 3: Google Calendar, заметки, утренний брифинг
- [ ] Фаза 4: Умный дом (Home Assistant)

## Стоимость

| Компонент | Цена |
|-----------|------|
| VPS (1 CPU, 2 GB RAM) | ~300-500 ₽/мес |
| Anthropic API (Claude Haiku) | ~$0.01-0.05 за запрос |
| n8n (self-hosted) | Бесплатно |
| Яндекс Диалоги | Бесплатно |
| Caddy + Let's Encrypt | Бесплатно |
