import re
import pandas as pd
import matplotlib.pyplot as plt
import os

def parse_output_file(filename):
    """
    Parse the output file to extract hand-by-hand information
    """
    hands = [{"hand_number":0, "stack":1000}]
    current_hand = {}
    
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    # Regular expressions for parsing
    hand_start_pattern = re.compile(r'=== Hand (\d+) ===')
    stack_pattern = re.compile(r'Current stack: (\d+)')
    
    for line in lines:
        hand_match = hand_start_pattern.search(line)
        stack_match = stack_pattern.search(line)
        
        if hand_match:
            # Start of a new hand
            if current_hand:
                hands.append(current_hand)
            current_hand = {'hand_number': int(hand_match.group(1))}
        
        if stack_match:
            current_hand['stack'] = int(stack_match.group(1))
    
    # Append the last hand
    if current_hand:
        hands.append(current_hand)
    
    return pd.DataFrame(hands)

def create_stack_size_plot(df, input_filename):
    """
    Create stack size progression plot and save with input filename
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df['hand_number'], df['stack'], marker='o', linestyle='-', markersize=6)
    plt.title('Stack Size Progression', fontsize=16)
    plt.xlabel('Hand Number', fontsize=12)
    plt.ylabel('Stack Size ($)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Add horizontal line for initial stack
    initial_stack = 1000
    plt.axhline(y=initial_stack, color='r', linestyle='--', label='Initial Stack')
    
    # Annotate final stack
    final_stack = df['stack'].iloc[-1]
    plt.annotate(f'Final Stack: ${final_stack}', 
                 xy=(df['hand_number'].iloc[-1], final_stack),
                 xytext=(10, 10), 
                 textcoords='offset points',
                 fontsize=10,
                 bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
    
    plt.legend()
    plt.tight_layout()
    
    # Create output filename
    base_filename = os.path.splitext(input_filename)[0]
    output_filename = f"{base_filename}_analysis.png"
    
    plt.savefig(output_filename)
    plt.close()
    
    print()
    print(f"Stack size analysis plot saved as {output_filename}")

def plot_graph(input_filename='output_2.txt'):
    # Parse the output file
    df = parse_output_file(input_filename)
    
    # Create stack size progression plot
    create_stack_size_plot(df, input_filename)
    
    # Print some basic statistics
    print("\nGame Statistics:")
    print(f"Total Hands: {len(df) - 1}")
    print(f"Starting Stack: $1000")
    print(f"Ending Stack: ${df['stack'].iloc[-1]}")
    print(f"Total Profit/Loss: ${df['stack'].iloc[-1] - 1000}")

if __name__ == '__main__':
    plot_graph(r'conservative_player.txt')