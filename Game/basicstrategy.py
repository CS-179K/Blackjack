from flask import session, redirect, url_for, Blueprint, render_template
import random

basicstrategy = Blueprint('basicstrategy', __name__)

card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

def create_deck(num_decks=1):
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [f'{rank} of {suit}' for suit in suits for rank in ranks]
    return deck * num_decks

def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

def deal_card():
    deck = session.get('deck', [])
    if not deck:
        deck = shuffle_deck(create_deck())
    card = deck.pop() if deck else None
    session['deck'] = deck
    return card

def hand_value(hand):
    value, ace_count = 0, 0
    for card in hand:
        rank = card.split()[0]
        value += card_values.get(rank, 0)
        if rank == 'A':
            ace_count += 1
    while value > 21 and ace_count:
        value -= 10
        ace_count -= 1
    return value

def is_soft_hand(hand):
    return 'A' in [card.split()[0] for card in hand] and hand_value(hand) <= 21

def initialize_game(shuffle_deck_flag=True):
    if shuffle_deck_flag:
        session['deck'] = shuffle_deck(create_deck())
    else:
        if 'deck' not in session:
            session['deck'] = create_deck()

    session['player_hands'] = [[deal_card(), deal_card()]]
    session['dealer_hand'] = [deal_card(), deal_card()]
    session['game_over'] = False
    session['current_hand'] = 0
    session['splitted'] = False
    session['insurance'] = None
    session['show_dealer_hand'] = False
    session['show_new_hand_button'] = False
    session['show_new_game_button'] = False
    session['insurance_prompted'] = False
    session['dealer_blackjack'] = False
    session['double_down'] = False
    session['original_bet_before_doubling'] = session.get('bet', 0)

def dealer_turn():
    if session.get('game_over', False) or session.get('show_dealer_hand', False):
        return

    dealer_hand = session.get('dealer_hand', [])
    if not dealer_hand:
        return 

    dealer_score = hand_value(dealer_hand)

    while dealer_score < 17:
        dealer_hand.append(deal_card())
        dealer_score = hand_value(dealer_hand)

    session['show_dealer_hand'] = True
    session['game_over'] = True
    session['show_new_hand_button'] = True
    session['show_new_game_button'] = True

def basic_strategy(player_total, dealer_value, soft):
    if 4 <= player_total <= 8:
        return 'hit'
    if player_total == 9:
        if dealer_value in [1, 2, 7, 8, 9, 10]:
            return 'hit'
        return 'double_down'
    if player_total == 10:
        if dealer_value in [1, 10]:
            return 'hit'
        return 'double_down'
    if player_total == 11:
        if dealer_value == 1:
            return 'hit'
        return 'double_down'
    
    if soft:
        if player_total in [12, 13, 14]:
            if dealer_value in [5, 6]:
                return 'double_down'
            return 'hit'
        if player_total in [15, 16]:
            if dealer_value in [4, 5, 6]:
                return 'double_down'
            return 'hit'
        if player_total == 17:
            if dealer_value in [3, 4, 5, 6]:
                return 'double_down'
            return 'hit'
        if player_total == 18:
            if dealer_value in [3, 4, 5, 6]:
                return 'double_down'
            if dealer_value in [2, 7, 8]:
                return 'stand'
            return 'hit'
        if player_total >= 19:
            return 'stand'
    else:
        if player_total == 12:
            if dealer_value in [1, 2, 3, 7, 8, 9, 10]:
                return 'hit'
            return 'stand'
        if player_total in [13, 14, 15, 16]:
            if dealer_value in [2, 3, 4, 5, 6]:
                return 'stand'
            return 'hit'
        if player_total >= 17:
            return 'stand'
        
def handle_player_action(action):
    if session.get('game_over', False):
        return redirect(url_for('basicstrategy.show_game'))

    player_hands = session.get('player_hands', [])
    current_hand_index = session.get('current_hand', 0)

    if not player_hands or current_hand_index >= len(player_hands):
        return redirect(url_for('basicstrategy.show_game'))

    hand = player_hands[current_hand_index]
    dealer_hand = session.get('dealer_hand', [])
    if not dealer_hand:
        return redirect(url_for('basicstrategy.show_game'))

    original_bet = session.get('bet', 0)
    double_down = session.get('double_down', False)
    original_bet_before_doubling = session.get('original_bet_before_doubling', original_bet)

    dealer_card_value = card_values.get(dealer_hand[0].split()[0], 0)

    player_total = hand_value(hand)
    soft = is_soft_hand(hand)

    correct_action = basic_strategy(player_total, dealer_card_value, soft)

    if action == correct_action:
        session['choice_feedback'] = 'Correct'
    else:
        session['choice_feedback'] = f'Incorrect. Correct move: {correct_action}'
    
    def update_game_state(is_game_over, result_message=None):
        session['game_over'] = is_game_over
        session['show_new_hand_button'] = is_game_over
        session['show_new_game_button'] = is_game_over
        if result_message:
            session['result'] = result_message

    def handle_bust():
        bet = session.get('bet', 0)
        if double_down:
            session['bankroll'] -= (original_bet_before_doubling * 2)
        else:
            session['bankroll'] -= bet

        session['show_dealer_hand'] = True
        session['bet'] = original_bet_before_doubling
        session['double_down'] = False

        return redirect(url_for('basicstrategy.show_game'))

    def handle_surrender():
        if double_down:
            session['bankroll'] += original_bet_before_doubling
            session['double_down'] = False
        else:
            session['bankroll'] -= session.get('bet', 0) / 2

        player_hands.pop(current_hand_index)
        if not player_hands:
            update_game_state(True, 'Player surrenders. You lose half your bet.')
        else:
            if current_hand_index >= len(player_hands):
                session['current_hand'] = len(player_hands) - 1
        session['player_hands'] = player_hands
        return redirect(url_for('basicstrategy.show_game'))

    def resolve_hand():
        dealer_hand = session.get('dealer_hand', [])
        if not dealer_hand: 
            return redirect(url_for('basicstrategy.show_game'))
            
        dealer_hand_value = hand_value(dealer_hand)
        bet = session.get('bet', 0)
        insurance = session.get('insurance', False)
        dealer_blackjack = session.get('dealer_blackjack', False)
        double_down = session.get('double_down', False)
        original_bet_before_doubling = session.get('original_bet_before_doubling', bet)

        if dealer_blackjack:
            if insurance:
                session['bankroll'] += bet
                update_game_state(True, 'Dealer has Blackjack. Insurance pays 2:1.')
            else:
                session['bankroll'] -= bet
                update_game_state(True, 'Dealer has Blackjack. You lose your bet.')
            return redirect(url_for('basicstrategy.show_game'))

        if all(hand_value(h) > 21 for h in session.get('player_hands', [])):
            return handle_bust()

        for hand in session.get('player_hands', []):
            player_hand_value = hand_value(hand)
            if player_hand_value > 21:
                continue

            if dealer_hand_value > 21 or player_hand_value > dealer_hand_value:
                session['bankroll'] += original_bet_before_doubling * (3 if double_down else 1.5)
                update_game_state(True, 'You win!')
            elif player_hand_value == dealer_hand_value:
                update_game_state(True, 'Push! It\'s a tie.')
            else:
                session['bankroll'] -= original_bet_before_doubling * (2 if double_down else 1)
                update_game_state(True, 'Dealer wins.')

        session['bet'] = original_bet_before_doubling
        session['double_down'] = False

        return redirect(url_for('basicstrategy.show_game'))

    if action == 'hit':
        hand.append(deal_card())
        session['player_hands'] = player_hands
        if hand_value(hand) > 21:
            return handle_bust()
        session['result'] = 'Correct' if correct_action == 'hit' else 'Incorrect'

    elif action == 'stand':
        session['current_hand'] += 1

        if session['current_hand'] >= len(player_hands):
            dealer_turn() 
            return resolve_hand() 
        else:
            return redirect(url_for('basicstrategy.show_game'))

    elif action == 'split':
        if len(hand) == 2 and hand_value([hand[0]]) == hand_value([hand[1]]):
            card1, card2 = hand.pop(0), hand.pop(0)
            player_hands[current_hand_index] = [card1, deal_card()]
            player_hands.append([card2, deal_card()])
            session['player_hands'] = player_hands
            session['splitted'] = True
            session['current_hand'] = len(player_hands) - 2
        session['result'] = 'Correct' if correct_action == 'split' else 'Incorrect'

    elif action == 'double_down':
        if len(hand) == 2:
            hand.append(deal_card())
            session['double_down'] = True
            session['player_hands'] = player_hands
            if hand_value(hand) > 21:
                return handle_bust()
            else:
                session['current_hand'] += 1
                if session['current_hand'] >= len(player_hands):
                    dealer_turn()
                    return resolve_hand()
        session['result'] = 'Correct' if correct_action == 'double_down' else 'Incorrect'

    elif action == 'surrender':
        session['result'] = 'Correct' if correct_action == 'surrender' else 'Incorrect'
        return handle_surrender()

    return redirect(url_for('basicstrategy.show_game'))

@basicstrategy.route('/start_new_hand', methods=['POST'])
def start_new_hand():
    if not session.get('game_over', False):
        return redirect(url_for('basicstrategy.show_game'))

    initialize_game(shuffle_deck_flag=False)
    session['show_new_hand_button'] = False
    session['show_new_game_button'] = False
    session['show_dealer_hand'] = False

    return redirect(url_for('basicstrategy.show_game')) 


@basicstrategy.route('/start_new_game', methods=['POST'])
def start_new_game():
    session['bankroll'] = 1000  
    initialize_game()
    session['result'] = None  
    session['show_new_game_button'] = False
    session['show_new_hand_button'] = False

    return redirect(url_for('basicstrategy.show_game')) 


@basicstrategy.route('/')
def show_game():
    if 'bankroll' not in session:
        session['bankroll'] = 1000 

    if 'player_hands' not in session or 'dealer_hand' not in session:
        initialize_game()
    player_hands = session.get('player_hands', [])
    dealer_hand = session.get('dealer_hand', [])
    show_dealer_hand = session.get('show_dealer_hand', False)
    result = session.get('result', None)
    insurance = session.get('insurance', None)
    game_over = session.get('game_over', False)
    splitted = session.get('splitted', False)
    show_new_hand_button = session.get('show_new_hand_button', False)
    bet = session.get('bet', 0)
    show_new_game_button = session.get('show_new_game_button', False)

    player_hand_values = [hand_value(hand) for hand in player_hands]
    player_hands_with_values = list(zip(player_hands, player_hand_values))


    dealer_hand_value = hand_value(dealer_hand) if show_dealer_hand else None
    return render_template('basicstrategy.html',
                            player_hands_with_values=player_hands_with_values,
                            dealer_hand=dealer_hand,
                            dealer_hand_value=dealer_hand_value,
                            result=result,
                            insurance=insurance,
                            game_over=game_over,
                            splitted=splitted,
                            show_new_hand_button=show_new_hand_button,
                            show_new_game_button=show_new_game_button,
                            show_dealer_hand=show_dealer_hand,
                            bet=bet,
                            bankroll=session['bankroll'],
                            card_values=card_values) 

@basicstrategy.route('/handle_player_action/<action>')
def player_action(action):
    handle_player_action(action)
    return redirect(url_for('basicstrategy.show_game')) 
