import os
from flask import Flask


def create_app():
    base = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base, "views", "templates"),
        static_folder=os.path.join(base, "views", "static"),
    )
    app.config.from_object("app.config.Config")

    from .routes import bp
    app.register_blueprint(bp)
    return app
