# **Авторизация**
Из бота передается json следующего вида:
```json
{  
  "email": "user@example.com",  
  "telegram_id": 123456789  
}
```  
_возможно уберем telegram_id_
Ожидаемый JSON от бекэнда на вход:  
```json
{  
  "success": true,
  "user_id": 1234
}
 ```
_либо false, если email не найден_

# **Шаблоны чек-листов**
На бекэнд поступает query params:
```http request
GET /patterns?user_id=1234
```

JSON, который передает бек после запроса:
```json
{
  "patterns": [
    {
      "id": 1,
      "name": "Плановая проверка"
    },
    {
      "id": 2,
      "name": "Проверка склада"
    }
  ]
}
```

# **Фильтр проверок**
На бекэнд поступает query params:
Со следующими параметрами:
* user_id
* date_at_from
* date_at_to
* finished_at_from
* finished_at_to
* status
* overdue
* pattern_id
* show_my
* made_by_me
```http request
GET /checks?user_id=42&date_at_from=2026-04-22&date_at_to=2026-04-26&finished_at_from=null&finished_at_to=null&status=process&overdue=false&pattern_id=1&show_my=true&made_by_me=false
```

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

# **Фильтр задач**
На бекэнд поступает query params:
Со следующими параметрами:
* user_id
* date_period_from
* date_period_to
* priority
* show_my
* made_by_me

```http request
GET /tasks?user_id=42&date_period_from=2026-04-22&date_period_to=2026-04-26&priority=high&show_my=true&made_by_me=false
```

JSON, который передает бек после запроса задач:
```json
{
  "items": [
    {
      "name": "Название",
      "status": "process",
      "priority": "high",
      "deadline_at": "2026-04-22"
    },
    {
      "name": "Подготовить отчет",
      "status": "created",
      "priority": "medium",
      "deadline_period": "2026-04-29"
    }
  ]
}
```

# **Сводка по проверкам на сегодня**
Запрос на бекэнд query params:
```http request
GET /checks/today_summary?user_id=1234
```

JSON-запрос на сводку по проверкам ожидается такой: 
```json 
{
  "summary": {
    "completed": 67,
    "process": 67,
    "verification": 67,
    "created": 67
  }
}
```

# **Сводка по задачам на сегодня**
Запрос на бекэнд query params:
```http request
GET /tasks/today_summary?user_id=1234
```

JSON-запрос на сводку по задачам ожидается такой: 
```json 
{
  "summary": {
    "completed": 67,
    "process": 67,
    "verification": 67,
    "created": 67
  }
}
```