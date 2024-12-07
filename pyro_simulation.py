import torch
import pyro
import pyro.distributions as dist
import numpy as np
from entire_game import *
import csv

class PyroPokerSimulation:
    def __init__(self, game):
        """
        Initialize the Pyro-based Poker Simulation
        
        Args:
            game (PokerGame): An instance of the poker game class
        """
        self.game = game
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def simulate_poker_hands_1v1(self, player1_hand, player2_hand, num_simulations=10000):
        """
        Simulate poker hands with fixed player hands and random community cards using Pyro.
        
        Args:
            player1_hand (list): First player's initial hand
            player2_hand (list): Second player's initial hand
            num_simulations (int): Number of Monte Carlo simulations
        
        Returns:
            dict: Win percentages for each player and ties
        """
        def poker_simulation_model(player1_hand, player2_hand):
            # Track wins and outcomes
            total_results = torch.zeros(3, device=self.device)
            
            for _ in range(num_simulations):
                # Reset the deck
                self.game.reset_deck()
                
                # Remove player cards from the deck
                initial_dealt = set(player1_hand + player2_hand)
                for card in initial_dealt:
                    if card in self.game.deck:
                        self.game.deck.remove(card)
                
                # Draw community cards
                flop = self.game.deal_flop(initial_dealt)
                turn = self.game.deal_turn(initial_dealt.union(set(flop)))
                river = self.game.deal_river(initial_dealt.union(set(flop), {turn}))
                
                # Combine community cards
                community_cards = flop + [turn, river]
                
                # Determine winner
                _, _, winner = determine_winner(
                    player1_hand, player2_hand, community_cards
                )
                
                # Update results
                if winner == 1:
                    total_results[0] += 1
                elif winner == 2:
                    total_results[1] += 1
                else:
                    total_results[2] += 1
            
            return total_results / num_simulations

        # Run the simulation
        with pyro.plate('simulation', num_simulations):
            win_percentages = poker_simulation_model(player1_hand, player2_hand)
        
        # Convert to dictionary
        return {
            'Player 1 Win': round(win_percentages[0].item() * 100, 2),
            'Player 2 Win': round(win_percentages[1].item() * 100, 2),
            'Tie': round(win_percentages[2].item() * 100, 2)
        }

    def simulate_pre_flop(self, player_cards, num_opponent_draws=100, num_community_draws=100):
        """
        Simulate pre-flop scenarios with Pyro sampling.
        
        Args:
            player_cards (list): Player's initial hand
            num_opponent_draws (int): Number of opponent hand draws
            num_community_draws (int): Number of community card draws
        
        Returns:
            dict: Win percentages for the player
        """
        def pre_flop_model(player_cards):
            # Track wins and outcomes
            total_results = torch.zeros(3, device=self.device)
            
            for _ in range(num_opponent_draws):
                # Reset the deck
                self.game.reset_deck()
                
                # Track dealt cards
                initial_dealt = set(player_cards)
                
                # Remove initial dealt cards from the deck
                for card in initial_dealt:
                    if card in self.game.deck:
                        self.game.deck.remove(card)
                
                # Draw opponent cards
                opponent_cards = self.game.deal_opponent_cards(initial_dealt)
                
                # Track cards already dealt
                current_dealt = initial_dealt.union(set(opponent_cards))
                
                # Inner simulation for community cards
                for _ in range(num_community_draws):
                    # Reset the deck for this community card iteration
                    self.game.reset_deck()
                    
                    # Remove initial dealt cards from the deck
                    for card in current_dealt:
                        if card in self.game.deck:
                            self.game.deck.remove(card)
                    
                    # Draw community cards
                    flop = self.game.deal_flop(current_dealt)
                    turn = self.game.deal_turn(current_dealt.union(set(flop)))
                    river = self.game.deal_river(current_dealt.union(set(flop), {turn}))
                    
                    # Combine community cards
                    community_cards = flop + [turn, river]
                    
                    # Determine winner
                    _, _, winner = determine_winner(
                        player_cards, opponent_cards, community_cards
                    )
                    
                    # Update results
                    if winner == 1:
                        total_results[0] += 1
                    elif winner == 2:
                        total_results[1] += 1
                    else:
                        total_results[2] += 1
            
            return total_results / (num_opponent_draws * num_community_draws)

        # Run the simulation
        with pyro.plate('simulation', num_opponent_draws * num_community_draws):
            win_percentages = pre_flop_model(player_cards)
        
        # Convert to dictionary
        return {
            'Player 1 Win': round(win_percentages[0].item() * 100, 2),
            'Player 2 Win': round(win_percentages[1].item() * 100, 2),
            'Tie': round(win_percentages[2].item() * 100, 2)
        }

    def simulate_scenario_1(self, player_cards, flop, num_opponent_draws=100, num_turn_river_draws=100):
        """
        Simulate scenario with fixed player cards and flop using Pyro.
        
        Args:
            player_cards (list): Player's initial hand
            flop (list): Community flop cards
            num_opponent_draws (int): Number of opponent hand draws
            num_turn_river_draws (int): Number of turn and river card draws
        
        Returns:
            dict: Win percentages for the player
        """
        def scenario_1_model(player_cards, flop):
            # Track wins and outcomes
            total_results = torch.zeros(3, device=self.device)
            
            for _ in range(num_opponent_draws):
                # Reset the deck
                self.game.reset_deck()
                
                # Track dealt cards
                initial_dealt = set(player_cards + flop)
                
                # Draw opponent cards
                opponent_cards = self.game.deal_opponent_cards(initial_dealt)
                
                # Track cards already dealt
                current_dealt = initial_dealt.union(set(opponent_cards))
                
                # Inner simulation for turn and river
                for _ in range(num_turn_river_draws):
                    # Reset the deck for this inner iteration
                    self.game.reset_deck()
                    
                    # Ensure initial cards are removed from the deck
                    for card in initial_dealt.union(set(opponent_cards)):
                        if card in self.game.deck:
                            self.game.deck.remove(card)
                    
                    # Draw turn
                    turn = self.game.deal_turn(current_dealt)
                    
                    # Draw river
                    river = self.game.deal_river(current_dealt.union({turn}))
                    
                    # Combine community cards
                    community_cards = flop + [turn, river]
                    
                    # Determine winner
                    _, _, winner = determine_winner(
                        player_cards, opponent_cards, community_cards
                    )
                    
                    # Update results
                    if winner == 1:
                        total_results[0] += 1
                    elif winner == 2:
                        total_results[1] += 1
                    else:
                        total_results[2] += 1
            
            return total_results / (num_opponent_draws * num_turn_river_draws)

        # Run the simulation
        with pyro.plate('simulation', num_opponent_draws * num_turn_river_draws):
            win_percentages = scenario_1_model(player_cards, flop)
        
        # Convert to dictionary
        return {
            'Player 1 Win': round(win_percentages[0].item() * 100, 2),
            'Player 2 Win': round(win_percentages[1].item() * 100, 2),
            'Tie': round(win_percentages[2].item() * 100, 2)
        }

    def simulate_scenario_2(self, player_cards, flop, turn, num_opponent_draws=100, num_river_draws=100):
        """
        Simulate scenario with fixed player cards, flop, and turn using Pyro.
        
        Args:
            player_cards (list): Player's initial hand
            flop (list): Community flop cards
            turn (card): Community turn card
            num_opponent_draws (int): Number of opponent hand draws
            num_river_draws (int): Number of river card draws
        
        Returns:
            dict: Win percentages for the player
        """
        def scenario_2_model(player_cards, flop, turn):
            # Track wins and outcomes
            total_results = torch.zeros(3, device=self.device)
            
            for _ in range(num_opponent_draws):
                # Reset the deck
                self.game.reset_deck()
                
                # Track dealt cards
                initial_dealt = set(player_cards + flop + [turn])
                
                # Draw opponent cards
                opponent_cards = self.game.deal_opponent_cards(initial_dealt)
                
                # Track cards already dealt
                current_dealt = initial_dealt.union(set(opponent_cards))
                
                # Inner simulation for river
                for _ in range(num_river_draws):
                    # Reset the deck for this inner iteration
                    self.game.reset_deck()
                    
                    # Ensure initial cards are removed from the deck
                    for card in initial_dealt.union(set(opponent_cards)):
                        if card in self.game.deck:
                            self.game.deck.remove(card)
                    
                    # Draw river
                    river = self.game.deal_river(current_dealt)
                    
                    # Combine community cards
                    community_cards = flop + [turn, river]
                    
                    # Determine winner
                    _, _, winner = determine_winner(
                        player_cards, opponent_cards, community_cards
                    )
                    
                    # Update results
                    if winner == 1:
                        total_results[0] += 1
                    elif winner == 2:
                        total_results[1] += 1
                    else:
                        total_results[2] += 1
            
            return total_results / (num_opponent_draws * num_river_draws)

        # Run the simulation
        with pyro.plate('simulation', num_opponent_draws * num_river_draws):
            win_percentages = scenario_2_model(player_cards, flop, turn)
        
        # Convert to dictionary
        return {
            'Player 1 Win': round(win_percentages[0].item() * 100, 2),
            'Player 2 Win': round(win_percentages[1].item() * 100, 2),
            'Tie': round(win_percentages[2].item() * 100, 2)
        }

    def simulate_scenario_3(self, player_cards, community_cards, num_opponent_draws=100):
        """
        Simulate scenario with all community cards fixed using Pyro.
        
        Args:
            player_cards (list): Player's initial hand
            community_cards (list): All community cards
            num_opponent_draws (int): Number of opponent hand draws
        
        Returns:
            dict: Win percentages for the player
        """
        def scenario_3_model(player_cards, community_cards):
            # Track wins and outcomes
            total_results = torch.zeros(3, device=self.device)
            
            for _ in range(num_opponent_draws):
                # Reset the deck
                self.game.reset_deck()
                
                # Track dealt cards
                initial_dealt = set(player_cards + community_cards)
                
                # Ensure initial cards are removed from the deck
                for card in initial_dealt:
                    if card in self.game.deck:
                        self.game.deck.remove(card)
                
                # Draw opponent cards
                opponent_cards = self.game.deal_opponent_cards(initial_dealt)
                
                # Determine winner
                _, _, winner = determine_winner(
                    player_cards, opponent_cards, community_cards
                )
                
                # Update results
                if winner == 1:
                    total_results[0] += 1
                elif winner == 2:
                    total_results[1] += 1
                else:
                    total_results[2] += 1
            
            return total_results / num_opponent_draws

        # Run the simulation
        with pyro.plate('simulation', num_opponent_draws):
            win_percentages = scenario_3_model(player_cards, community_cards)
        
        # Convert to dictionary
        return {
            'Player 1 Win': round(win_percentages[0].item() * 100, 2),
            'Player 2 Win': round(win_percentages[1].item() * 100, 2),
            'Tie': round(win_percentages[2].item() * 100, 2)
        }
    
    
# Function to determine if cards are suited
def are_suited(card1_suit, card2_suit):
    return "Suited" if card1_suit == card2_suit else "Unsuited"

# Example usage function (similar to original)
def run_simulations(game):
    # Create simulation instance
    simulator = PyroPokerSimulation(game)
    
    # Deal initial cards
    cards = game.deal_cards()
    player_cards = cards['Player 1']
    
    print("Player Cards:", game.display_cards(player_cards))

    print("\nScenario 0 (Player Cards Fixed):")
    result_0 = simulator.simulate_pre_flop(player_cards)
    print(result_0)
    print()

    flop = game.deal_flop(set(player_cards))
    print("Flop:", game.display_cards(flop))
    
    # Scenario 1: Fixed player cards and flop
    print("\nScenario 1 (Player Cards + Flop Fixed):")
    result_1 = simulator.simulate_scenario_1(player_cards, flop)
    print(result_1)
    print()

    turn = game.deal_turn(set(player_cards).union(set(flop)))
    print("Turn:", game.display_cards([turn]))
    
    # Scenario 2: Fixed player cards, flop, and turn
    print("\nScenario 2 (Player Cards, Flop, Turn Fixed):")
    result_2 = simulator.simulate_scenario_2(player_cards, flop, turn)
    print(result_2)
    print()

    river = game.deal_river(set(player_cards).union(set(flop), {turn}))
    print("River:", game.display_cards([river]))
    
    # Scenario 3: All community cards fixed
    community_cards = flop + [turn, river]
    print("\nScenario 3 (All Community Cards Fixed):")
    result_3 = simulator.simulate_scenario_3(player_cards, community_cards)
    print(result_3)
    print()

# Load data from CSV
def load_data(csv_file):
    data = []
    with open(csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["First_Card"] == "T" or row["Second_Card"] == "T":
                if row["First_Card"] == "T":
                    row["First_Card"] = "10"
                if row["Second_Card"] == "T":
                    row["Second_Card"] = "10"
            data.append({
                "card1": row["First_Card"],
                "card2": row["Second_Card"],
                "type": row["Hand_Type"],
                "win_rate": float(row["Win_Rate"])
            })
    return data

def get_win_rate(player_cards, data):

    card1_rank, card1_suit = player_cards[0][0], player_cards[0][1]
    card2_rank, card2_suit = player_cards[1][0], player_cards[1][1]
        
    # Determine the card type (Pair, Suited, Unsuited)
    if card1_rank == card2_rank:
        card_type = "Pair"
    else:
        card_type = are_suited(card1_suit, card2_suit)
    
    # Lookup win rate
    for entry in data:
        if (
            (entry["card1"] == card1_rank and entry["card2"] == card2_rank or
             entry["card1"] == card2_rank and entry["card2"] == card1_rank) and
            entry["type"] == card_type
        ):
            return float(entry["win_rate"])
    
    return 0


csv_file = "poker_hand_statistics.csv"  # Replace with your CSV file name
data = load_data(csv_file)