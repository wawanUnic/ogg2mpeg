# ogg2mpeg
Конвертер аудио файлов OGG в MP3


# Установка на Ubuntu 24.04

Тестировалось на машине: 1vCPU, 1Gb RAM, 20Gb SSD, 100Mb Eth

Настройка производится для сервера ogg2mpeg.duckdns.org с адресом 45.130.151.102

Задействованные порты:
```
22 - SSH - управление сервером. Вход только по ключу
80 - HHTP - веб-интерфейс (витрина). Возвращает постоянное перенаправление на HTTPs
443 - HTTPs - веб-интерфейс (витрина).
```

## 1. Добавим нового пользователя
Работаем от root

Пользователь name:password

```
adduser name
usermod -aG sudo name
su - name
sudo ls -la /root
sudo reboot
```

## 2. Создадим ключи для SSH
Работаем от root

```
ssh-keygen
cd .ssh
ls -l
nano id_rsa
mv id_rsa.pub authorized_keys
chmod 644 authorized_keys
```
Скопируем содержимое закрытого ключа из консоли и сохраним его в пустом формате на ПК с помощью текстового редактора

Имя файла не критично. Важно: приватный ключ должен содержать:
-----НАЧНИТЕ ОТКРЫВАТЬ ЗАКРЫТЫЙ КЛЮЧ OPENSSH----- ... -----END OPENSSH ПРИВАТНЫЙ КЛЮЧ-----

Публичный ключ скопируем всем пользователям в папку .ssh

Права 644 нужно сделать у всех пользователей

В Windows загрузим PuTTYgen. В меню: нажмите Conversions->Import key и найдем сохраненный файл закрытого ключа
Он загрузится в программу. Нажмем «Сохранить закрытый ключ» в формате PuTTY .ppk в D:\Program Files\PuTTY\KEYs
Загрузим файл .ppk в свой профиль SSH уже в программе PuTTY: Connection->SSH->Auth->Credentials
Connection - keepAlive 15 sec
Сохраним свой профиль в PuTTY

## 3. Запретим на вход по паролю
Работаем от root

nano /etc/ssh/sshd_config:
```
PubkeyAuthentication yes
PasswordAuthentication no
```
service ssh restart

## 4. Обновим систему
Работаем от name
```
sudo apt update
sudo apt upgrade
sudo reboot
sudo apt-get install python3-pip
sudo apt install python3.12-venv
```

## 5. Копируем исходные файлы
Работаем от name

Создаем папку ogg2mpeg. Копируем в неё исходные файлы

Даем права на исполнение (!!! Дать папке /home/name права на R+X other !!!):
```
find ogg2mpeg/ -type f -exec chmod 755 {} \;
```

## 6. Создаем виртуальное окружение
Работаем от name

Версии добавленных пакетов:

annotated-types   0.7.0

anyio             4.8.0

click             8.1.8

fastapi           0.115.7

h11               0.14.0

idna              3.10

pip               24.0

pydantic          2.10.6

pydantic_core     2.27.2

pydub             0.25.1

python-multipart  0.0.20

sniffio           1.3.1

starlette         0.45.3

typing_extensions 4.12.2

uvicorn           0.34.0

```
cd /home/pi/ogg2mpeg
python3 -m venv myenv
source myenv/bin/activate
pip install fastapi uvicorn pydub python-multipart
pip list
python main.py -- Эту команду не запускать! Это только для ручного тестирования
```

## 7. Добавляем сервисы в systemD
Работаем от name

sudo nano /etc/systemd/system/ogg2mpeg.service:
```
[Unit]
Description=ogg2mpeg
After=network-online.target nss-user-lookup.target

[Service]
User=name
Group=name
WorkingDirectory=/home/pi/ogg2mpeg
Environment="PYTHONPATH=/home/pi/ogg2mpeg/myenv/lib/python3.12/site-packages"
ExecStartPre=/usr/bin/sleep 10
ExecStart=/home/pi/ogg2mpeg/myenv/bin/python3.12 /home/pi/ogg2mpeg/main.py

RestartSec=10
Restart=always
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Настраивам systemD:
```
sudo systemctl daemon-reload
sudo systemctl enable --now ogg2mpeg.service
systemctl status ogg2mpeg.service
```

## 8. Устанавливаем кэширующий прокси-сервер
Работаем от name

Устанавливаем nginx:
```
sudo apt install nginx
sudo systemctl enable nginx
sudo systemctl start nginx
systemctl status nginx
```

Правим настройки sudo nano /etc/nginx/sites-available/ogg2mpeg:
```
server {
    listen 80;
    listen [::]:80;
    server_name ogg2mpeg.duckdns.org;
    access_log /var/log/nginx/ogg2mpeg.duckdns.org-access.log;
    error_log /var/log/nginx/ogg2mpeg.duckdns.org-error.log;

location / {
    proxy_pass http://localhost:7788;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Создаем линк, проверяем ошибки, перезапускаем:
```
sudo ln -s /etc/nginx/sites-available/ogg2mpeg /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 9. Шифруем соединение
Работаем от name

Будет отредактирован файл /etc/nginx/sites-available/ogg2mpeg

Ключ генерируется около 10-20 минут!

```
apt install certbot python3-certbot-nginx
certbot --nginx -d ogg2mpeg.duckdns.org
```

Можно посмотреть статус бота и принудительно обновить:
```
sudo systemctl status certbot.timer
sudo certbot renew --dry-run
```

## 10. Устанавливаем обработчик для веб-старницы 45.130.151.102
Работаем от name

Блокируем вход по IP-адресу сервера

Правим индексный файл командой sudo nano /var/www/html/index.html

```
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="5;https://ogg2mpeg.duckdns.org">
<meta charset="UTF-8">
<title>Nero-Reports</title>
<style>
body { width: 35em; margin: 0 auto;
font-family: Tahoma, Verdana, Arial, sans-serif; }
</style>
</head>
<body>
<h1>Ogg2mpeg</h1>

<p>Сейчас вы будете перенаправлены...</p>

<p>Если это не произошло, то нажмите
<a href="http://ogg2mpeg.duckdns.org/">сюда</a>.<br/>
</body>
</html>
```

Копируем в папку /var/www/html файл фавикона из папки /home/name/

Удаляем старый индексный файл (индексный файл по умолчанию от nginx)

## 11. Устанавливаем фаер-вол
Работаем от name

Устанавливаем и настраиваем утилиту ufw (0.36.2)

```
sudo apt install ufw
sudo ufw status
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

sudo ufw enable
sudo ufw reload
sudo ufw status

sudo reboot
sudo ufw status
```
