# main.py

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/gamemodes')
def gamemodes():
    return render_template('gamemodes.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, games=current_user.games, bank=current_user.bank, high_score=current_user.high_score, wins=current_user.wins)

@main.route('/game')
def game():
    return render_template('index.html')

@main.route('/cardcount')
def cardcount():
    return render_template('cardcount.html')

@main.route('/basicstrategy')
def basicstrategy():
        return render_template('basicstrategy.html')
