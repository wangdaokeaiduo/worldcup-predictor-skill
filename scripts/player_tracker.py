import json
import os
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "player_db.json")

def load_db():
    if not os.path.exists(DB_PATH):
        return {"players": {}}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def query(teams):
    data = load_db()
    results = {}
    for team in teams:
        team_players = {name: info for name, info in data.get("players", {}).items() if info["team"] == team}
        if team_players:
            results[team] = team_players
    
    if not results:
        print(f"No player data found for teams: {', '.join(teams)}")
        return

    print("=== Player Performance Database (Micro-level Stats) ===")
    for team, players in results.items():
        print(f"\n[{team}] Core Players:")
        for name, info in players.items():
            print(f"  - {name} | Matches: {info['matches_played']} | Goals: {info['goals']} | Assists: {info['assists']} | Stamina: {info['stamina_status']}")
            for ev in info['key_events']:
                print(f"    * {ev}")

def update(player_name, team, goals_added, assists_added, stamina_status, key_event):
    data = load_db()
    if "players" not in data:
        data["players"] = {}
        
    if player_name not in data["players"]:
        data["players"][player_name] = {
            "team": team,
            "goals": 0,
            "assists": 0,
            "matches_played": 0,
            "stamina_status": "Unknown",
            "key_events": []
        }
        
    p = data["players"][player_name]
    p["goals"] += int(goals_added)
    p["assists"] += int(assists_added)
    p["matches_played"] += 1
    p["stamina_status"] = stamina_status
    if key_event and key_event.strip() and key_event != "none":
        p["key_events"].append(key_event)
        
    save_db(data)
    print(f"Successfully updated stats for {player_name} ({team}).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 player_tracker.py query <team1> [team2] ...")
        print("  python3 player_tracker.py update <player_name> <team> <goals> <assists> <stamina> <key_event>")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "query":
        teams = sys.argv[2:]
        if not teams:
            print("Please specify at least one team.")
            sys.exit(1)
        query(teams)
        
    elif command == "update":
        if len(sys.argv) < 8:
            print("Usage: python3 player_tracker.py update <player_name> <team> <goals> <assists> <stamina> <key_event>")
            print("Example: python3 player_tracker.py update 'Vinícius' '巴西' 1 0 'Fatigued after 90m' 'Scored winning goal'")
            sys.exit(1)
            
        player_name = sys.argv[2]
        team = sys.argv[3]
        goals = sys.argv[4]
        assists = sys.argv[5]
        stamina = sys.argv[6]
        event = sys.argv[7]
        
        update(player_name, team, goals, assists, stamina, event)
    else:
        print(f"Unknown command: {command}")
