function log(msg) {
    const el = document.getElementById("log");
    el.textContent += `[${new Date().toLocaleTimeString()}] ${msg}\n`;
    el.scrollTop = el.scrollHeight;
}

function mineBlock() {
    fetch('/mine', { method: 'POST' })
        .then(res => res.json())
        .then(data => log(data.message))
        .then(() => fetchChain())
        .catch(err => log("❌ Error mining: " + err));
}

function syncChain() {
    fetch('/sync', { method: 'POST' })
        .then(res => res.json())
        .then(data => log(data.message || "Synced."))
        .then(() => fetchChain())
        .catch(err => log("❌ Error syncing: " + err));
}

function fetchChain() {
    fetch('/chain')
        .then(res => res.json())
        .then(data => {
            renderChain(data);
        });
}

function renderChain(chainData) {
    const chainContainer = document.getElementById('chain');
    chainContainer.innerHTML = "";  // Clear old blocks

    chainData.forEach(block => {
        const blockHTML = `
        <div class="block">
            <h2>Block #${block.index}</h2>
            <p><strong>Timestamp:</strong> ${block.timestamp}</p>
            <p><strong>Previous Hash:</strong> ${block.previous_hash}</p>
            <p><strong>Hash:</strong> ${block.hash}</p>
            <p><strong>Nonce:</strong> ${block.nonce}</p>
            <p><strong>Difficulty:</strong> ${block.difficulty}</p>
            <p><strong>Data:</strong></p>
            <pre>${block.transactions}</pre>
        </div>`;
        chainContainer.innerHTML += blockHTML;
    });
    chainContainer.scrollTop = chainContainer.scrollHeight;
}

function fetchPeers() {
    fetch('/peers')
        .then(res => res.json())
        .then(data => log("Known peers: " + JSON.stringify(data.peers)));
}

function startSSE() {
    const source = new EventSource('/stream');
    source.onmessage = (e) => {
        msg = e.data;
        log("📥 " + msg);
        if (msg.includes("accepted from node") || msg.includes("added")) {
            fetchChain();  // 🟢 re-fetch the chain from backend
        }
    }
    fetchChain();  // 🟢 fetch the chain on load

}

window.onload = startSSE;
