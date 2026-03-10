# Currency ETL Pipeline 

Проект реализует ETL-пайплайн для загрузки курсов валют из API Европейского центрального банка (ECB), трансформации данных и записи результата в ClickHouse с оркестрацией через Apache Airflow.

В рамках задания реализованы два DAG:
- `maintenance_currency_dag` — для загрузки данных за указанный период
- `integration_currency_dag` — для ежедневной загрузки данных за предыдущий день


## What the Project does

### Data Sourse
Используется API Европейского центрального банка (ECB) для получения курсов валют.

### Currency
В проекте обрабатываются данные для:
- USD
- EUR

### Result
После обработки данные приводятся к формату, подходящему для записи в таблицу `currency` в ClickHouse.

Каждая строка содержит:
- `id` — уникальный UUID
- `date` — дата курса
- `usd` — всегда `1.0`
- `euro` — значение EUR по отношению к USD
- `created` — время создания записи
- `updated` — `NULL`


## Pipeline Architecture

```
ECB API
   ↓
Airflow DAG: maintenance_currency_dag
   ↓
fetch → transform
   ↓
Airflow DAG: integration_currency_dag
   ↓
insert_batch()
   ↓
ClickHouse
```

## Tech Stack

- Python

- Apache Airflow

- ClickHouse

- Docker / Docker Compose

- Pandas

- Requests


## Project Structure

```
tech_task1
│
├── dags
│   ├── integration_dag.py
│   └── maintenance_dag.py
│
├── src
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   └── ecb_client.py
│   ├── processing
│   │   ├── __init__.py
│   │   └── transform.py
│   └── db
│       ├── __init__.py
│       └── clickhouse_client.py
│
├── sql
│   └── currency_table.sql
│
├── screenshots
│   ├── integration.png
│   ├── maintenance.png
│   ├── airflow_dag_success.png
│   └── data_stored_in_clickhouse.png
│   └── data_stored_in_clickhouse2.png
│
├── docker-compose.yml
├── requirements.txt
├── test_ecb_rates.py
└── README.md
```


## DAG Overview

### 1. maintenance_currency_dag

DAG для загрузки исторических данных за заданный период.

Функциональность:

- принимает start_date и end_date

- получает данные из ECB API

- выполняет трансформацию

- подготавливает список словарей в формате, подходящем для БД

Используется для ручной или тестовой загрузки данных за период.

### 2. integration_currency_dag

DAG для ежедневной интеграции данных.

Функциональность:

- при запуске берет данные за предыдущий день

- использует ту же логику получения и трансформации данных

- записывает результат в ClickHouse

Используется как основной DAG интеграции.


## Формат итоговых данных

Пример итоговой записи:

```
{
  "id": "8d1f8b5a-8a4f-4db5-8d72-1a2b3c4d5e6f",
  "date": "2024-01-02",
  "usd": 1.0,
  "euro": 1.0956,
  "created": "2026-03-10 15:30:00",
  "updated": null
}
```


## DDL таблицы ClickHouse

```
CREATE TABLE IF NOT EXISTS currency
(
    id UUID,
    date Date,
    usd Float64,
    euro Float64,
    created DateTime,
    updated Nullable(DateTime)
)
ENGINE = MergeTree()
ORDER BY date;
```


## Запуск проекты локально:

1. Клонировать репозиторий

```
git clone https://github.com/maria-python/fx-rates-pipeline.git
cd fx-rates-pipeline
```

2. Поднять сервисы

```
docker compose up --build
```

4. Открыть Airflow & ClickHouse

Airflow address: ` http://localhost:8080 `

Login: ` admin `

Password: ` admin `

ClickHouse address: ` http://localhost:8124 `

Login: ` default `

Password: ` admin1234 `


## Локальная проверка Python-logic

Для быстрой проверки получения и трансформации данных можно выполнить:

```
python3 test_ecb_rates.py
```

Ожидаемый результат:

- вывод RAW DATA

- вывод TRANSFORMED DATA

Это подтверждает, что:

- API-запрос работает

- трансформация выполняется корректно

- итоговая структура соответствует требованиям задания


## Task Summary

В рамках задания реализовано:

- два DAG с требуемыми именами

- загрузка данных из ECB API

- трансформация данных в требуемую структуру

- добавление технических полей id, created, updated

- DDL таблицы currency для ClickHouse

- запись данных в ClickHouse

- Docker Compose c сервисами Airflow и ClickHouse

- локальный воспроизводимый запуск


## Implementation Steps

В процессе выполнения задания возникло несколько технических задач, связанных с настройкой инфраструктуры и интеграцией сервисов.

Основные сложности в процессе разработки:

1. Конфликт портов Docker

При первом запуске возникла ошибка занятости порта ClickHouse:

```
Bind for 0.0.0.0:8123 failed: port is already allocated
```

Что было сделано:

- проверены уже запущенные контейнеры

- изменены порты в docker-compose.yml

- очищены старые контейнеры и volumes

2. Несовместимость typing из-за версии Python в Airflow

Airflow внутри контейнера использовал Python 3.8, из-за чего аннотация list[str] вызывала ошибку.

Что было сделано:

- заменено на List[str] из typing

3. Ошибка аутентификации ClickHouse

На этапе интеграции DAG не мог записать данные в ClickHouse из-за расхождения в конфигурации пользователя и пароля.

Что было сделано:

- проверена конфигурация пользователя default

- синхронизированы настройки пароля в ClickHouse и в clickhouse_client.py

- соединение дополнительно проверено напрямую из контейнера Airflow

4. Ошибка типов при вставке

После исправления соединения возникла ошибка вставки, связанная с тем, что ClickHouse ожидал тип Date, а в коде передавалась строка.

Что было сделано:

- поле date было приведено к типу datetime.date до вставки

5. Проверка данных ECB

При тестировании локально данные начинались не с 2024-01-01, а с 2024-01-02.

Это нормальное поведение, так как:

- ECB не всегда возвращает данные на выходные и праздники

- 1 января может отсутствовать в ответе API


## Improvements

Что можно улучшить дальше:

Если бы на задачу было больше времени, следующим шагом я бы добавила:

- unit-тесты для трансформации

- более детальное логирование

- retry / timeout handling для внешнего API

- использование Airflow Connections / Variables

- защиту от дублирующей загрузки

- более явные healthchecks для всех сервисов в Docker Compose



## Conclusion

В результате реализован рабочий ETL-пайплайн, который:

- получает данные из внешнего API

- преобразует их в требуемый формат

- оркестрируется через Airflow

- записывает результат в ClickHouse

Проект показывает не только реализацию основной логики, но и решение реальных практических проблем, возникающих при работе с Docker, Airflow, ClickHouse и типами данных.


---

Maria Ilnitska  

Junior Data Engineer  
