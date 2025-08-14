import os
from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Lista de juegos de ejemplo (más adelante se puede ampliar con toda la lista Steam)
sample_games = [
    {"name": "Portal 2", "appid": 620},
    {"name": "Hades", "appid": 1145360},
    {"name": "Hollow Knight", "appid": 367520},
    {"name": "Cyberpunk 2077", "appid": 1091500}
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/games")
def get_games():
    min_score = 0.8
    min_reviews = 50
    result = []

    for game in sample_games:
        url = f"https://store.steampowered.com/appreviews/{game['appid']}?json=1&language=all"
        try:
            res = requests.get(url, timeout=10).json()
            stats = res.get("query_summary")
            if not stats:
                continue
            total_reviews = stats["total_positive"] + stats["total_negative"]
            score = stats["total_positive"] / total_reviews
            if score >= min_score and total_reviews >= min_reviews:
                result.append({
                    "name": game["name"],
                    "appid": game["appid"],
                    "score": round(score*100,1),
                    "total_reviews": total_reviews,
                    "link": f"https://store.steampowered.com/app/{game['appid']}"
                })
        except:
            continue
    return jsonify(result)

if __name__ == "__main__":
    # Render asigna el puerto con variable de entorno PORT
    port = int(os.environ.get("PORT", 5000))
    # Debes bindear a 0.0.0.0, no localhost
    app.run(host="0.0.0.0", port=port)
