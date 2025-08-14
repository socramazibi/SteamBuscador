import os
import requests
from flask import Flask, render_template, jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

# Descarga el catálogo completo de Steam una vez
STEAM_APP_LIST_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
app_list = requests.get(STEAM_APP_LIST_URL).json()["applist"]["apps"]

# Limitar a los primeros N juegos para demo (puedes subir N luego)
MAX_GAMES = 5000  

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/games")
def get_games():
    min_score = 0.8
    min_reviews = 50
    result = []

    def check_game(game):
        try:
            url = f"https://store.steampowered.com/appreviews/{game['appid']}?json=1&language=all"
            res = requests.get(url, timeout=5).json()
            stats = res.get("query_summary")
            if not stats:
                return None
            total_reviews = stats["total_positive"] + stats["total_negative"]
            score = stats["total_positive"] / total_reviews
            if score >= min_score and total_reviews >= min_reviews:
                return {
                    "name": game["name"],
                    "appid": game["appid"],
                    "score": round(score*100,1),
                    "total_reviews": total_reviews,
                    "link": f"https://store.steampowered.com/app/{game['appid']}"
                }
        except:
            return None

    # Usar ThreadPoolExecutor para hacer varias consultas a la vez
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(check_game, game) for game in app_list[:MAX_GAMES]]
        for future in as_completed(futures):
            game_data = future.result()
            if game_data:
                result.append(game_data)

    # Ordenar por porcentaje de positivas descendente
    result = sorted(result, key=lambda x: x["score"], reverse=True)
    return jsonify(result)
