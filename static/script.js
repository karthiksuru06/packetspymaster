let eventSource;
const logDiv = document.getElementById("log");
const startForm = document.getElementById("startForm");
const stopBtn = document.getElementById("stopBtn");
const autoscroll = document.getElementById("autoscroll");

startForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(startForm);
  await fetch("/start", { method: "POST", body: formData });
  startStreaming();
});

stopBtn.addEventListener("click", async () => {
  if (eventSource) eventSource.close();
  await fetch("/stop", { method: "POST" });
});

function startStreaming() {
  logDiv.innerHTML = "";
  eventSource = new EventSource("/stream");
  eventSource.onmessage = (event) => {
    const packet = JSON.parse(event.data);
    const entry = `[${packet.timestamp}] [${packet.protocol}] ${packet.src} → ${packet.dst} ${packet.info}`;
    const p = document.createElement("div");
    p.textContent = entry;
    logDiv.appendChild(p);
    if (autoscroll.checked) logDiv.scrollTop = logDiv.scrollHeight;
  };
}

function download(format) {
  window.location.href = `/download/${format}`;
}

function clearLogs() {
  fetch('/clear', { method: 'POST' })
    .then(response => {
      if (!response.ok) throw new Error("Failed to clear logs");
      logDiv.innerHTML = ""; // Clear UI
      console.log("🧹 Logs cleared successfully");
    })
    .catch(err => console.error("❌ Clear failed:", err));
}
