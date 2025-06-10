# Tender Processing Orchestrator

Минималистичный оркестратор для последовательной обработки тендеров через микросервисы.

## 🎯 Назначение

Оркестратор принимает данные тендера и последовательно обрабатывает их через три сервиса:

1. **Классификатор** - добавляет коды ОКПД2 к товарам
2. **Стандартизатор** - приводит характеристики к стандартным значениям
3. **Сервис подбора** - находит подходящие товары из каталога

## 📁 Структура проекта

```
src/
├── api/
│   ├── dependencies.py      # Проверка API ключей
│   └── endpoints/
│       ├── tender.py        # Основной эндпоинт
│       └── health.py        # Health checks
├── core/
│   ├── config.py           # Конфигурация
│   └── exceptions.py       # Кастомные исключения
├── models/
│   └── tender.py           # Pydantic модели
├── services/
│   ├── orchestrator.py     # Бизнес-логика
│   └── service_client.py   # HTTP клиент
└── main.py                 # FastAPI приложение
```

## 🚀 Быстрый старт

### 1. Настройка окружения

```bash
cp .env.example .env
# Отредактируйте .env - добавьте API ключи сервисов
```

### 2. Запуск в Docker

```bash
docker-compose up -d
```

### 3. Проверка работоспособности

```bash
# Базовая проверка
curl http://localhost:8080/health

# Детальная проверка всех сервисов
curl http://localhost:8080/health/detailed
```

## 📡 API

### Обработка тендера

```http
POST /api/v1/process-tender
Content-Type: application/json
X-API-Key: {api_key}  # Если включена проверка

{
  "tenderInfo": {...},
  "items": [...],
  "generalRequirements": {...},
  "attachments": [...]
}
```

Ответ включает:
- Результаты подбора товаров
- Метрики времени обработки каждым сервисом

## ⚙️ Конфигурация

Все настройки через переменные окружения:

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `CLASSIFIER_URL` | URL сервиса классификации | http://classifier:8000/... |
| `STANDARDIZER_URL` | URL сервиса стандартизации | http://standardizer:8000/... |
| `MATCHER_URL` | URL сервиса подбора | http://matcher:8002/... |
| `*_API_KEY` | API ключи для сервисов | - |
| `REQUEST_TIMEOUT` | Таймаут запросов (сек) | 300 |
| `REQUIRE_API_KEY` | Требовать API ключ | false |

## 🔍 Мониторинг

- `/health` - статус оркестратора
- `/health/detailed` - статус всех сервисов
- Логи: `docker-compose logs -f orchestrator`

## 🏗️ Разработка

### Локальный запуск

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### Добавление нового сервиса

1. Добавьте URL и API ключ в `config.py`
2. Добавьте метод вызова в `service_client.py`
3. Добавьте шаг обработки в `orchestrator.py`

## 📝 Лицензия

MIT