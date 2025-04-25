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

  // Load saved theme or default to dark
  document.addEventListener("DOMContentLoaded", function () {
      const theme = localStorage.getItem('theme') || 'light';
      localStorage.setItem('theme', theme);
      document.body.classList.add(theme + '-theme');
      const toggle = document.getElementById('themeToggle');
      document.getElementById('themeToggle').checked = theme === 'dark';
      // toggle.checked = theme === 'dark';
  });

  // Toggle and save
  document.getElementById('themeToggle').addEventListener('change', function () {
      const body = document.body;
      if (this.checked) {
          body.classList.remove('light-theme');
          body.classList.add('dark-theme');
          localStorage.setItem('theme', 'dark');
      } else {
          body.classList.remove('dark-theme');
          body.classList.add('light-theme');
          localStorage.setItem('theme', 'light');
      }
  });

}

window.onload = startSSE;
