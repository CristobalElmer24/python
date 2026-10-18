from flask import Blueprint

from .controllers import analizador_controller, automata_controller

bp = Blueprint("main", __name__)
bp.add_url_rule("/", "index", analizador_controller.index, methods=["GET", "POST"])
bp.add_url_rule("/automatas", "automatas", automata_controller.automatas)
