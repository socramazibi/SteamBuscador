document.getElementById("searchBtn").addEventListener("click", async () => {
    document.getElementById("results").innerHTML = "<p>⏳ Buscando...</p>";
    const res = await fetch("/api/games");
    const data = await res.json();
    let output = "";
    if(data.length === 0){
        output = "<p>❌ No se encontraron juegos.</p>";
    } else {
        data.forEach(game => {
            output += `
            <div class="game">
                <h3>${game.name}</h3>
                <p>👍 ${game.score}% positivas (${game.total_reviews} reseñas)</p>
                <a href="${game.link}" target="_blank">Ver en Steam</a>
            </div>
            `;
        });
    }
    document.getElementById("results").innerHTML = output;
});
