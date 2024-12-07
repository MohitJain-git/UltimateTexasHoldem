import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk

from entire_game import * 
from casino_poker import CasinoPokerGame
from casino_game_simulator import *

# Constants
CARD_IMAGES = [f"card_images/{suit}_{rank}.png" for suit in ["hearts", "diamonds", "clubs", "spades"] for rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]]
STARTING_BALANCE = 1000

class PokerGameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Texas Holdem")
        self.root.geometry("1200x800")
        
        # Game initialization
        self.game = PokerGame()
        self.casino_game = CasinoPokerGame()
        self.evaluate = PokerHandEvaluator()
        self.bot_simulator = CasinoGameSimulator()
        
        # Game stats tracking
        self.total_hands = 0
        self.hands_won = 0
        self.total_profit = 0
        self.start_time = datetime.now()
        self.output_player_txt = f'player_stats_{generate_timestamp()}.txt'
        self.output_bot_txt = f'bot_stats_{generate_timestamp()}.txt'
        self.starting_stack = self.casino_game.get_player_stack()

        # Round state tracking
        self.game_stage = "initial"  # Possible stages: initial, ante, pre-flop, flop, river, showdown
        self.player_cards = []
        self.dealer_cards = []
        self.com_cards = []
        
        # Setup UI components
        self.setup_ui()
    
    def setup_ui(self):
        # Player Balance Display
        self.balance_frame = tk.Frame(self.root)
        self.balance_frame.pack(pady=10)
        
        self.balance_label = tk.Label(self.balance_frame, 
                                      text=f"Player Balance: ${self.casino_game.get_player_stack()}", 
                                      font=("Arial", 14))
        self.balance_label.pack()
        
        # Game Stage Label
        self.stage_label = tk.Label(self.root, text="Game Stage: Initial", font=("Arial", 12))
        self.stage_label.pack(pady=5)
        
        # Card Display Frames
        self.dealer_card_frame = self.create_card_frame("Dealer Cards")
        self.com_card_frame = self.create_card_frame("Community Cards")
        self.player_card_frame = self.create_card_frame("Player Cards")
        
        # Action Buttons Frame
        self.action_frame = tk.Frame(self.root)
        self.action_frame.pack(pady=10)
        
        # Initial Ante Button
        self.ante_button = tk.Button(self.action_frame, text="Place Ante", command=self.place_ante, 
                                     font=("Arial", 10))
        self.ante_button.pack(side=tk.LEFT, padx=5)
    
    def create_card_frame(self, label_text):
        label = tk.Label(self.root, text=label_text)
        label.pack(pady=5)
        
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        return frame
    
    def place_ante(self):
        # Prompt for ante bet amount
        ante_amount = simpledialog.askinteger("Ante Bet", 
                                               "Enter Ante Bet Amount:",
                                               initialvalue=10, 
                                               minvalue=10, 
                                               maxvalue=self.casino_game.max_amount)
        
        if ante_amount is not None:
            if self.casino_game.place_bet(ante_amount):
                # Automatically place blind bet
                self.casino_game.place_blind_bet()
                
                # Optional trip bet
                trip_amount = simpledialog.askinteger("Trip Bet (Optional)", 
                                                      "Enter Trip Bet Amount (0 to skip):", 
                                                      initialvalue=5,
                                                      minvalue=0, 
                                                      maxvalue=self.casino_game.max_trip_bet)
                if trip_amount is not None and trip_amount > 0:
                    if not self.casino_game.place_trip_bet(trip_amount):
                        messagebox.showerror("Bet Error", "Cannot place blind bet.")
                
                # Update balance
                self.balance_label.config(text=f"Player Balance: ${self.casino_game.get_player_stack()}")
                
                # Clear previous card displays
                for frame in [self.player_card_frame, self.dealer_card_frame, self.com_card_frame]:
                    for widget in frame.winfo_children():
                        widget.destroy()
                
                # Deal cards
                dealt_cards = self.game.deal_cards()
                self.player_cards = dealt_cards["Player 1"]
                # print(self.player_cards)
                self.dealer_cards = dealt_cards["Player 2"]
                # print(self.dealer_cards)
                self.com_cards = dealt_cards["Community Cards"]
                
                # Display player cards
                self.display_cards(self.player_cards, self.player_card_frame)
                
                # Update game stage
                self.game_stage = "pre-flop"
                self.stage_label.config(text="Game Stage: Pre-Flop")
                
                # Setup pre-flop action buttons
                self.setup_preflop_actions()
            else:
                messagebox.showerror("Bet Error", "Invalid bet amount. Please try again.")
    
    def setup_preflop_actions(self):
        # Clear previous action buttons
        for widget in self.action_frame.winfo_children():
            widget.destroy()
        
        # Check button
        check_button = tk.Button(self.action_frame, text="Check", command=self.place_blind_bet, 
                                 font=("Arial", 10))
        check_button.pack(side=tk.LEFT, padx=5)
        
        # Pre-Flop Bet button
        preflop_bet_button = tk.Button(self.action_frame, text="Pre-Flop Bet", command=self.place_preflop_bet, 
                                       font=("Arial", 10))
        preflop_bet_button.pack(side=tk.LEFT, padx=5)
    
    def place_blind_bet(self):
        
        self.balance_label.config(text=f"Player Balance: ${self.casino_game.get_player_stack()}")
        
        # Display first 3 community cards
        self.display_cards(self.com_cards[:3], self.com_card_frame)
        
        # Update game stage
        self.game_stage = "flop"
        self.stage_label.config(text="Game Stage: Flop")
        
        # Setup flop action buttons
        self.setup_flop_actions()
    
    def place_preflop_bet(self):
        if self.casino_game.place_pre_flop_bet():
            # Update balance
            self.balance_label.config(text=f"Player Balance: ${self.casino_game.get_player_stack()}")
            
            # Go directly to showdown
            self.go_to_showdown()
        else:
            messagebox.showerror("Bet Error", "Cannot place pre-flop bet.")
    
    def setup_flop_actions(self):
        # Clear previous action buttons
        for widget in self.action_frame.winfo_children():
            widget.destroy()
        
        # Check button
        check_button = tk.Button(self.action_frame, text="Check", command=self.place_river_cards, 
                                 font=("Arial", 10))
        check_button.pack(side=tk.LEFT, padx=5)

        # Flop Bet button
        flop_bet_button = tk.Button(self.action_frame, text="Flop Bet", command=self.place_flop_bet, 
                                    font=("Arial", 10))
        flop_bet_button.pack(side=tk.LEFT, padx=5)
    
    def place_flop_bet(self):
        if self.casino_game.place_flop_bet():
            # Update balance
            self.balance_label.config(text=f"Player Balance: ${self.casino_game.get_player_stack()}")
            
            # Go directly to showdown
            self.go_to_showdown()
        else:
            messagebox.showerror("Bet Error", "Cannot place flop bet.")
    
    def place_river_cards(self):
        # Add 4th and 5th community cards
        self.display_cards(self.com_cards, self.com_card_frame)
        
        # Update game stage
        self.game_stage = "river"
        self.stage_label.config(text="Game Stage: River")
        
        # Setup river action buttons
        self.setup_river_actions()
    
    def setup_river_actions(self):
        # Clear previous action buttons
        for widget in self.action_frame.winfo_children():
            widget.destroy()
        
        # River Bet button
        river_bet_button = tk.Button(self.action_frame, text="River Bet", command=self.place_river_bet, 
                                     font=("Arial", 10))
        river_bet_button.pack(side=tk.LEFT, padx=5)
        
        # Fold button
        fold_button = tk.Button(self.action_frame, text="Fold", command=self.fold, 
                                font=("Arial", 10))
        fold_button.pack(side=tk.LEFT, padx=5)
    
    def place_river_bet(self):
        if self.casino_game.place_river_bet():
            # Update balance
            self.balance_label.config(text=f"Player Balance: ${self.casino_game.get_player_stack()}")
            
            # Go directly to showdown
            self.go_to_showdown()
        else:
            messagebox.showerror("Bet Error", "Cannot place river bet.")
    
    def fold(self):

        self.display_cards(self.dealer_cards, self.dealer_card_frame)
        # Call fold method in casino game
        self.casino_game.fold()

        self.total_profit = self.casino_game.get_player_stack() - self.starting_stack
        self.total_hands += 1

        self.append_hand_to_txt(self.casino_game.round_history, "Player Folded!")
        self.bot_logic()
        
        # Update balance
        self.balance_label.config(text=f"Player Balance: ${self.casino_game.get_player_stack()}")
        
        # Show result message
        messagebox.showinfo("Game Result", "You folded. Player Balance: $" + str(self.casino_game.get_player_stack()))
        
        # Setup new game button
        self.setup_new_game_actions()
    
    def go_to_showdown(self):
        # Update game stage
        self.game_stage = "showdown"
        self.stage_label.config(text="Game Stage: Showdown")
        
        # Add full community cards
        self.display_cards(self.com_cards, self.com_card_frame)
        
        # Setup showdown actions
        self.setup_showdown_actions()
    
    def setup_showdown_actions(self):
        # Clear previous action buttons
        for widget in self.action_frame.winfo_children():
            widget.destroy()
        
        # Showdown button
        showdown_button = tk.Button(self.action_frame, text="Showdown", command=self.showdown, 
                                    font=("Arial", 10))
        showdown_button.pack(side=tk.LEFT, padx=5)
    
    def showdown(self):
        # Display dealer cards
        self.display_cards(self.dealer_cards, self.dealer_card_frame)
        
        # Determine winner
        result, best_5_cards, winner_index = determine_winner(self.player_cards, self.dealer_cards, self.com_cards)
        
        # Get hand scores
        player_hand_score = self.evaluate.evaluate_hand(self.player_cards, self.com_cards)
        dealer_hand_score = self.evaluate.evaluate_hand(self.dealer_cards, self.com_cards)

        # Resolve the round
        self.casino_game.resolve_round(player_hand_score[0], dealer_hand_score[0], winner_index)

        if winner_index == 1:
            self.hands_won += 1
        self.total_profit = self.casino_game.get_player_stack() - self.starting_stack
        self.total_hands += 1

        ## Write a funciton Input the values into the logs of the player and also get the output for each hand as the bot.
        ## Also add this function when the player folds
        ## Write a function to get the graphs for the same as well
        self.append_hand_to_txt(self.casino_game.round_history, result)
        self.bot_logic()

        
        # Update balance
        self.balance_label.config(text=f"Player Balance: ${self.casino_game.get_player_stack()}")
        
        # Show result message
        messagebox.showinfo("Game Result", f"{result}\nPlayer Balance: ${self.casino_game.get_player_stack()}")
        
        # Setup new game button
        self.setup_new_game_actions()
        
        # Check if game is over
        if self.casino_game.is_game_over():
            messagebox.showinfo("Game Over", "You've run out of chips!")
            self.root.quit()

    def setup_new_game_actions(self):
        # Clear previous action buttons
        for widget in self.action_frame.winfo_children():
            widget.destroy()
        
        # New Game button
        new_game_button = tk.Button(self.action_frame, text="New Game", command=self.reset_game, 
                                    font=("Arial", 10))
        new_game_button.pack(side=tk.LEFT, padx=5)
    
    def reset_game(self):
        # Clear all card frames
        for frame in [self.player_card_frame, self.dealer_card_frame, self.com_card_frame]:
            for widget in frame.winfo_children():
                widget.destroy()
        
        # Reset game stage
        self.game_stage = "initial"
        self.stage_label.config(text="Game Stage: Initial")
        
        # Reset action buttons
        for widget in self.action_frame.winfo_children():
            widget.destroy()
        
        # Reset ante button
        self.ante_button = tk.Button(self.action_frame, text="Place Ante", command=self.place_ante, 
                                     font=("Arial", 10))
        self.ante_button.pack(side=tk.LEFT, padx=5)
        
        # Reset player and game state
        self.player_cards = []
        self.dealer_cards = []
        self.com_cards = []
    
    def convert_to_image_name(self, cards):
        suit_map = {'H': 'hearts', 'D': 'diamonds', 'C': 'clubs', 'S': 'spades'}
        rank_map = {'2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', 
                    '9': '9', '10': '10', 'J': 'jack', 'Q': 'queen', 'K': 'king', 'A': 'ace'}
        
        converted_cards = [f"card_images/{suit_map[suit]}_{rank_map[rank]}.png" for rank, suit in cards]
        return converted_cards
    
    def append_hand_to_txt(self, round_results, result):
        with open(self.output_player_txt, "a") as file:
            sys.stdout = file  # Redirect print statements to the file
            print(f"\n=== Hand {self.total_hands} ===")
            print(f"\nPlayer's hand: {self.game.display_cards(self.player_cards)}")
            print(f"\nDealer's hand: {self.game.display_cards(self.dealer_cards)}")
            print(f"Community cards: {self.game.display_cards(self.com_cards)}")
            print(result)
            print(self.calculate_total_wins(round_results))
            print(f"\nHand complete. Current stack: {self.casino_game.get_player_stack()}")
            sys.stdout = sys.__stdout__
        
    def bot_logic(self):
        with open(self.output_bot_txt, "a") as file:
            sys.stdout = file  # Redirect print statements to the file
            print(f"\n=== Hand {self.total_hands} ===")
            self.bot_simulator.simulate_hand_with_given_cards(10, self.player_cards, self.dealer_cards, self.com_cards, make_trip_bet=True, trip_bet_amount=5)
            sys.stdout = sys.__stdout__

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

    def calculate_total_wins(self,round_results):
        sums = {
            'total_wins_sum': sum(result['total_win'] for result in round_results),
            'main_pot_wins_sum': sum(result['main_pot_win'] for result in round_results),
            'blind_bet_wins_sum': sum(result['blind_bet_win'] for result in round_results),
            'trip_bet_wins_sum': sum(result['trip_bet_win'] for result in round_results)
        }
        
        return sums
    
    def display_cards(self, cards, frame, width=100, height=150):
        # Clear previous cards in the frame
        for widget in frame.winfo_children():
            widget.destroy()
        
        # Display cards
        for card in self.convert_to_image_name(cards):
            image = Image.open(card)
            image = image.resize((width, height), Image.LANCZOS)
            card_img = ImageTk.PhotoImage(image)
            card_label = tk.Label(frame, image=card_img)
            card_label.image = card_img  # Keep reference to avoid garbage collection
            card_label.pack(side=tk.LEFT)

if __name__ == "__main__":
    root = tk.Tk()
    game = PokerGameUI(root)
    root.mainloop()

    plot_graph(game.output_bot_txt)
    plot_graph(game.output_player_txt)