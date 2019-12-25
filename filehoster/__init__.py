from .client import WebClient


app = WebClient(__name__)
webapp = app.get_run("0.0.0.0", port=8080)
