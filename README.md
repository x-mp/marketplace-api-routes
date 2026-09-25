# Маршруты API маркетплейсов

Каталог HTTP-маршрутов для интеграций с маркетплейсами. Сейчас включён Wildberries; структура позволяет добавить Ozon и Яндекс Маркет отдельными каталогами.

**Дата сборки каталога: 25.09.2026.** Источник данных Wildberries — [снимок 13 OpenAPI-спецификаций от 14.05.2026](https://github.com/bigancientmammoth/wb-swagger/tree/d6cb5a3ca0f2fad242ad3297926d802c45fd49c5/original/ru), перепубликованный сторонним проектом с [официального портала WB API](https://dev.wildberries.ru/). При сборке 25.09.2026 прямой доступ к порталу для автоматической загрузки вернул антибот-страницу/HTTP 498. Поэтому **актуальность каждого маршрута на 25.09.2026 не подтверждена**. Дата сборки не равна дате проверки маршрутов в рабочем API.

## Wildberries

- [JSON-каталог](wildberries/routes.json): 290 операций из 13 категорий, включая HTTP-метод, путь, домен, URL, теги, признак `deprecated` и ссылку на официальную категорию.
- [CSV-каталог](wildberries/routes.csv): удобен для поиска и таблиц. Если у метода несколько доменов, каждый домен занимает отдельную строку.
- [Официальная документация](https://dev.wildberries.ru/docs/openapi/api-information) и [Swagger](https://dev.wildberries.ru/swagger/products) — первичный источник для перепроверки маршрута перед использованием.

Пример поиска:

```bash
python - <<'PY'
import json
routes = json.load(open('wildberries/routes.json', encoding='utf-8'))['routes']
for route in routes:
    if 'stocks' in route['path'] and not route['deprecated']:
        print(route['method'], *route['urls'])
PY
```

Каталог описывает маршруты, а не доступность метода конкретному токену. Для вызова проверяйте описание метода, права токена, параметры и лимиты на официальном портале. Запись `deprecated: false` означает только отсутствие флага устаревания в исходном снимке.

## Обновление

```bash
python -m pip install -r requirements.txt
python scripts/build_wb.py
```

Скрипт скачивает закреплённый снимок и проверяет формат OpenAPI. Для новой версии необходимо поменять `COMMIT` и `SNAPSHOT_DATE` в скрипте, проверить источник и заново сгенерировать файлы. При доступе к оригинальным YAML можно передать `--source-dir`. Смена даты сборки сама по себе не подтверждает актуальность спецификаций.

## Дальнейшее расширение

Для Ozon и Яндекс Маркета будут добавлены `ozon/routes.json` и `yandex-market/routes.json` с теми же основными полями и отдельной информацией об источнике и дате. Их маршруты в текущий каталог **не включены**.

Источник производного каталога Wildberries: [bigancientmammoth/wb-swagger](https://github.com/bigancientmammoth/wb-swagger), лицензия [MIT](https://github.com/bigancientmammoth/wb-swagger/blob/main/LICENSE). Официальная документация принадлежит Wildberries.
