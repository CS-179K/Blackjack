from flask import session, render_template, redirect, url_for, Blueprint, request
from urllib.parse import unquote
import random
from . import models
from . import db
from flask_login import current_user

game = Blueprint('game', __name__)

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
    session['doubled_down'] = False
    session['original_bet_before_doubling'] = session.get('bet', 0)

def dealer_turn():
    if session.get('game_over', False) or session.get('show_dealer_hand', False):
        return

    dealer_hand = session.get('dealer_hand', [])
    dealer_score = hand_value(dealer_hand)

    while dealer_score < 17:
        dealer_hand.append(deal_card())
        dealer_score = hand_value(dealer_hand)

    session['show_dealer_hand'] = True
    session['game_over'] = True
    session['show_new_hand_button'] = True
    session['show_new_game_button'] = True

def handle_player_action(action):
    if session.get('game_over', False):
        return redirect(url_for('game.show_game'))

    player_hands = session.get('player_hands', [])
    current_hand_index = session.get('current_hand', 0)
    hand = player_hands[current_hand_index]
    original_bet = session.get('bet', 0)
    doubled_down = session.get('doubled_down', False)
    original_bet_before_doubling = session.get('original_bet_before_doubling', original_bet)

    def update_game_state(is_game_over, result_message=None):
        session['game_over'] = is_game_over
        session['show_new_hand_button'] = is_game_over
        session['show_new_game_button'] = is_game_over
        if result_message:
            session['result'] = result_message

    def handle_bust():
        # Handle the case where the player busts
        bet = session.get('bet', 0)
        doubled_down = session.get('doubled_down', False)
        original_bet_before_doubling = session.get('original_bet_before_doubling', bet)

        # Deduct the appropriate amount from the bankroll based on the doubled down state
        if doubled_down:
            session['bankroll'] -= (original_bet_before_doubling * 2)  # Lose doubled bet
        else:
            session['bankroll'] -= bet  # Lose original bet

        # Check if all hands are busted
        if not any(hand_value(h) <= 21 for h in session.get('player_hands', [])):
            update_game_state(True, 'You bust!')
            session['show_dealer_hand'] = True
            if current_user.is_authenticated:
                update_user_stats('loss')

        # Reset doubled down flag
        session['bet'] = original_bet_before_doubling
        session['doubled_down'] = False

        return redirect(url_for('game.show_game'))


    def handle_surrender():
        if doubled_down:
            session['bankroll'] += original_bet_before_doubling  # Refund half of the doubled bet
            session['doubled_down'] = False
        else:
            session['bankroll'] -= session.get('bet', 0) / 2
        player_hands.pop(current_hand_index)
        if not player_hands:
            update_game_state(True, 'Player surrenders. You lose half your bet.')
        else:
            if current_hand_index >= len(player_hands):
                session['current_hand'] = len(player_hands) - 1
        session['player_hands'] = player_hands
        if current_user.is_authenticated:
            update_user_stats('loss')
        return redirect(url_for('game.show_game'))

    def resolve_hand():
        dealer_hand = session.get('dealer_hand', [])
        dealer_hand_value = hand_value(dealer_hand)
        bet = session.get('bet', 0)
        insurance = session.get('insurance', False)
        dealer_blackjack = session.get('dealer_blackjack', False)
        doubled_down = session.get('doubled_down', False)
        original_bet_before_doubling = session.get('original_bet_before_doubling', bet)

        def handle_dealer_blackjack():
            if insurance:
                session['bankroll'] += bet  # Insurance bet pays 2:1
                update_game_state(True, 'Dealer has Blackjack. Insurance pays 2:1.')
            else:
                session['bankroll'] -= bet  # Original bet lost
                update_game_state(True, 'Dealer has Blackjack. You lose your bet.')
            if current_user.is_authenticated:
                update_user_stats('loss')  
            return redirect(url_for('game.show_game'))

        if dealer_blackjack:
            return handle_dealer_blackjack()

        if all(hand_value(h) > 21 for h in session.get('player_hands', [])):  # Check if all hands are busted
            return handle_bust()

        for hand in session.get('player_hands', []):
            player_hand_value = hand_value(hand)
            if player_hand_value > 21:
                continue  # Skip this hand if it is busted

            if dealer_hand_value > 21 or player_hand_value > dealer_hand_value:
                # Player wins
                if player_hand_value == 21:  # Blackjack
                    if doubled_down:
                        session['bankroll'] += original_bet_before_doubling * 3  # Double Down, double the payout
                        update_game_state(True, 'Blackjack! You won double down.')
                    else:
                        session['bankroll'] += original_bet_before_doubling * 1.5  # Blackjack pays 3:2
                        update_game_state(True, 'Blackjack! You win with a 3 to 2 payout.')
                else:
                    if doubled_down:
                        session['bankroll'] += original_bet_before_doubling * 2  # Double Down, double the payout
                        update_game_state(True, 'You win! You won double down.')
                    else:
                        session['bankroll'] += bet  # Win with the original bet amount
                        update_game_state(True, 'You win!')
                if current_user.is_authenticated:
                    update_user_stats('win')
            elif player_hand_value == dealer_hand_value:
                update_game_state(True, 'Push! It\'s a tie.')
            else:
                # Dealer wins
                if doubled_down:
                    session['bankroll'] -= original_bet_before_doubling * 2  # Double Down, double the loss
                    update_game_state(True, 'Dealer wins. You lost the double down.')
                else:
                    session['bankroll'] -= bet  # Loss
                    update_game_state(True, 'Dealer wins.')
                if current_user.is_authenticated:
                    update_user_stats('loss')

        # Reset bet and doubled down flag
        session['bet'] = original_bet_before_doubling
        session['doubled_down'] = False

        return redirect(url_for('game.show_game'))


    def is_pair(card1, card2):
        return hand_value([card1]) == hand_value([card2])

    if action == 'hit':
        if hand_value(hand) <= 21:
            card = deal_card()
            if card:
                hand.append(card)
                if hand_value(hand) > 21:
                    return handle_bust()
        session['player_hands'] = player_hands
        return redirect(url_for('game.show_game'))

    elif action == 'stay':
        session['player_hands'] = player_hands
        if current_hand_index == len(player_hands) - 1:
            dealer_turn()  # Handle dealer's turn
            return resolve_hand()  # Determine the outcome after dealer plays
        else:
            session['current_hand'] = current_hand_index + 1
        return redirect(url_for('game.show_game'))

    elif action == 'split':
        if len(hand) == 2 and is_pair(hand[0], hand[1]):
            card1, card2 = hand.pop(0), hand.pop(0)
            new_hand1 = [card1, deal_card()]
            new_hand2 = [card2, deal_card()]
            player_hands[current_hand_index] = new_hand1
            player_hands.append(new_hand2)
            session['player_hands'] = player_hands
            session['splitted'] = True
            session['current_hand'] = len(player_hands) - 2
        return redirect(url_for('game.show_game'))

    elif action == 'double_down':
        if len(hand) == 2:
            card = deal_card()
            hand.append(card)
            if current_hand_index == len(player_hands) - 1:
                session['doubled_down'] = True
                if hand_value(hand) > 21:
                    return handle_bust()
                else:
                    session['player_hands'] = player_hands
                    session['current_hand'] += 1
                    if session['current_hand'] >= len(player_hands):
                        dealer_turn()  # Handle dealer's turn if it's the last hand
                        return resolve_hand()
            else:
                session['current_hand'] = current_hand_index + 1
                session['original_bet_before_doubling'] = session.get('bet', 0)  # Store the original bet amount
                session['bet'] *= 2  # Double the bet amount
                session['doubled_down'] = True
                if hand_value(hand) > 21:
                    return handle_bust()
                else:
                    session['player_hands'] = player_hands
                    session['current_hand'] += 1
                    if session['current_hand'] >= len(player_hands):
                        dealer_turn()  # Handle dealer's turn if it's the last hand
                        return resolve_hand()
        return redirect(url_for('game.show_game'))

    elif action == 'surrender':
        return handle_surrender()

    return redirect(url_for('game.show_game'))

@game.route('/player_action/<action>')
def player_action(action):
    handle_player_action(action)
    # Instead of redirecting, render the template directly for AJAX
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
    insurance_prompted = session.get('insurance_prompted', False)

    # Calculate player hands' values
    player_hand_values = [hand_value(hand) for hand in player_hands]
    player_hands_with_values = list(zip(player_hands, player_hand_values))

    # Check if dealer's face-up card is an Ace
    dealer_face_up_card = dealer_hand[0] if dealer_hand else None
    dealer_face_up_is_ace = dealer_face_up_card and dealer_face_up_card.startswith('A')

    # Calculate dealer hand value if Fit should be shown
    dealer_hand_value = hand_value(dealer_hand) if show_dealer_hand else None

    if dealer_face_up_is_ace and not insurance_prompted and not game_over:
        session['insurance_prompted'] = True
        print("Insurance on")
        return render_template('index.html',
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
                               bankroll=session['bankroll'])
    else:
        return render_template('index.html',
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
                            bankroll=session['bankroll'])

@game.route('/start_game', methods=['POST'])
def start_game():
    if 'bankroll' not in session:
        session['bankroll'] = 1000  # Default bankroll

    bet = int(request.form.get('bet', 0))
    if bet <= 0 or bet > session['bankroll']:
        return "Invalid bet amount or insufficient bankroll.", 400

    session['bet'] = bet
    initialize_game()
    if current_user != 'AnonymousUserMixin':
        current_user.bank = session['bankroll']
        db.session.commit()
    return redirect(url_for('game.show_game'))

@game.route('/start_new_hand', methods=['POST'])
def start_new_hand():
    if not session.get('game_over', False):
        return redirect(url_for('game.show_game'))

    # Initialize the game for a new hand without shuffling the deck
    initialize_game(shuffle_deck_flag=False)
    session['show_new_hand_button'] = False
    session['show_new_game_button'] = False
    session['show_dealer_hand'] = False
    
    return redirect(url_for('game.show_game'))

@game.route('/start_new_game', methods=['POST'])
def start_new_game():
    session['bankroll'] = 1000  # Reset bankroll
    initialize_game()
    if current_user != 'AnonymousUserMixin':
        current_user.bank = session['bankroll']
        db.session.commit()
    session['result'] = None  # Clear result
    session['show_new_game_button'] = False
    session['show_new_hand_button'] = False
    return redirect(url_for('game.show_game'))

@game.route('/')
def show_game():
    if 'bankroll' not in session:
        session['bankroll'] = 1000  # Default bankroll

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
    insurance_prompted = session.get('insurance_prompted', False)

    # Calculate player hands' values
    player_hand_values = [hand_value(hand) for hand in player_hands]
    player_hands_with_values = list(zip(player_hands, player_hand_values))

    # Check if dealer's face-up card is an Ace
    dealer_face_up_card = dealer_hand[0] if dealer_hand else None
    dealer_face_up_is_ace = dealer_face_up_card and dealer_face_up_card.startswith('A')
    if dealer_face_up_card and dealer_face_up_card.startswith('A'):
        dealer_face_up_is_ace = True
        insurance_prompted=True
    print(dealer_face_up_card,dealer_face_up_is_ace)

    # Calculate dealer hand value if Fit should be shown
    dealer_hand_value = hand_value(dealer_hand) if show_dealer_hand else None

    # Show insurance option only if dealer's face-up card is an Ace
    if dealer_face_up_is_ace  and not game_over and insurance!=False:
        session['insurance_prompted'] = True
        return render_template('index.html',
                               player_hands_with_values=player_hands_with_values,
                               dealer_hand=dealer_hand,
                               insurance_prompted=insurance_prompted,
                               dealer_hand_value=dealer_hand_value,
                               result=result,
                               insurance=insurance,
                               game_over=game_over,
                               splitted=splitted,
                               show_new_hand_button=show_new_hand_button,
                               show_new_game_button=show_new_game_button,
                               show_dealer_hand=show_dealer_hand,
                               bet=bet,
                               bankroll=session['bankroll'])

    return render_template('index.html',
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
                           bankroll=session['bankroll'])

@game.route('/insurance', methods=['POST'])
def insurance():
    if session.get('game_over', False):
        return redirect(url_for('game.show_game'))

    # Check if insurance prompt is valid
    dealer_hand = session.get('dealer_hand', [])
    dealer_face_up_card = dealer_hand[0] 
    dealer_face_up_is_ace = False
    if dealer_face_up_card and dealer_face_up_card.startswith('A'):
        dealer_face_up_is_ace = True
    print(dealer_face_up_card)
    

    if  dealer_face_up_is_ace!=True:
        # If dealer's face-up card is not an Ace, ignore insurance choice
        print('not an Ace')
        return redirect(url_for('game.show_game'))

    insurance_choice = request.form.get('insurance_choice')
    print(insurance_choice)
    bet = session.get('bet', 0)

    if insurance_choice == 'take':
        session['insurance'] = True
        session['bankroll'] -= bet / 2
    else:
        print('No Insurance')
        session['insurance'] = False

    # Reveal dealer's hand after insurance choice
    dealer_hand_value = hand_value(dealer_hand)
    
    if dealer_face_up_is_ace and dealer_hand_value == 21:
        session['dealer_blackjack'] = True
    else:
        session['dealer_blackjack'] = False

    return redirect(url_for('game.show_game'))

# Developer console
@game.route('/add_card_to_hand', methods=['POST'])
def add_card_to_hand():
    ace_of_spades = "Ace of Spades"
    if 'game_over' in session and session['game_over']:
        return "Game is over. Start a new game to continue.", 400
    
    hand_type = request.form.get('hand_type')
    card = unquote(request.form.get('card'))
    
    if hand_type not in ['player', 'dealer'] or not card:
        return "Invalid hand type or card.", 400
    if hand_type == 'player':
        player_hands = session.get('player_hands', [])
        if player_hands:
            #player_hands[0].insert(0,card)  # add card to the first hand
            if card == '10 of Spades':
                player_hands[0] = [card, 'A of Spades']
            else:
                player_hands[0] = [card, card]
            session['player_hands'] = player_hands
            print(player_hands)
    elif hand_type == 'dealer':
        dealer_hand = session.get('dealer_hand', [])
        #dealer_hand.insert(0,card)
        if card == '10 of Spades':
            dealer_hand = [card, 'A of Spades']
        else:
            dealer_hand = [card, 'card']
        session['dealer_hand'] = dealer_hand

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
    insurance_prompted = session.get('insurance_prompted', False)

    # Calculate player hands' values
    player_hand_values = [hand_value(hand) for hand in player_hands]
    player_hands_with_values = list(zip(player_hands, player_hand_values))

    # Check if dealer's face-up card is an Ace
    dealer_face_up_card = dealer_hand[0] if dealer_hand else None
    dealer_face_up_is_ace = dealer_face_up_card and dealer_face_up_card.startswith('A')

    # Calculate dealer hand value if Fit should be shown
    dealer_hand_value = hand_value(dealer_hand) if show_dealer_hand else None

    if dealer_face_up_is_ace and not insurance_prompted and not game_over:
        session['insurance_prompted'] = True
        return render_template('index.html',
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
                               bankroll=session['bankroll'])
    else:
        return render_template('index.html',
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
                            bankroll=session['bankroll'])

def update_user_stats(result):
    if result == 'win':
        current_user.wins += 1
        # Update high score if needed
        current_score = session['bankroll']
        if current_score > current_user.high_score:
            current_user.high_score = current_score
    elif result == 'loss':
        current_user.bank -= session.get('bet', 0) # Subtracts the bet amount to the user's bank
    elif result == 'tie':
        # Handle ties if necessary, e.g., increase ties count
        pass

    # Increment games played
    current_user.games += 1
    current_user.bank = session['bankroll']
    db.session.commit()
