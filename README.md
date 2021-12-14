# Тестовое задание для PERX

### Перезапуск Docker (можно использовать и как запуск)
```commandline
./restart.sh
```

### Файлы-примеры 
- ./data/resource1.xlsx
- ./data/resource2.xls

### Настройки переменных окружения 
```commandline
api.env
```

## Загрузка файлов на обработку
### Пример запроса 

```commandline
curl --location --request POST 'http://localhost:5000/api/upload' \
--header 'Authorization: Basic YWRtaW46KmY2MnAyQiJFUysqYXNBNQ==' \
--form 'file=@"./perx_test/resource2.xls"'
```

### Пример ответа

```json
{
    "status": "file uploaded",
    "job_id": "a8984e85-44b1-47eb-a499-7b2aa0d1f5d6"
}
```

## Получение информации по задаче
### Пример запроса:
```json
curl --location --request GET 'http://localhost:5000/api/job_status/a8984e85-44b1-47eb-a499-7b2aa0d1f5d6' \
--header 'Authorization: Basic YWRtaW46KmY2MnAyQiJFUysqYXNBNQ=='
```

### Результаты ответа
#### В очереди
```json
{
    "status": "queued"
}
```
#### В процессе
```json
{
    "status": "started",
    "started_at": "2021-01-01 10:10:10",
    "ended_at": null,
    "progress": 29.3
}
```
#### Выполнено
```json
{
    "status": "finished",
    "started_at": "2021-12-14 14:11:06",
    "ended_at": "2021-12-14 14:11:06",
    "progress": 100,
    "result": [
        {
            "sheet": "Default_Data_Result(10)",
            "result": "removed: 10"
        },
        {
            "sheet": "Data_With_Other_Fields",
            "result": "removed: 10"
        },
        {
            "sheet": "Crazy_Data",
            "result": "removed: 10"
        }
    ]
}
```
