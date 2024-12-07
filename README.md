# Ultimate Texas Hold'em

A Python implementation of the popular casino poker variant Ultimate Texas Hold'em with a graphical user interface built using Tkinter.

## Features

- Interactive GUI built with Tkinter
- Complete Ultimate Texas Hold'em gameplay mechanics
- Player vs Dealer format
- Real-time betting system
- Card visualization
- Hand evaluation and comparison

## Installation

```bash
git clone https://github.com/MohitJain-git/UltimateTexasHoldem.git
cd UltimateTexasHoldem
pip install -r requirements.txt
```

## Usage

To start the game, run:

```bash
python ui.py
```

## Output

After you exit the game, two text files will be generated one for the bot and the other is the players hands, and for each of them, there will be a graph generated showing the performance wrt to each hand played

## Game Rules

Ultimate Texas Hold'em is played against the dealer:
- Players make equal Ante and Blind bets before the cards are dealt
- Players receive two hole cards and combine them with five community cards to make their best five-card hand
- Betting rounds proceed as follows:
  - Pre-flop: Players can bet 3x or 4x their Ante before seeing community cards
  - Flop: Players can bet 2x their Ante after seeing three community cards
  - River: Players can bet 1x their Ante after all community cards are revealed
- Best five-card poker hand wins

**Optional Bets**
- Trips Bet: Players win if their final five-card hand is three of a kind or higher

**Payouts**
![image](https://github.com/user-attachments/assets/23642d3e-f9bd-4ee6-aad0-5ab49cc5ad02)

**Hand Rankings** (highest to lowest):
- Royal Flush
- Straight Flush
- Four of a Kind
- Full House
- Flush
- Straight
- Three of a Kind
- Two Pair
- Pair
- High Card
