# Odyssey Badge Holders Soft

## Установка и запуск

* Установить библиотеки командой
```bash 
  pip install -r requirements.txt
```
* Запустить командой
```bash 
  python main.py
```

## Файлы
<li>wallets.txt — приватные ключи кошельков. Каждый с новой строки.</li>
<li>proxies.txt — прокси в формате login:pass@ip:port</li> 

## Настройки
Все настройки производятся в файле `config.py`.

1. [ ] SHUFFLE_WALLETS — перемешивать ли кошельки;
2. [ ] PAUSE_BETWEEN_WALLETS — пауза в секундах [от, до] между кошельками;
3. [ ] RETRIES — кол-во повторных попыток в случае ошибки.
4. [ ] PAUSE_BETWEEN_RETRIES - пауза между попытками.
