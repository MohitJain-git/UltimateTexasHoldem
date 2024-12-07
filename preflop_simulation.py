import pyro
import csv
from tqdm import tqdm
from entire_game import *

class PyroSim1v1:
    def __init__(self):
        self.game = PokerGame()
        
    def simulate_poker_hands_1v1(self, player1_hand, player2_hand, num_simulations=300):
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
            total_results = [0,0,0]
            
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
            
            return total_results

        # Run the simulation
        with pyro.plate('simulation', num_simulations):
            win_percentages = poker_simulation_model(player1_hand, player2_hand)
            
        total = win_percentages[0] + win_percentages[1] + win_percentages[2]

        return {
            'Player 1 Win': round(win_percentages[0]/total * 100, 2),
            'Player 2 Win': round(win_percentages[1]/total * 100, 2),
            'Tie': round(win_percentages[2]/total * 100, 2)
        }

class CSVBatchWriter:
    def __init__(self, filename, batch_size=1000):
        """
        Initialize CSV batch writer
        
        Args:
            filename (str): Output CSV filename
            batch_size (int): Number of rows to write in each batch
        """
        self.filename = filename
        self.batch_size = batch_size
        self.current_batch = []
        self.batch_count = 0
        
        # Write CSV header
        with open(self.filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Player1_Card', 'Player2_Card', 'Player1_Win_Rate', 'Player2_Win_Rate', 'Tie_Rate'
            ])
    
    def add_simulation_result(self, player1_hand, player2_hand, result):
        """
        Add simulation result to batch
        
        Args:
            player1_hand (list): First player's hand
            player2_hand (list): Second player's hand
            result (dict): Simulation results
        """
        self.current_batch.append([
            player1_hand, player2_hand,
            result['Player 1 Win'], 
            result['Player 2 Win'], 
            result['Tie']
        ])
        
        if len(self.current_batch) >= self.batch_size:
            self.flush_batch()
    
    def flush_batch(self):
        """
        Write current batch to CSV and reset
        """
        if not self.current_batch:
            return
        
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.current_batch)
        
        self.batch_count += 1
        print(f"Batch {self.batch_count} written: {len(self.current_batch)} rows")
        self.current_batch = []

game = PokerGame()
evaluator = PokerHandEvaluator()

def get_preflop_abstraction(cards):
        card1, card2 = cards
        rank1, suit1 = card1
        rank2, suit2 = card2
        
        # Convert ranks to values
        value1 = evaluator.card_values[rank1]
        value2 = evaluator.card_values[rank2]
        
        # Order by higher rank
        if value1 < value2:
            value1, value2 = value2, value1
            rank1, rank2 = rank2, rank1

        elif value1 == value2:
            return f"{rank1}{rank2}" # Pair
            
        # Create abstraction
        if suit1 == suit2:
            return f"{rank1}{rank2}s"  # Suited
        else:
            return f"{rank1}{rank2}o"  # Offsuit


def run_comprehensive_poker_simulation():
    """
    Run comprehensive 1v1 poker hand simulation

    """
    output_filename = f'preflop_monte_carlo_{generate_timestamp()}.csv'

    simulator = PyroSim1v1()
    csv_writer = CSVBatchWriter(output_filename)
    
    # Generate all possible hand combination
    deck = game.deck
    
    checklist = []
    # Use tqdm for progress tracking
    for i in tqdm(range(len(deck)), desc="Simulating Hands"):
        for j in range(i+1, len(deck)):
            player1_hand = [deck[i],deck[j]]
            abstracted_p1 = get_preflop_abstraction(player1_hand)

            if abstracted_p1 in checklist:
                continue
            else:
                checklist.append(abstracted_p1)
            
            for k in range(j+1,len(deck)):
                for l in range(k+1,len(deck)):

                    player2_hand = [deck[k],deck[l]]
                    abstracted_p2 = get_preflop_abstraction(player2_hand)

                    # Run simulation
                    result = simulator.simulate_poker_hands_1v1(player1_hand, player2_hand)
                    
                    # Store result
                    csv_writer.add_simulation_result(abstracted_p1, abstracted_p2, result)
    
    # Flush any remaining results
    csv_writer.flush_batch()
    print("Simulation complete. Results saved to", output_filename)

# Run the simulation
if __name__ == "__main__":
    run_comprehensive_poker_simulation()