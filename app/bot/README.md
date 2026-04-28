# **Авторизация**
Из бота передается json следующего вида:
```json
{  
  "email": "user@example.com",  
  "telegram_id": 123456789  
}
```  
Ожидаемый JSON от бекэнда:  
```json
{  
  "success": true 
}
 ```
_либо false, если email не найден_

JSON, который передает бек после запроса проверок:
```json
{
  "items": [
    {
      "name": "Название",
      "pattern_name": "шаблон чеклиста",
      "status": "completed",
      "date_at": "2026-04-22",
      "deadline_at": "2026-04-26"
    },
    {
      "name": "Проверка склада",
      "pattern_name": "Плановая проверка",
      "status": "process",
      "date_at": "2026-04-24",
      "deadline_at": "2026-04-30"
    }
  ]
}
```

JSON, который передает бек после запроса задач:
```json
{
  "items": [
    {
      "name": "Название",
      "status": "process",
      "priority": "high",
      "deadline_period": {
        "from": "2026-04-22",
        "to": "2026-04-26"
      }
    },
    {
      "name": "Подготовить отчет",
      "status": "created",
      "priority": "medium",
      "deadline_period": {
        "from": "2026-04-27",
        "to": "2026-04-29"
      }
    }
  ]
}
```

JSON-запрос на сводку по проверкам: 
```json 
{
  "summary": {
    "completed": 5,
    "process": 10,
    "verification": 6,
    "created": 7
  }
}
```

JSON-запрос на сводку по задачам: 
```json 
{
  "summary": {
    "completed": 5,
    "process": 10,
    "verification": 6,
    "created": 7
  }
}
```