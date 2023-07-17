from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from website.util import login_required
from website.db import get_db

from . import minecraft_blueprint, server

@minecraft_blueprint.route('/')
#@login_required(permissions=0b10<<4)
@login_required()
def index():
    data = {
            'status': server.status(),
            'online': server.online(),
            'logs': server.logs()
            }
    return render_template('minecraft/index.html', data=data)

@minecraft_blueprint.route('/start')
#@login_required(permissions=0b01<<4)
@login_required()
def start():
    server.start()
    return redirect(url_for('minecraft.index'))

@minecraft_blueprint.route('/stop')
#@login_required(permissions=0b01<<4)
@login_required()
def stop():
    server.stop()
    return redirect(url_for('minecraft.index'))

