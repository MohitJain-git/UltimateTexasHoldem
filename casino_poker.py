class CasinoPokerGame:
    def __init__(self, initial_player_stack=1000, initial_dealer_stack=100000, min_amount=10, max_amount=100, min_trip_bet=5, max_trip_bet=100):
        self.player_stack = initial_player_stack
        self.dealer_stack = initial_dealer_stack
        self.max_amount = max_amount
        self.min_amount = min_amount
        self.min_trip_bet = min_trip_bet
        self.max_trip_bet = max_trip_bet
        self.starting_stack = initial_player_stack
        
        # Tracking bet amounts for each round
        self.start_bet = 0
        self.side_bet = False
        self.blind_bet = 0
        self.trip_bet = 0
        self.final_bet = 0
        
        # Tracking round outcomes
        self.round_history = []
    
    def place_bet(self, bet_amount):
        """
        Place the compulsory start bet to start the game
        
        :return: Boolean indicating if ante bet was successful
        """
        if bet_amount > self.player_stack or bet_amount > self.max_amount or bet_amount < self.min_amount:
            return False
        
        self.start_bet = bet_amount
        self.side_bet = True
        self.player_stack -= self.start_bet
        return True
    
    def place_blind_bet(self):
        """
        Place the optional blind bet with higher potential payout
        
        :return: Boolean indicating if blind bet was successful
        """
        if self.start_bet > self.player_stack or self.side_bet == False:
            return False

        self.blind_bet = self.start_bet
        self.player_stack -= self.start_bet
        return True

    def place_trip_bet(self, bet_amount):
        """
        Place an optional trip bet with higher potential payout
        
        :param bet_amount: Amount to bet on the trip
        :return: Boolean indicating if trip bet was successful
        """
        if bet_amount > self.player_stack or self.side_bet == False or bet_amount > self.max_trip_bet or bet_amount < self.min_trip_bet:
            return False
        
        self.trip_bet = bet_amount
        self.player_stack -= bet_amount
        return True
    
    def place_pre_flop_bet(self):
        """
        Place a bet before the flop
        
        :param bet_amount: Amount to bet
        :return: Boolean indicating if bet was successful
        """
        bet_amount = 4 * self.start_bet

        if bet_amount > self.player_stack:
            return False
        
        self.final_bet = bet_amount
        self.player_stack -= bet_amount
        return True
    
    def place_flop_bet(self):
        """
        Place a bet after the flop
        
        :param bet_amount: Amount to bet
        :return: Boolean indicating if bet was successful
        """
        bet_amount = 2 * self.start_bet

        if bet_amount > self.player_stack:
            return False
        
        self.final_bet = bet_amount
        self.player_stack -= bet_amount
        return True
    
    def place_river_bet(self):
        """
        Place a bet after the river
        
        :param bet_amount: Amount to bet
        :return: Boolean indicating if bet was successful
        """
        bet_amount = 1 * self.start_bet

        if bet_amount > self.player_stack:
            return False
        
        self.final_bet = bet_amount
        self.player_stack -= bet_amount
        return True
    
    def get_trip_multiplier(self, score):
    # Define the mapping of scores to payout multipliers
        score_to_multiplier = {
        10: 50,  # Royal Flush (RF)
        9: 40,   # Straight Flush (SF)
        8: 30,   # Quads (Q)
        7: 8,    # Full House (FH)
        6: 7,    # Flush (F)
        5: 4,    # Straight (S)
        4: 3,    # Trips (T)
        3: -1,    # You Lose
        2: -1,    # You Lose
        1: -1,    # You Lose
    }

    # Return the corresponding multiplier or None for invalid scores
        return score_to_multiplier.get(score, None)
    
    def get_blind_multiplier(self, score):
    # Define the mapping of scores to payout multipliers
        score_to_multiplier = {
        10: 500,  # Royal Flush (RF)
        9: 50,   # Straight Flush (SF)
        8: 10,   # Quads (Q)
        7: 3,    # Full House (FH)
        6: 1.5,  # Flush (F)
        5: 1,    # Straight (S)
        4: 0,    # Push
        3: 0,    # Push
        2: 0,    # Push
        1: 0,    # Push
    }

    # Return the corresponding multiplier or None for invalid scores
        return score_to_multiplier.get(score, None)

    def fold(self):
        # Special Case of Resolve where no extra bet is made and there are no payouts
        self.resolve_round(1,1,1,fold = True)

    def resolve_round(self, player_hand_score, dealer_hand_score, player_wins, fold = False):
        # Calculate total main pot
        total_main_pot = self.start_bet + self.final_bet + self.blind_bet + self.trip_bet
        if fold == False:
            # print(self.trip_bet)
            # print(self.get_trip_multiplier(player_hand_score))
            if self.trip_bet:
                trip_bet_win = self.trip_bet + self.trip_bet * self.get_trip_multiplier(player_hand_score)
            else:
                trip_bet_win = 0
                    
            if player_wins == 1 :
                blind_bet_win = self.blind_bet + self.blind_bet * self.get_blind_multiplier(player_hand_score)
                if dealer_hand_score == 1:
                    main_pot_win = (self.final_bet * 2) + self.start_bet
                else:
                    main_pot_win = (self.final_bet + self.start_bet) * 2 
                
            elif player_wins == 2:
                blind_bet_win = 0
                main_pot_win = 0

            else:
                blind_bet_win = self.blind_bet
                main_pot_win = self.final_bet + self.start_bet
            
            player_wins = blind_bet_win + main_pot_win + trip_bet_win
            # print(blind_bet_win)
            # print(main_pot_win)
            # print(trip_bet_win)
            # print("Win logic",player_wins)

            self.player_stack += player_wins


            # Record round outcome
            round_result = {
                'start_bet' : self.start_bet,
                'trip_bet': self.trip_bet,
                'blind_bet' : self.blind_bet,
                'final_bet': self.final_bet,
                'total_bet': total_main_pot,
                'total_win': player_wins - total_main_pot,
                'main_pot_win': main_pot_win,
                'trip_bet_win': trip_bet_win,
                'blind_bet_win': blind_bet_win,
                'player_stack_after': self.player_stack
            }

        else:
            round_result = {
                'start_bet' : self.start_bet,
                'trip_bet': self.trip_bet,
                'blind_bet' : self.blind_bet,
                'final_bet': 0,
                'total_bet': total_main_pot,
                'total_win': -total_main_pot,
                'main_pot_win': 0,
                'trip_bet_win': 0,
                'blind_bet_win': 0,
                'player_stack_after': self.player_stack,
            }

        self.round_history.append(round_result)
        
        # Reset all bets for next round
        self.start_bet = 0
        self.side_bet = False
        self.blind_bet = 0
        self.trip_bet = 0
        self.final_bet = 0
    
    def get_player_stack(self):
        """
        Get current player stack
        
        :return: Current player chip count
        """
        return self.player_stack
    
    def get_dealer_stack(self):
        """
        Get current dealer stack
        
        :return: Current dealer chip count
        """
        return self.dealer_stack
    
    def get_round_history(self):
        """
        Get the history of all rounds played
        
        :return: List of round outcomes
        """
        return self.round_history
    
    def is_game_over(self):
        """
        Check if the game is over (either player or dealer ran out of chips)
        
        :return: Boolean indicating if game is over
        """
        return self.player_stack <= self.min_amount