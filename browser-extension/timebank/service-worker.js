// If a browser restart finds an active timer, its actual stop time is unknown.
// Mark it interrupted; it is excluded from reward calculations.
chrome.runtime.onStartup.addListener(async () => {
  const data = await chrome.storage.local.get(["activeSession", "history"]);
  if (!data.activeSession) return;
  const history = Array.isArray(data.history) ? data.history : [];
  history.unshift({ id: data.activeSession.id, activity: data.activeSession.activity,
    startedAt: data.activeSession.startedAt, stoppedAt: new Date().toISOString(),
    durationSeconds: null, status: "INTERRUPTED", eligibleForRewards: false,
    note: "Browser restarted during session; duration unknown and excluded from rewards." });
  await chrome.storage.local.set({ history: history.slice(0, 1000), activeSession: null });
});
