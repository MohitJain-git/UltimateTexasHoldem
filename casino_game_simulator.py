from entire_game import *
from casino_poker import *
from pyro_simulation import *
from result_graph import *

import sys
from datetime import datetime
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

class CasinoGameSimulator:
    def __init__(self, initial_stack=1000, min_bet=10, max_bet=100, min_trip=5, max_trip=100):
        self.poker_game = PokerGame()
        self.hand_evaluator = PokerHandEvaluator()
        self.poker_sim = PyroPokerSimulation(self.poker_game)
        self.casino_game = CasinoPokerGame(
            initial_player_stack=initial_stack,
            min_amount=min_bet,
            max_amount=max_bet,
            min_trip_bet=min_trip,
            max_trip_bet=max_trip
        )
        
        # Stats tracking
        self.total_hands = 0
        self.hands_won = 0
        self.total_profit = 0
        self.start_time = datetime.now()

    def simulate_hand_with_given_cards(self, start_bet, player_hand, dealer_hand, community_cards, 
                                   make_trip_bet=False, trip_bet_amount=0, verbose=True):
        """Simulate a single hand of Ultimate Texas Hold'em with given cards"""
        
        # Place initial bets
        if not self.casino_game.place_bet(start_bet):
            if verbose:
                print("Invalid bet amount or insufficient funds")
            return False
        
        # Place optional blind bet (always equal to ante in Ultimate Texas Hold'em)
        self.casino_game.place_blind_bet()
        
        # Place optional trips bet
        if make_trip_bet and trip_bet_amount > 0:
            if not self.casino_game.place_trip_bet(trip_bet_amount):
                if verbose:
                    print("Invalid trips bet amount")
                return False
        
        if verbose:
            print(f"\nPlayer's hand: {self.poker_game.display_cards(player_hand)}")
        
        # Split community cards
        flop = community_cards[:3]
        turn = community_cards[3]
        river = community_cards[4]
        
        # Decision point 1: Pre-flop (4x bet)
        # Simple strategy: Bet if we have pocket pairs or high cards
        if self._should_bet_preflop(player_hand):
            if self.casino_game.place_pre_flop_bet():
                if verbose:
                    print("Made 4x pre-flop bet")
        
        # If no pre-flop bet, decision point 2: Post-flop (2x bet)
        elif self._should_bet_flop(player_hand, flop):
            if verbose:
                print(f"Flop: {self.poker_game.display_cards(flop)}")
            if self.casino_game.place_flop_bet():
                if verbose:
                    print("Made 2x flop bet")
        
        # If no flop bet, decision point 3: River (1x bet)
        else:
            if verbose:
                print(f"Flop: {self.poker_game.display_cards(flop)}")
                print(f"Turn: {self.poker_game.display_cards([turn])}")
                print(f"River: {self.poker_game.display_cards([river])}")
            
            community_cards_full = flop + [turn] + [river]
            if self._should_bet_river(player_hand, community_cards_full):
                if self.casino_game.place_river_bet():
                    if verbose:
                        print("Made 1x river bet")
            else:
                if verbose:
                    print("Folded")
                    print(f"\nDealer's hand: {self.poker_game.display_cards(dealer_hand)}")
                self.casino_game.fold()
                self.total_profit = self.casino_game.get_player_stack() - self.casino_game.starting_stack  # Assuming 1000 initial stack
                self.total_hands += 1
                if verbose:
                    print(f"\nHand complete. Current stack: {self.casino_game.get_player_stack()}")
                return True
        
        # Show all cards and evaluate hands
        community_cards_full = flop + [turn] + [river]
        if verbose:
            print(f"\nDealer's hand: {self.poker_game.display_cards(dealer_hand)}")
            print(f"Community cards: {self.poker_game.display_cards(community_cards_full)}")
        
        # Evaluate both hands
        player_result = self.hand_evaluator.evaluate_hand(player_hand, community_cards_full)
        dealer_result = self.hand_evaluator.evaluate_hand(dealer_hand, community_cards_full)
        
        if verbose:
            print(f"\nPlayer has: {player_result[1]}")
            print(f"Dealer has: {dealer_result[1]}")
        
        if player_result[0] > dealer_result[0]:
            winner = 1  # Player wins
        elif player_result[0] < dealer_result[0]:
            winner = 2  # Dealer wins
        else:
            # Equal hand ranks, compare kickers
            winner = self.hand_evaluator.evaluate_equal_rank_hands(player_result, dealer_result)

        if verbose:
            if winner == 1:
                print(f"\nPlayer won")
            elif winner == 2:
                print(f"\nDealer won")
            else:
                print(f"\nIt's a tie")
        
        # Resolve all bets
        self.casino_game.resolve_round(player_result[0], dealer_result[0], winner)
        
        # Update statistics
        self.total_hands += 1
        if winner == 1:
            self.hands_won += 1
        
        self.total_profit = self.casino_game.get_player_stack() - self.casino_game.starting_stack
        
        if verbose:
            print(f"\nHand complete. Current stack: {self.casino_game.get_player_stack()}")
        
        return True

        
    def simulate_hand(self, start_bet, make_trip_bet=False, trip_bet_amount=0, verbose=True):
        """Simulate a single hand of Ultimate Texas Hold'em"""
        # Reset deck for new hand
        self.poker_game.reset_deck()
        
        # Place initial bets
        if not self.casino_game.place_bet(start_bet):
            if verbose:
                print("Invalid bet amount or insufficient funds")
            return False
        
        # Place optional blind bet (always equal to ante in Ultimate Texas Hold'em)
        self.casino_game.place_blind_bet()
        
        # Place optional trips bet
        if make_trip_bet and trip_bet_amount > 0:
            if not self.casino_game.place_trip_bet(trip_bet_amount):
                if verbose:
                    print("Invalid trips bet amount")
                return False
        
        # Deal hole cards
        player_hand = self.poker_game.deal_player_cards()
        dealer_hand = self.poker_game.deal_opponent_cards()
        
        if verbose:
            print(f"\nPlayer's hand: {self.poker_game.display_cards(player_hand)}")
        
        # Deal community cards but don't show them yet
        flop = self.poker_game.deal_flop()
        turn = self.poker_game.deal_turn()
        river = self.poker_game.deal_river()
        
        # Decision point 1: Pre-flop (4x bet)
        # Simple strategy: Bet if we have pocket pairs or high cards
        if self._should_bet_preflop(player_hand):
            if self.casino_game.place_pre_flop_bet():
                if verbose:
                    print("Made 4x pre-flop bet")
        
        # If no pre-flop bet, decision point 2: Post-flop (2x bet)
        elif self._should_bet_flop(player_hand, flop):
            if verbose:
                print(f"Flop: {self.poker_game.display_cards(flop)}")
            if self.casino_game.place_flop_bet():
                if verbose:
                    print("Made 2x flop bet")
        
        # If no flop bet, decision point 3: River (1x bet)
        else:
            if verbose:
                print(f"Flop: {self.poker_game.display_cards(flop)}")
                print(f"Turn: {self.poker_game.display_cards([turn])}")
                print(f"River: {self.poker_game.display_cards([river])}")
            
            community_cards = flop + [turn] + [river]
            if self._should_bet_river(player_hand, community_cards):
                if self.casino_game.place_river_bet():
                    if verbose:
                        print("Made 1x river bet")
            else:
                if verbose:
                    print("Folded")
                    print(f"\nDealer's hand: {self.poker_game.display_cards(dealer_hand)}")
                self.casino_game.fold()
                self.total_profit = self.casino_game.get_player_stack() - 1000  # Assuming 1000 initial stack
                self.total_hands += 1
                if verbose:
                    print(f"\nHand complete. Current stack: {self.casino_game.get_player_stack()}")
                return True
        
        # Show all cards and evaluate hands
        community_cards = flop + [turn] + [river]
        if verbose:
            print(f"\nDealer's hand: {self.poker_game.display_cards(dealer_hand)}")
            print(f"Community cards: {self.poker_game.display_cards(community_cards)}")
        
        # Evaluate both hands
        player_result = self.hand_evaluator.evaluate_hand(player_hand, community_cards)
        dealer_result = self.hand_evaluator.evaluate_hand(dealer_hand, community_cards)
        
        if verbose:
            print(f"\nPlayer has: {player_result[1]}")
            print(f"Dealer has: {dealer_result[1]}")
        

        if player_result[0] > dealer_result[0]:
            winner = 1  # Player wins
        elif player_result[0] < dealer_result[0]:
            winner = 2  # Dealer wins
        else:
            # Equal hand ranks, compare kickers
            winner = self.hand_evaluator.evaluate_equal_rank_hands(player_result, dealer_result)

        if verbose:
            if winner == 1:
                print(f"\nPlayer won")
            elif winner == 2:
                print(f"\nDealer won")
            else:
                print(f"\nIt's a tie")
        
        # Resolve all bets
        self.casino_game.resolve_round(player_result[0], dealer_result[0], winner)
        
        # Update statistics
        self.total_hands += 1
        if winner == 1:
            self.hands_won += 1
        
        self.total_profit = self.casino_game.get_player_stack() - 1000  # Assuming 1000 initial stack
        
        if verbose:
            print(f"\nHand complete. Current stack: {self.casino_game.get_player_stack()}")
        
        return True
    
    def _should_bet_preflop(self, hand):
        """Simple pre-flop betting strategy"""
        # values = [self.hand_evaluator.card_values[card[0]] for card in hand]
        # Bet on pocket pairs or both cards 10 or higher
        # return (values[0] == values[1]) or (min(values) >= 10)
        win_rate = get_win_rate(hand, data)
        # print(win_rate)
        # result = self.poker_sim.simulate_pre_flop(hand)
        if win_rate > 0.56:
            return True
        return False
        # return True
    
    def _should_bet_flop(self, hand, flop):
        """Simple flop betting strategy"""
        # result = self.hand_evaluator.evaluate_hand(hand, flop)
        # # Bet if we have pair or better
        # return result[0] >= 3
        result = self.poker_sim.simulate_scenario_1(hand, flop)
        if result['Player 2 Win'] < 40:
            return True
        return False
        # return True
    
    def _should_bet_river(self, hand, community_cards):
        """Simple river betting strategy"""
        # result = self.hand_evaluator.evaluate_hand(hand, community_cards)
        # # Bet if we have two pair or better
        # return result[0] >= 2
        player_result = self.hand_evaluator.evaluate_hand(hand, community_cards)
        if player_result[0] > 3:
            return True
        result = self.poker_sim.simulate_scenario_3(hand, community_cards)
        if result['Player 2 Win'] < 45:
            return True
        return False
    
    def calculate_total_wins(self,round_results):
        """
        Calculate the sum of different types of wins from a list of round results.
        
        Args:
            round_results (list): List of dictionaries containing round results
            
        Returns:
            dict: Dictionary containing the sums of different types of wins
        """
        sums = {
            'total_wins_sum': sum(result['total_win'] for result in round_results),
            'main_pot_wins_sum': sum(result['main_pot_win'] for result in round_results),
            'blind_bet_wins_sum': sum(result['blind_bet_win'] for result in round_results),
            'trip_bet_wins_sum': sum(result['trip_bet_win'] for result in round_results)
        }
        
        return sums
    
    def simulate_session(self, num_hands=100, start_bet=10, make_trip_bet=False, trip_bet_amount=0, verbose=False):
        """Simulate multiple hands"""
        for i in range(num_hands):
            if verbose:
                print(f"\n=== Hand {i+1} ===")
            
            if not self.simulate_hand(start_bet, make_trip_bet, trip_bet_amount, verbose):
                break
                
            if self.casino_game.is_game_over():
                if verbose:
                    print("Game over - out of chips!")
                break
        
        self._print_session_stats()
        final_results = self.casino_game.get_round_history()
        print(self.calculate_total_wins(final_results))

    def _print_session_stats(self):
        """Print statistics for the session"""
        duration = datetime.now() - self.start_time
        print("\n=== Session Statistics ===")
        print(f"Total hands played: {self.total_hands}")
        print(f"Hands won: {self.hands_won}")
        print(f"Win rate: {(self.hands_won/self.total_hands)*100:.1f}%")
        print(f"Total profit/loss: ${self.total_profit}")
        print(f"Average profit per hand: ${self.total_profit/self.total_hands:.2f}")
        print(f"Session duration: {duration}")
        print(f"Final chip stack: ${self.casino_game.get_player_stack()}")

# Example usage:
def main():
    # Initialize simulator with default values
    simulator = CasinoGameSimulator(initial_stack=1000, min_bet=10, max_bet=100)
    
    # Simulate a session of 100 hands with $10 bets
    simulator.simulate_session(
        num_hands=100,
        start_bet=10,
        make_trip_bet=False,
        trip_bet_amount=0,
        verbose=True # Set to True for detailed hand information
    )

if __name__ == "__main__":
    
    output_file = f"casino_sim_{generate_timestamp()}.txt"
    with open(output_file, "w") as file:
        sys.stdout = file  # Redirect print statements to the file
        main()
        # Reset stdout to default (optional)
        sys.stdout = sys.__stdout__
        print(f"All print statements have been written to {output_file}.")
        
    plot_graph(output_file)