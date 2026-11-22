#!/usr/bin/env python3
"""
WFL Enriched Goals Table Creator
================================

This script processes WFL (Winnipeg Football League) CSV data to create an enriched goals table
that maps individual player goals to specific games with sequential numbering.

The script reads two CSV files:
1. Goals data (unformatted) - contains player goals by date
2. Games data - contains game information and scores

Output: A comprehensive table with GameID, player_name, team, and goal_num columns.

Author: AI Assistant
Date: 2025
"""

import pandas as pd
import re

def create_full_enriched_goals():
    """
    Main function to create the enriched goals table from CSV data.
    
    This function:
    1. Reads and processes the goals and games CSV files
    2. Maps date columns to game days
    3. Creates sequential goal numbering for each game
    4. Handles special cases like forfeits
    5. Outputs a clean, structured goals table
    """
    
    # STEP 1: Load the CSV files
    print("Loading CSV files...")
    goals_df = pd.read_csv('WFL2425_goals_unformatted_updated.csv')
    games_df = pd.read_csv('WFL2425games.csv')
    
    # STEP 2: Data preprocessing
    # Convert Gameday column to numeric, handling any non-numeric values gracefully
    games_df['Gameday'] = pd.to_numeric(games_df['Gameday'], errors='coerce')
    
    # STEP 3: Display data structure for debugging and understanding
    print("Goals CSV columns:", goals_df.columns.tolist())
    print("All game days from games CSV:")
    for _, game in games_df.iterrows():
        if pd.notna(game['Gameday']):
            print(f"GameDay {game['Gameday']}: {game['GameID']} - {game['Date']}")
    
    # STEP 4: Create team abbreviation mapping
    # This maps the short team codes from the goals CSV to full team names
    team_mapping = {
        'n60': 'North 60',           # North 60 team
        'se': 'Sports Experts',       # Sports Experts team
        'dd': 'Double Doubles',       # Double Doubles team
        'rdfc': 'RDFC'               # RDFC team
    }
    
    # STEP 5: Create date column to game day mapping
    # The goals CSV has columns named by dates (23rd, 30th, etc.)
    # We need to map these to actual game day numbers
    column_to_gameday = {
        '23rd': 1,   # October 23, 2024 - GameDay 1
        '30th': 2,   # October 30, 2024 - GameDay 2
        '6th': 3,    # November 6, 2024 - GameDay 3
        '13th': 4,   # November 13, 2024 - GameDay 4
        '20th': 5,   # November 20, 2024 - GameDay 5
        '27th': 6,   # November 27, 2024 - GameDay 6
        '4th': 7,    # December 4, 2024 - GameDay 7
        '11th': 8,   # December 11, 2024 - GameDay 8
        '8th': 9,    # January 8, 2025 - GameDay 9
        '15th': 10,  # January 15, 2025 - GameDay 10
        '22nd': 11,  # January 22, 2025 - GameDay 11
        '29th': 12,  # January 29, 2025 - GameDay 12
        '5th': 13,   # February 5, 2025 - GameDay 13
        '12th': 14,  # February 12, 2025 - GameDay 14
        '19th': 15,  # February 19, 2025 - GameDay 15
        '26th': 16, # February 26, 2025 - Semi-finals (note the space!)
        '5th': 17  # March 5, 2025 - Finals (note the .1 suffix)
    }
    
    # STEP 6: Initialize data structures
    enriched_goals = []           # List to store all goal records
    game_goal_counts = {}         # Dictionary to track goal numbers per game
    
    # STEP 7: Process each player row in the goals data
    print("\nProcessing player goals...")
    for _, player_row in goals_df.iterrows():
        # Extract team abbreviation and player name from the first two columns
        team_abbr = player_row.iloc[0]   # First column: team abbreviation (n60, se, dd, rdfc)
        player_name = player_row.iloc[1] # Second column: player name
        
        # Skip header rows and invalid data
        if pd.isna(team_abbr) or team_abbr in ['Team', 'WFL 24/25', 'total'] or pd.isna(player_name):
            continue
            
        # Get the full team name using our mapping
        team_name = team_mapping.get(team_abbr, team_abbr)
        
        # STEP 8: Process each game day column (columns 2-18 represent different dates)
        for col_idx in range(2, 19):
            col_name = goals_df.columns[col_idx]  # Get the column name (e.g., "23rd", "30th")
            goals_scored_raw = player_row.iloc[col_idx]  # Get the raw value from that column
            
            # Convert the raw value to a number, handling any non-numeric values
            try:
                goals_scored = pd.to_numeric(goals_scored_raw, errors='coerce')
            except:
                goals_scored = 0
            
            # Only process if the player actually scored goals in this game day
            if pd.notna(goals_scored) and goals_scored > 0:
                # Check if this column corresponds to a known game day
                if col_name in column_to_gameday:
                    game_day = column_to_gameday[col_name]
                    
                    # Find all games that occurred on this game day
                    game_day_games = [g for g in games_df.iterrows() 
                                    if pd.notna(g[1]['Gameday']) and g[1]['Gameday'] == game_day]
                    
                    # STEP 9: Process each game for this game day
                    for _, game in game_day_games:
                        # Check if this team actually played in this specific game
                        if team_name in [game['Team1'], game['Team2']]:
                            game_id = game['GameID']
                            
                            # Initialize goal counter for this game if it doesn't exist yet
                            if game_id not in game_goal_counts:
                                game_goal_counts[game_id] = 0
                            
                            # STEP 10: Handle special cases and create goal records
                            # Check if this was a forfeit game
                            if 'forefit' in str(game['Notes']).lower():
                                # For forfeit games, mark goals as "Forfeit goal"
                                for _ in range(int(goals_scored)):
                                    game_goal_counts[game_id] += 1
                                    enriched_goals.append({
                                        'GameID': game_id,
                                        'player_name': 'Forfeit goal',
                                        'team': team_name,
                                        'goal_num': game_goal_counts[game_id]
                                    })
                            else:
                                # For regular games, record the actual player name
                                for _ in range(int(goals_scored)):
                                    game_goal_counts[game_id] += 1
                                    enriched_goals.append({
                                        'GameID': game_id,
                                        'player_name': player_name,
                                        'team': team_name,
                                        'goal_num': game_goal_counts[game_id]
                                    })
    
    # STEP 11: Create the final DataFrame and save results
    print("Creating final table...")
    result_df = pd.DataFrame(enriched_goals)
    
    # Sort by GameID and goal_num for clean, organized output
    result_df = result_df.sort_values(['GameID', 'goal_num'])
    
    # Save to CSV file
    result_df.to_csv('full_enriched_goals_table.csv', index=False)
    
    # STEP 12: Display summary statistics and results
    print(f"\n🎯 Full Enriched Goals Table Created Successfully!")
    print(f"📊 Total goals across all games: {len(result_df)}")
    print(f"🎮 Total games processed: {len(result_df['GameID'].unique())}")
    
    # Show breakdown by game for verification
    print(f"\n📋 Goals breakdown by game:")
    for game_id in sorted(result_df['GameID'].unique()):
        game_goals = result_df[result_df['GameID'] == game_id]
        print(f"  {game_id}: {len(game_goals)} goals")
    
    print(f"\n💾 Full table saved to 'full_enriched_goals_table.csv'")
    
    return result_df

def main():
    """
    Main execution function with error handling.
    """
    try:
        print("🚀 Starting WFL Enriched Goals Table Creation...")
        print("=" * 60)
        
        result = create_full_enriched_goals()
        
        print("\n✅ Script completed successfully!")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"❌ Error: Could not find required CSV file: {e}")
        print("Make sure both 'WFL2425_goals_unformatted_updated.csv' and 'WFL2425games.csv' are in the current directory.")
    except Exception as e:
        print(f"❌ Unexpected error occurred: {e}")
        print("Please check your data files and try again.")

if __name__ == "__main__":
    # This ensures the script only runs when executed directly (not when imported)
    main()
