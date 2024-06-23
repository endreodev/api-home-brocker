# hypercorn_config.py
bind = ["localhost:5000"]
certfile = "localhost.crt"
keyfile = "localhost.key"
shutdown_timeout = 60 



#openssl req -x509 -nodes -days 965 -newkey rsa:2048 -keyout localhost.key -out localhost.crt