# main.py

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    name=current_user.name
    bank=current_user.bank
    wins=current_user.wins
    games=current_user.games
    losses=current_user.games - current_user.wins
    return render_template('profile.html', name=name, bank=bank, wins=wins, games=games, losses=losses)
@main.route('/game')
def game():
    return render_template('game.html')