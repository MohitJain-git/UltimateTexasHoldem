import itertools
import random
import pandas as pd
from collections import Counter
from itertools import combinations
from datetime import datetime 

class PokerGame:
    def __init__(self):
        # Create a deck of cards using product of ranks and suits
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['S', 'H', 'D', 'C']
        self.deck = list(itertools.product(ranks, suits))
        self.shuffle_deck()
        
        # Track dealt cards to avoid repeats
        self.dealt_cards = set()

    def reset_deck(self):
        # Reset and reshuffle the deck for a new game
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['S', 'H', 'D', 'C']
        self.deck = list(itertools.product(ranks, suits))
        self.shuffle_deck()
        self.dealt_cards.clear()
        
    def shuffle_deck(self):
        random.shuffle(self.deck)
    
    def deal_cards(self):
        # Deal cards for two players
        self.reset_deck()
        
        player1_hand = [self.deck.pop() for _ in range(2)]
        player2_hand = [self.deck.pop() for _ in range(2)]
        
        # Deal community cards
        community_cards = [self.deck.pop() for _ in range(5)]
        
        return {
            'Player 1': player1_hand,
            'Player 2': player2_hand,
            'Community Cards': community_cards
        }
    
    def deal_player_cards(self, already_dealt=None):
        """Deal two cards to the player, avoiding previously dealt cards."""
        if already_dealt is None:
            already_dealt = set()
        
        player_hand = []
        for _ in range(2):
            # Find a card not yet dealt
            card = self._find_unique_card(already_dealt.union(self.dealt_cards))
            player_hand.append(card)
            self.dealt_cards.add(card)
        
        return player_hand
    
    def deal_opponent_cards(self, already_dealt=None):
        """Deal two cards to the opponent, avoiding previously dealt cards."""
        if already_dealt is None:
            already_dealt = set()
        
        opponent_hand = []
        for _ in range(2):
            # Find a card not yet dealt
            card = self._find_unique_card(already_dealt.union(self.dealt_cards))
            opponent_hand.append(card)
            self.dealt_cards.add(card)
        
        return opponent_hand
    
    def deal_flop(self, already_dealt=None):
        """Deal the first three community cards (flop)."""
        if already_dealt is None:
            already_dealt = set()
        
        flop = []
        for _ in range(3):
            # Find a card not yet dealt
            card = self._find_unique_card(already_dealt.union(self.dealt_cards))
            flop.append(card)
            self.dealt_cards.add(card)
        
        return flop
    
    def deal_turn(self, already_dealt=None):
        """Deal the fourth community card (turn)."""
        if already_dealt is None:
            already_dealt = set()
        
        # Find a card not yet dealt
        card = self._find_unique_card(already_dealt.union(self.dealt_cards))
        self.dealt_cards.add(card)
        
        return card
    
    def deal_river(self, already_dealt=None):
        """Deal the fifth community card (river)."""
        if already_dealt is None:
            already_dealt = set()
        
        # Find a card not yet dealt
        card = self._find_unique_card(already_dealt.union(self.dealt_cards))
        self.dealt_cards.add(card)
        
        return card
    
    def _find_unique_card(self, excluded_cards):
        """Find a card that hasn't been dealt yet."""
        for card in self.deck:
            if card not in excluded_cards:
                self.deck.remove(card)
                return card
        
        raise ValueError("No more unique cards available in the deck")
    
    def display_cards(self, cards):
        """Display cards in a readable format."""
        return ' '.join([f"{rank}{suit}" for rank, suit in cards])
   
    def display_cards_dict(self, cards_dict):
        for player, hand in cards_dict.items():
            print(f"\n{player}:")
            hand_str = ' '.join([f"{rank}{suit}" for rank, suit in hand])
            print(hand_str)

class PokerHandEvaluator:
    # Define hand rankings
    HAND_RANKINGS = {
        'Royal Flush': 10,
        'Straight Flush': 9,
        'Four of a Kind': 8,
        'Full House': 7,
        'Flush': 6,
        'Straight': 5,
        'Three of a Kind': 4,
        'Two Pair': 3,
        'One Pair': 2,
        'High Card': 1
    }
    
    def __init__(self):
        self.card_values = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, 
                           '9':9, '10':10, 'J':11, 'Q':12, 'K':13, 'A':14}

    def evaluate_hand(self, hole_cards, community_cards):
        all_cards = hole_cards + community_cards
        all_combinations = list(combinations(all_cards, 5))
        best_hand = (0, '', [])  # (score, hand_name, cards)
        
        for five_cards in all_combinations:
            ranks = [card[0] for card in five_cards]
            # print("RANKS", ranks)
            suits = [card[1] for card in five_cards]
            # print("SUITS", suits)
            # Convert ranks to values
            values = sorted([self.card_values[rank] for rank in ranks], reverse=True)
            # print("VALUES", values)
            

            # Check for each hand type
            if self._is_royal_flush(values, suits):
                score = (self.HAND_RANKINGS['Royal Flush'], values)
                hand_name = 'Royal Flush'
            elif self._is_straight_flush(values, suits):
                score = (self.HAND_RANKINGS['Straight Flush'], values)
                hand_name = 'Straight Flush'
            elif self._is_four_kind(values):
                score = (self.HAND_RANKINGS['Four of a Kind'], values)
                hand_name = 'Four of a Kind'
            elif self._is_full_house(values):
                score = (self.HAND_RANKINGS['Full House'], values)
                hand_name = 'Full House'
            elif self._is_flush(suits):
                score = (self.HAND_RANKINGS['Flush'], values)
                hand_name = 'Flush'
            elif self._is_straight(values):
                score = (self.HAND_RANKINGS['Straight'], values)
                hand_name = 'Straight'
            elif self._is_three_kind(values):
                score = (self.HAND_RANKINGS['Three of a Kind'], values)
                hand_name = 'Three of a Kind'
            elif self._is_two_pair(values):
                score = (self.HAND_RANKINGS['Two Pair'], values)
                hand_name = 'Two Pair'
            elif self._is_one_pair(values):
                score = (self.HAND_RANKINGS['One Pair'], values)
                hand_name = 'One Pair'
            else:
                score = (self.HAND_RANKINGS['High Card'], values)
                hand_name = 'High Card'
                
            if score[0] > best_hand[0]:
                best_hand = (score[0], hand_name, five_cards)
            elif score[0] == best_hand[0]:
                output = self.evaluate_equal_rank_hands(best_hand, (score[0], hand_name, five_cards))
                if output == 2:
                    best_hand = (score[0], hand_name, five_cards)

                
        return best_hand
    
    def evaluate_equal_rank_hands(self, p1_score, p2_score):
        ranks_1 = [card[0] for card in p1_score[2]]
        ranks_2 = [card[0] for card in p2_score[2]]

        values_1 = sorted([self.card_values[rank] for rank in ranks_1], reverse=True)
        values_2 = sorted([self.card_values[rank] for rank in ranks_2], reverse=True)

        # Royal Flush
        if p1_score[0] == 10:
            return 3
        
        # Straight Flush
        elif p1_score[0] == 9 or p1_score[0] == 5:
            if values_1 == [14, 5, 4, 3, 2]:
                values_1 = [5, 4, 3, 2, 1]
            if values_2 == [14, 5, 4, 3, 2]:
                values_2 = [5, 4, 3, 2, 1]
                
            if max(values_1) > max(values_2):
                return 1
            elif max(values_2) > max(values_1):
                return 2
            return 3
        
        # Four of a Kind
        elif p1_score[0] == 8:
            count_1 = Counter(values_1)
            count_2 = Counter(values_2)
            quad_1 = [k for k, v in count_1.items() if v == 4][0]
            quad_2 = [k for k, v in count_2.items() if v == 4][0]
            if quad_1 > quad_2:
                return 1
            elif quad_2 > quad_1:
                return 2
            else:
                kicker_1 = [k for k, v in count_1.items() if v == 1][0]
                kicker_2 = [k for k, v in count_2.items() if v == 1][0]
                if kicker_1 > kicker_2:
                    return 1
                elif kicker_2 > kicker_1:
                    return 2
                return 3
        
        # Full House
        elif p1_score[0] == 7:
            count_1 = Counter(values_1)
            count_2 = Counter(values_2)
            triple_1 = [k for k, v in count_1.items() if v == 3][0]
            triple_2 = [k for k, v in count_2.items() if v == 3][0]
            if triple_1 > triple_2:
                return 1
            elif triple_2 > triple_1:
                return 2
            else:
                pair_1 = [k for k, v in count_1.items() if v == 2][0]
                pair_2 = [k for k, v in count_2.items() if v == 2][0]
                if pair_1 > pair_2:
                    return 1
                elif pair_2 > pair_1:
                    return 2
                return 3
        
        # Flush
        elif p1_score[0] == 6:
            for i in range(5):
                if values_1[i] > values_2[i]:
                    return 1
                elif values_2[i] > values_1[i]:
                    return 2
            return 3
        
        # Three of a Kind
        elif p1_score[0] == 4:
            count_1 = Counter(values_1)
            count_2 = Counter(values_2)
            triple_1 = [k for k, v in count_1.items() if v == 3][0]
            triple_2 = [k for k, v in count_2.items() if v == 3][0]
            if triple_1 > triple_2:
                return 1
            elif triple_2 > triple_1:
                return 2
            
            # Compare kickers
            kickers_1 = sorted([k for k, v in count_1.items() if v == 1], reverse=True)
            kickers_2 = sorted([k for k, v in count_2.items() if v == 1], reverse=True)
            for i in range(2):
                if kickers_1[i] > kickers_2[i]:
                    return 1
                elif kickers_2[i] > kickers_1[i]:
                    return 2
            return 3
        
        # Two Pair
        elif p1_score[0] == 3:
            count_1 = Counter(values_1)
            count_2 = Counter(values_2)
            pairs_1 = sorted([k for k, v in count_1.items() if v == 2], reverse=True)
            pairs_2 = sorted([k for k, v in count_2.items() if v == 2], reverse=True)
            
            # Compare higher pairs
            if pairs_1[0] > pairs_2[0]:
                return 1
            elif pairs_2[0] > pairs_1[0]:
                return 2
                
            # Compare lower pairs
            if pairs_1[1] > pairs_2[1]:
                return 1
            elif pairs_2[1] > pairs_1[1]:
                return 2
                
            # Compare kickers
            kicker_1 = [k for k, v in count_1.items() if v == 1][0]
            kicker_2 = [k for k, v in count_2.items() if v == 1][0]
            if kicker_1 > kicker_2:
                return 1
            elif kicker_2 > kicker_1:
                return 2
            return 3
        
        # One Pair
        elif p1_score[0] == 2:
            count_1 = Counter(values_1)
            count_2 = Counter(values_2)
            pair_1 = [k for k, v in count_1.items() if v == 2][0]
            pair_2 = [k for k, v in count_2.items() if v == 2][0]
            
            if pair_1 > pair_2:
                return 1
            elif pair_2 > pair_1:
                return 2
                
            # Compare kickers
            kickers_1 = sorted([k for k, v in count_1.items() if v == 1], reverse=True)
            kickers_2 = sorted([k for k, v in count_2.items() if v == 1], reverse=True)
            for i in range(3):
                if kickers_1[i] > kickers_2[i]:
                    return 1
                elif kickers_2[i] > kickers_1[i]:
                    return 2
            return 3
        
        # High Card
        else:
            for i in range(5):
                if values_1[i] > values_2[i]:
                    return 1
                elif values_2[i] > values_1[i]:
                    return 2
            return 3

    # Helper methods to check hand types
    def _is_royal_flush(self, values, suits):
        return values == [14, 13, 12, 11, 10] and len(set(suits)) == 1

    def _is_straight_flush(self, values, suits):
        return self._is_straight(values) and len(set(suits)) == 1

    def _is_four_kind(self, values):
        return max(Counter(values).values()) == 4

    def _is_full_house(self, values):
        counts = Counter(values).values()
        return sorted(counts) == [2, 3]

    def _is_flush(self, suits):
        return len(set(suits)) == 1

    def _is_straight(self, values):
        # Check regular straight
        if len(set(values)) == 5 and max(values) - min(values) == 4:
            return True
        # Check Ace-low straight (A,2,3,4,5)
        if sorted(values) == [2, 3, 4, 5, 14]:
            return True
        return False

    def _is_three_kind(self, values):
        return max(Counter(values).values()) == 3

    def _is_two_pair(self, values):
        counts = Counter(values).values()
        return sorted(counts) == [1, 2, 2]

    def _is_one_pair(self, values):
        return max(Counter(values).values()) == 2

def determine_winner(player1_cards, player2_cards, community_cards):
    evaluator = PokerHandEvaluator()
    
    p1_score = evaluator.evaluate_hand(player1_cards, community_cards)
    p2_score = evaluator.evaluate_hand(player2_cards, community_cards)
    
    if p1_score[0] > p2_score[0]:
        return f"Player wins with {p1_score[1]}", p1_score[2], 1
    elif p2_score[0] > p1_score[0]:
        return f"Dealer wins with {p2_score[1]}", p2_score[2], 2
    else:
        output = evaluator.evaluate_equal_rank_hands(p1_score, p2_score)
        if output == 1:
            return f"Player wins with a better {p1_score[1]}", p1_score[2], 1
        elif output == 2:
            return f"Dealer wins with a better {p1_score[1]}", p2_score[2], 2
        else:
            return f"Tie!! Both have a {p1_score[1]}", p1_score[2], 3

# def play_poker():
#     game = PokerGame()
#     dealt_cards = game.deal_cards()
#     game.display_cards_dict(dealt_cards)
#     return dealt_cards

# cards = play_poker()
# print(cards)

# result, best_5_cards, winner_index = determine_winner(cards["Player 1"], cards["Player 2"], cards["Community Cards"])
# print(result)

def generate_timestamp():
    # Generate a timestamp in the format YYYYMMDD_HHMMSS
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return timestamp




