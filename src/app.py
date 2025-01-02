from flask import Flask, Blueprint
from src.restx import api
from src.views.source_view import ns_source
from src.views.chat_view import ns_chat

app = Flask(__name__)

blueprint = Blueprint('api', __name__)

api.init_app(blueprint)
app.register_blueprint(blueprint)

api.add_namespace(ns_source)
api.add_namespace(ns_chat)

if __name__ == "__main__":
    app.run()