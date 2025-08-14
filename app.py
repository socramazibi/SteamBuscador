import os
import json
import datetime
import requests
import threading
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

CACHE_FILE = "steam_cache.json"
STEAM_APP_LIST_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"

# Función para actualizar caché
def update_cache(max_games=5000):
    print("Actualizando caché de Steam...")
    try:
        app_list = requests.get(STEAM_APP_LIST_URL).json()["applist"]["apps"][:max_games]
        cached_games = []

        for game in app_list:
            try:
                url = f"https://store.steampowered.com/appreviews/{game['appid']}?json=1&language=all"
                res = requests.get(url, timeout=5).json()
                stats = res.get("query_summary")
                if not stats:
                    continue
                total_reviews = stats["total_positive"] + stats["total_negative"]
                if total_reviews == 0:
                    continue
                score = stats["total_positive"] / total_reviews
                cached_games.append({
                    "name": game["name"],
                    "appid": game["appid"],
                    "score": round(score*100,1),
                    "total_reviews": total_reviews,
                    "link": f"https://store.steampowered.com/app/{game['appid']}",
                    "header_image": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{game['appid']}/header.jpg"
                })
            except:
                continue

        data = {
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "games": cached_games
        }

        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)
        print("Caché actualizada.")
    except Exception as e:
        print("Error al actualizar caché:", e)

# Ejecutar actualización en segundo plano
def update_cache_background():
    thread = threading.Thread(target=update_cache)
    thread.start()

# Actualizar caché al iniciar si no existe
if not os.path.exists(CACHE_FILE):
    update_cache_background()

# Rutas
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/games")
def get_games():
    min_score = float(request.args.get("min_score", 80)) / 100
    min_reviews = int(request.args.get("min_reviews", 50))
    search_text = request.args.get("search", "").lower()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    with open(CACHE_FILE) as f:
        data = json.load(f)
    games = data["games"]

    # Filtrado
    filtered = []
    for g in games:
        if g["score"]/100 < min_score or g["total_reviews"] < min_reviews:
            continue
        if search_text and search_text not in g["name"].lower():
            continue
        filtered.append(g)

    # Ordenar por score descendente
    filtered.sort(key=lambda x: x["score"], reverse=True)

    # Paginación
    total_pages = (len(filtered) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated = filtered[start:end]

    return jsonify({
        "games": paginated,
        "total_pages": total_pages,
        "current_page": page
    })

@app.route("/api/last_update")
def last_update():
    with open(CACHE_FILE) as f:
        data = json.load(f)
    return jsonify({"last_updated": data.get("last_updated", "Desconocido")})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
