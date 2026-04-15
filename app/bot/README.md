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
