async function updateLastTime() {
    const res = await fetch("/api/last_update");
    const data = await res.json();
    document.getElementById("lastUpdate").innerText = `Última actualización: ${data.last_updated}`;
}

async function loadGames(page=1) {
    const search = document.getElementById("search").value;
    const minScore = document.getElementById("minScore").value;
    const minReviews = document.getElementById("minReviews").value;

    document.getElementById("results").innerHTML = "<p>⏳ Buscando...</p>";

    const res = await fetch(`/api/games?search=${encodeURIComponent(search)}&min_score=${minScore}&min_reviews=${minReviews}&page=${page}`);
    const data = await res.json();
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "";

    if(data.games.length === 0){
        resultsDiv.innerHTML = "<p>❌ No se encontraron juegos.</p>";
    } else {
        data.games.forEach(g => {
            const div = document.createElement("div");
            div.className = "game";
            div.innerHTML = `
                <img src="${g.header_image}" alt="${g.name}">
                <h3>${g.name}</h3>
                <p>👍 ${g.score}% positivas (${g.total_reviews} reseñas)</p>
                <a href="${g.link}" target="_blank">Ver en Steam</a>
            `;
            resultsDiv.appendChild(div);
        });
    }

    // Paginación
    const paginationDiv = document.getElementById("pagination");
    paginationDiv.innerHTML = "";
    for(let i=1; i<=data.total_pages; i++){
        const btn = document.createElement("button");
        btn.className = "page-btn";
        btn.innerText = i;
        if(i===data.current_page) btn.disabled = true;
        btn.onclick = () => loadGames(i);
        paginationDiv.appendChild(btn);
    }

    updateLastTime();
}

document.getElementById("searchBtn").addEventListener("click", () => loadGames());
window.onload = () => loadGames();
