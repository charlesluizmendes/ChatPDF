from flask import Flask, Blueprint
from src.restx import api
from src.config import config_db, config_ma
from src.views.pdf_view import ns_pdf
from src.views.chat_view import ns_chat

app = Flask(__name__)

config_db(app)
config_ma(app)

blueprint = Blueprint('api', __name__)

api.init_app(blueprint)
app.register_blueprint(blueprint)

api.add_namespace(ns_pdf)
api.add_namespace(ns_chat)

if __name__ == "__main__":
    app.run()