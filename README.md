# Маршруты API маркетплейсов

Единый каталог HTTP-маршрутов Wildberries, Ozon и Яндекс Маркета для разработчиков интеграций. Данные доступны в JSON и CSV, без токенов и личных данных продавцов.

**Дата сборки: 25.09.2026.** Это дата подготовки каталога, а не подтверждение доступности каждого метода в рабочем API. Статус `current_status: not_live_verified` в каждом JSON означает, что маршруты получены из спецификаций, но не проверены рабочими запросами.

| Маркетплейс | Операций | Снимок источника | Происхождение |
| --- | ---: | --- | --- |
| [Wildberries](wildberries/routes.json) ([CSV](wildberries/routes.csv)) | 290 | 14.05.2026 | [Стороннее зеркало](https://github.com/bigancientmammoth/wb-swagger/tree/d6cb5a3ca0f2fad242ad3297926d802c45fd49c5/original/ru) официальных Swagger-файлов |
| [Ozon](ozon/routes.json) ([CSV](ozon/routes.csv)) | 511 | 19.08.2026 | [Сторонний снимок](https://github.com/MissiaL/ozon-api/tree/1953152c36955225b459cf55963a2c3a7a234661/references) Seller API (463) и Performance API (48) |
| [Яндекс Маркет](yandex-market/routes.json) ([CSV](yandex-market/routes.csv)) | 169 | 22.09.2026 | [Официальный OpenAPI-репозиторий](https://github.com/yandex-market/yandex-market-partner-api/tree/321c272cfe218c21fd1644242cef205b6c9b8dbe/openapi) |

**Итого: 970 операций.** Каталоги содержат метод, путь, домен и полный URL, краткое название, теги, признак `deprecated`, ссылку на официальную документацию и исходный файл. `deprecated: false` означает лишь отсутствие соответствующего флага в исходной спецификации.

Для Wildberries и Ozon прямую автоматическую загрузку с официальных порталов 25.09.2026 заблокировала антибот-защита. Поэтому их снимки могут не содержать более поздних изменений. Перед подключением маршрута перепроверяйте его параметры, авторизацию, лимиты и статус в [документации Wildberries](https://dev.wildberries.ru/docs/openapi/api-information), [Ozon Seller API](https://docs.ozon.ru/api/seller/), [Ozon Performance API](https://docs.ozon.ru/api/performance/) или [документации Яндекс Маркета](https://yandex.ru/dev/market/partner-api/doc/ru/).

## Как использовать

```bash
git clone https://github.com/x-mp/marketplace-api-routes.git
cd marketplace-api-routes
python - <<'PY'
import json
for marketplace in ('wildberries', 'ozon', 'yandex-market'):
    routes = json.load(open(f'{marketplace}/routes.json', encoding='utf-8'))['routes']
    for route in routes:
        if 'stocks' in route['path'] and not route['deprecated']:
            print(marketplace, route['method'], *route['urls'])
PY
```

CSV подходит для таблиц; при нескольких доменах у метода создаётся по строке на домен. JSON сохраняет одну запись на HTTP-операцию и массив URL.

## Пересборка

```bash
python -m pip install -r requirements.txt
python scripts/build_wb.py
python scripts/build_others.py ozon
python scripts/build_others.py yandex-market
```

Скрипты используют закреплённые коммиты источников для воспроизводимости. Для нового снимка обновите commit и дату источника в соответствующем скрипте, проверьте происхождение спецификации и пересоберите каталог. Для локальных исходников доступны `--source-dir`; у Яндекс Маркета это корень клонированного репозитория. Простая смена даты сборки не делает маршруты актуальными.

Производные данные Wildberries основаны на [зеркале под MIT](https://github.com/bigancientmammoth/wb-swagger/blob/main/LICENSE); первичная документация принадлежит Wildberries. Официальная спецификация Яндекс Маркета опубликована под [BSD-3-Clause](https://github.com/yandex-market/yandex-market-partner-api/blob/main/LICENSE). Каталог содержит только факты о маршрутах и короткие названия методов, а не полные тексты спецификаций.
