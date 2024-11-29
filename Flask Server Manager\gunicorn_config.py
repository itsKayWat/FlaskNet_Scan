import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# SSL Configuration
keyfile = "certs/private.key"
certfile = "certs/certificate.crt"

# Process naming
proc_name = "flask_server_manager"

# Server hooks
def on_starting(server):
    server.log.info("Server is starting")

def on_reload(server):
    server.log.info("Server is reloading")

def on_exit(server):
    server.log.info("Server is shutting down")