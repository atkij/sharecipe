from flask import (
        Blueprint, flash, g, redirect, render_template, request, session, url_for
        )

from website.auth import login_required
from website.db import get_db

from website.minecraft_server import BedrockServer

bp = Blueprint('minecraft', __name__, url_prefix='/minecraft')
server = BedrockServer()

@bp.route('/')
@login_required(permissions=0b10<<4)
def index():
    data = {
            'status': server.status(),
            'online': server.online(),
            'logs': server.logs()
            }
    return render_template('minecraft/index.html', data=data)

@bp.route('/start')
@login_required(permissions=0b01<<4)
def start():
    server.start()
    return redirect(url_for('minecraft.index'))

@bp.route('/stop')
@login_required(permissions=0b01<<4)
def stop():
    server.stop()
    return redirect(url_for('minecraft.index'))

