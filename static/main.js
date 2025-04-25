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

// Load saved theme or default to dark
function setDarkTheme() {
    const theme = localStorage.getItem('theme') || 'dark';
    localStorage.setItem('theme', theme);
    document.body.classList.add(theme + '-theme');
    document.getElementById('themeToggle').checked = theme === 'dark';
}

function startSSE() {
    const source = new EventSource('/stream');
    source.onmessage = (e) => {
        msg = e.data;
        log("📥 " + msg);
        if (msg.includes("accepted from node") || msg.includes("mined, saved and broadcasted")) {
            fetchChain();  // 🟢 re-fetch the chain from backend
        }
    }
    fetchChain();  // 🟢 fetch the chain on load
    setDarkTheme();

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

  document.getElementById('transactionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('transactionInput');
    const value = input.value.trim();
  
    if (!value) return;
  
    const res = await fetch('/submit_transaction', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ transaction: value })
    });
  
    const msg = await res.json();
    // alert(msg.message || msg.error);
  
    input.value = '';
    fetchTransactions();
  });
  
  setInterval(fetchTransactions, 3000);
  fetchTransactions();


}

async function fetchTransactions() {
    const res = await fetch('/transactions');
    const data = await res.json();
  
    const pendingList = document.getElementById('pendingTransactions');
    pendingList.innerHTML = '';
  
    if (data.length === 0) {
      pendingList.innerHTML = '<li>No pending transactions.</li>';
      return;
    }
  
    data.forEach(tx => {
      // alert("Transaction: " + tx);
      const li = document.createElement('li');
      li.textContent = tx;
      pendingList.appendChild(li);
    });

  }
  
// Initialize the app
window.onload = startSSE;
