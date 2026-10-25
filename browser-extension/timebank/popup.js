const $ = (id) => document.getElementById(id);
let current = null;
let historyRows = [];
const fmt = (seconds) => {
  if (!Number.isFinite(seconds) || seconds < 0) return "Duration unknown";
  const s = Math.floor(seconds), h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), r = s % 60;
  return [h,m,r].map(n => String(n).padStart(2,"0")).join(":");
};
const elapsed = (session) => Math.max(0, (Date.now() - Date.parse(session.startedAt)) / 1000);
async function refresh() {
  const data = await chrome.storage.local.get(["activeSession", "history"]);
  current = data.activeSession || null; historyRows = Array.isArray(data.history) ? data.history : [];
  $("start").disabled = Boolean(current); $("stop").disabled = !current;
  $("activity").disabled = Boolean(current); $("consent").disabled = Boolean(current);
  $("timer").textContent = current ? fmt(elapsed(current)) : "00:00:00";
  $("state").textContent = current ? "Session active: " + current.activity : "No active session";
  $("count").textContent = historyRows.length + " record" + (historyRows.length === 1 ? "" : "s");
  renderHistory();
}
function renderHistory() {
  const list = $("history"); list.replaceChildren();
  for (const row of historyRows.slice(0, 30)) {
    const li = document.createElement("li"), title = document.createElement("strong"), meta = document.createElement("div");
    title.textContent = row.activity || "Activity"; meta.className = "muted";
    meta.textContent = row.status + " · " + (row.durationSeconds == null ? "Duration unknown" : fmt(row.durationSeconds)) + " · " + (row.startedAt || "");
    li.append(title, meta); list.append(li);
  }
}
$("start").addEventListener("click", async () => {
  const activity = $("activity").value.trim();
  if (!activity || !$("consent").checked) { $("state").textContent = "Enter an activity and approve local recording first."; return; }
  const session = { id: crypto.randomUUID(), activity, startedAt: new Date().toISOString(), consented: true };
  await chrome.storage.local.set({ activeSession: session }); await refresh();
});
$("stop").addEventListener("click", async () => {
  if (!current) return;
  const row = { id: current.id, activity: current.activity, startedAt: current.startedAt, stoppedAt: new Date().toISOString(), durationSeconds: Math.floor(elapsed(current)), status: "RECORDED_UNVERIFIED", eligibleForRewards: false, note: "Elapsed time only; not evidence of attention or payable earnings." };
  historyRows.unshift(row); await chrome.storage.local.set({ history: historyRows.slice(0, 1000), activeSession: null }); await refresh();
});
$("export").addEventListener("click", async () => {
  const data = await chrome.storage.local.get(["history"]), rows = Array.isArray(data.history) ? data.history : [];
  const cols = ["id","activity","startedAt","stoppedAt","durationSeconds","status","eligibleForRewards","note"];
  const esc = (v) => "\"" + String(v == null ? "" : v).replace(/\"/g, "\"\"") + "\"";
  const csv = [cols.join(","), ...rows.map(row => cols.map(k => esc(row[k])).join(","))].join("\r\n");
  const url = URL.createObjectURL(new Blob([csv], {type:"text/csv;charset=utf-8"}));
  const a = document.createElement("a"); a.href = url; a.download = "apip-timebank-history.csv"; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
$("delete").addEventListener("click", async () => {
  if (!confirm("Delete all saved TimeBank history and any active session from this browser? This cannot be undone.")) return;
  await chrome.storage.local.remove(["history", "activeSession"]); $("activity").value = ""; $("consent").checked = false; await refresh();
});
refresh();
setInterval(() => { if (current) $("timer").textContent = fmt(elapsed(current)); }, 1000);
