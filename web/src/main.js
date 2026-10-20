import "./style.css";
import { acceptInvite, getUser, handleAuthCallback, login, logout, onAuthChange } from "@netlify/identity";

const root = document.querySelector("#app");
const state = { user: null, events: [], jobs: [], query: "", tab: "discover", invite: null, busy: false };
const STATUS = ["saved", "qualified", "draft_ready", "proposal_sent_owner", "contract_funded_owner", "delivered_owner", "payment_reported_owner"];
const STATUS_LABEL = { saved: "Saved", qualified: "Qualified", draft_ready: "Draft ready", proposal_sent_owner: "Sent by owner", contract_funded_owner: "Funded contract", delivered_owner: "Delivered", payment_reported_owner: "Payment reported" };
const PROVIDERS = [
  ["upwork-local-bank", "Upwork → local bank", "Platform payout; confirm availability and fees in your own account."],
  ["payoneer-local-bank", "Payoneer → local bank", "Provider account and eligibility are managed by you."],
  ["western-union", "Western Union", "A payer-initiated transfer route; not escrow or a job marketplace."],
  ["other", "Other provider", "Enter setup details only on the provider's secure site."],
];

function esc(value = "") { return String(value); }
function newestByType(type) { return state.events.filter((e) => e.type === type).sort((a, b) => b.createdAt.localeCompare(a.createdAt)); }
function latestStatus(jobId) { return newestByType("pipeline.status").find((e) => e.jobId === jobId)?.status || "saved"; }
function savedJobs() { return newestByType("opportunity.saved").filter((e, i, a) => a.findIndex((x) => x.jobId === e.jobId) === i); }
function money(amount, currency = "USD") { try { return new Intl.NumberFormat(undefined, { style: "currency", currency, maximumFractionDigits: 2 }).format(Number(amount) || 0); } catch { return `${currency} ${amount}`; } }
function toast(text) { const el = document.createElement("div"); el.className = "toast"; el.textContent = text; document.body.append(el); setTimeout(() => el.remove(), 2800); }
function button(label, action, cls = "button") { const b = document.createElement("button"); b.className = cls; b.type = "button"; b.textContent = label; b.addEventListener("click", action); return b; }
function el(tag, cls, text) { const n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; }

async function api(path, options = {}) {
  const response = await fetch(path, { ...options, credentials: "same-origin", headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || `Request failed (${response.status})`);
  return body;
}

async function loadData() {
  const [workspace, jobs] = await Promise.all([api("/api/workspace"), api("/api/jobs")]);
  state.events = workspace.events || [];
  state.jobs = jobs.jobs || [];
  state.sourceUpdated = jobs.updatedAt || "not yet synced";
}

async function addEvent(event) {
  await api("/api/workspace", { method: "POST", body: JSON.stringify(event) });
  await loadData();
  render();
}

function shell() {
  root.replaceChildren();
  const frame = el("main", "shell");
  const top = el("header", "topbar");
  const brand = el("div", "brand");
  brand.append(el("div", "brand-mark", "A"));
  const word = el("div"); word.append(el("div", "brand-name", "APIP"), el("div", "brand-sub", "Income operations")); brand.append(word); top.append(brand);
  if (state.user) {
    const u = el("div", "user-box"); u.append(el("span", "", state.user.email || "Owner"), button("Sign out", async () => { await logout(); state.user = null; render(); }, "button ghost small")); top.append(u);
  }
  frame.append(top);
  root.append(frame);
  return frame;
}

function authView(message = "") {
  const frame = shell();
  const card = el("section", "auth-wrap");
  card.append(el("div", "eyebrow", "Private owner workspace"), el("h1", "Sign in to APIP"), el("p", "auth-help", "This deployment is designed for invited users only. Ask the Netlify site owner to invite your email in Identity settings; APIP never asks for bank details or payment credentials."));
  if (state.invite) {
    const inviteForm = el("form");
    inviteForm.append(el("div", "note", `Complete the invitation for ${state.invite.email || "your account"}. Choose your APIP password.`));
    const password = document.createElement("input"); password.type = "password"; password.className = "field"; password.minLength = 8; password.required = true; password.autocomplete = "new-password"; password.placeholder = "Create password"; inviteForm.append(password);
    const acceptButton = document.createElement("button"); acceptButton.className = "button primary"; acceptButton.type = "submit"; acceptButton.textContent = "Accept invitation"; inviteForm.append(acceptButton);
    inviteForm.addEventListener("submit", async (event) => { event.preventDefault(); const submit = inviteForm.querySelector("button"); submit.disabled = true; try { await acceptInvite(state.invite.token, password.value); state.invite = null; state.user = await getUser(); await ready(); } catch (error) { toast(error.message); submit.disabled = false; } });
    card.append(inviteForm);
  } else {
    const form = el("form");
    const email = document.createElement("input"); email.className = "field"; email.type = "email"; email.required = true; email.autocomplete = "username"; email.placeholder = "Email";
    const password = document.createElement("input"); password.className = "field"; password.type = "password"; password.required = true; password.autocomplete = "current-password"; password.placeholder = "Password";
    const submit = document.createElement("button"); submit.className = "button primary"; submit.textContent = "Sign in";
    form.append(email, password, submit);
    form.addEventListener("submit", async (event) => { event.preventDefault(); submit.disabled = true; try { await login(email.value, password.value); state.user = await getUser(); await ready(); } catch (error) { toast(error.message || "Sign in failed"); submit.disabled = false; } });
    card.append(form);
  }
  if (message) card.append(el("p", "note warning", message));
  frame.append(card, el("p", "footer", "APIP does not hold money, collect bank credentials, or automatically contact buyers."));
}

function createStats() {
  const stats = el("section", "stats");
  const drafts = newestByType("offer.draft").length;
  const funded = savedJobs().filter((lead) => latestStatus(lead.jobId) === "contract_funded_owner").length;
  const receipts = newestByType("payment.reported").filter((e) => e.evidenceType === "provider_reference").length;
  const cards = [["Open opportunities", state.jobs.length, "Remotive source cache"], ["Offers drafted", drafts, "Owner must submit"], ["Funded contracts", funded, "Owner-reported status"], ["Verified receipts", 0, "No payment-provider verification connected"]];
  for (const [label, value, hint] of cards) { const c = el("article", "stat"); c.append(el("div", "stat-label", label), el("div", `stat-value ${label === "Verified receipts" ? "green" : ""}`, String(value)), el("div", "stat-foot", hint)); stats.append(c); }
  return stats;
}

function navTabs() {
  const nav = el("nav", "tabs");
  for (const [key, label] of [["discover", "Discover"], ["pipeline", "Pipeline"], ["contracts", "Offer / contract drafts"], ["payments", "Payment routes"]]) {
    const b = button(label, () => { state.tab = key; render(); }, `tab ${state.tab === key ? "active" : ""}`); nav.append(b);
  }
  return nav;
}

function jobCard(job) {
  const card = el("article", "job-card"); const body = el("div");
  body.append(el("h3", "job-title", job.title || "Untitled role"), el("div", "company", job.company || "Company not listed"));
  const chips = el("div", "job-meta");
  for (const item of [job.category, job.jobType, job.location, job.salary || "Pay not listed", `Posted ${job.published || "date not listed"}`]) if (item) chips.append(el("span", "chip", item));
  body.append(chips);
  body.append(el("p", "job-description", job.summary || "Open the source to review the complete job brief and eligibility before applying."));
  const source = el("div", "source"); source.append(document.createTextNode("Source: "));
  const a = document.createElement("a"); a.href = job.url; a.target = "_blank"; a.rel = "noopener noreferrer"; a.textContent = job.source || "Remotive"; source.append(a); body.append(source);
  const actions = el("div", "job-actions");
  const safeId = String(job.id);
  const wasSaved = savedJobs().some((e) => e.jobId === safeId);
  actions.append(button(wasSaved ? "Saved" : "Save lead", async () => {
    if (wasSaved) { state.tab = "pipeline"; render(); return; }
    try { await addEvent({ type: "opportunity.saved", jobId: safeId, title: job.title, company: job.company, url: job.url, source: job.source, budget: job.salary || "Not listed", location: job.location || "Not listed", evidenceNote: "Imported from current source feed; owner must verify listing status and eligibility." }); toast("Lead saved"); } catch (error) { toast(error.message); }
  }, `button small ${wasSaved ? "ghost" : "primary"}`));
  const link = document.createElement("a"); link.href = job.url; link.target = "_blank"; link.rel = "noopener noreferrer"; link.className = "button ghost small"; link.textContent = "Review source ↗"; actions.append(link);
  card.append(body, actions); return card;
}

function discoverView(main) {
  const intro = el("section", "panel"); intro.append(el("div", "eyebrow", "Public-source job discovery"), el("h2", "Find work APIP can help you deliver"), el("p", "This source is Remotive’s public remote-jobs API. Listings are delayed by up to 24 hours, may restrict candidate locations, and must be reviewed at source. APIP does not auto-apply or scrape private pages."));
  intro.append(el("div", "note", `Last feed sync: ${state.sourceUpdated || "not yet synced"}. Scheduled refresh is configured for up to four runs daily (UTC) after Netlify deployment. Each listing links back to Remotive.`));
  const toolbar = el("div", "toolbar"); const search = document.createElement("input"); search.className = "field"; search.placeholder = "Filter titles, skills, company, or location"; search.value = state.query; search.addEventListener("input", () => { state.query = search.value; list.replaceChildren(...filtered().map(jobCard)); }); toolbar.append(search);
  const list = el("div", "job-list");
  function filtered() { const q = state.query.toLowerCase().trim(); return state.jobs.filter((j) => !q || [j.title, j.company, j.location, j.category, j.summary].join(" ").toLowerCase().includes(q)); }
  list.append(...filtered().map(jobCard));
  if (!state.jobs.length) list.append(el("div", "empty", "No feed has been synced yet. The first scheduled Netlify refresh will import the source feed. Until then, add a lead from a public listing using the manual lead form in Pipeline."));
  intro.append(toolbar, list); main.append(intro);
}

function pipelineView(main) {
  const section = el("section", "panel"); section.append(el("div", "eyebrow", "Evidence-led workflow"), el("h2", "Your opportunity pipeline"), el("p", "Status moves are owner-recorded. A proposal is not a contract; a contract amount is not revenue; a payout claim is not a verified receipt."));
  const form = document.createElement("form"); form.className = "panel nested-panel";
  form.append(el("h3", "job-title", "Add a public lead"));
  const grid = el("div", "form-grid");
  const title = document.createElement("input"); title.className = "field"; title.required = true; title.maxLength = 180; title.placeholder = "Job / opportunity title";
  const url = document.createElement("input"); url.className = "field"; url.type = "url"; url.required = true; url.placeholder = "https:// source listing URL";
  const company = document.createElement("input"); company.className = "field"; company.maxLength = 120; company.placeholder = "Company or marketplace";
  grid.append(fieldWrap("Title", title), fieldWrap("Source link", url), fieldWrap("Source / marketplace", company)); form.append(grid);
  const submit = document.createElement("button"); submit.className = "button primary"; submit.textContent = "Save lead"; form.append(submit);
  form.addEventListener("submit", async (event) => { event.preventDefault(); try { const id = `manual-${crypto.randomUUID()}`; await addEvent({ type: "opportunity.saved", jobId: id, title: title.value.trim(), company: company.value.trim() || "Not listed", url: url.value.trim(), source: company.value.trim() || new URL(url.value).hostname, evidenceNote: "Manually added by owner; status and budget not yet verified." }); toast("Lead saved"); form.reset(); } catch (error) { toast(error.message); } }); section.append(form);
  const list = el("div", "contract-list");
  for (const lead of savedJobs()) {
    const card = el("article", "contract-card"); const left = el("div"); left.append(el("div", "contract-name", lead.title), el("div", "contract-meta", `${lead.company || "Source unknown"} · ${STATUS_LABEL[latestStatus(lead.jobId)] || "Saved"} · ${lead.budget || "Budget unknown"}`));
    const right = el("div", "route-state"); const select = document.createElement("select"); select.className = "select small";
    for (const st of STATUS) { const o = document.createElement("option"); o.value = st; o.textContent = STATUS_LABEL[st]; o.selected = st === latestStatus(lead.jobId); select.append(o); }
    select.addEventListener("change", async () => { try { await addEvent({ type: "pipeline.status", jobId: lead.jobId, status: select.value }); toast("Status recorded as owner-supplied"); } catch (error) { toast(error.message); } });
    const a = document.createElement("a"); a.href = lead.url; a.target = "_blank"; a.rel = "noopener noreferrer"; a.className = "button ghost small"; a.textContent = "Source ↗";
    right.append(select, a); card.append(left, right); list.append(card);
  }
  if (!savedJobs().length) list.append(el("div", "empty", "Save a lead from Discover or add its public source link above.")); section.append(list); main.append(section);
}

function fieldWrap(labelText, input) { const w = el("div", "form-field"); const label = el("label", "", labelText); if (!input.id) input.id = `field-${crypto.randomUUID()}`; label.htmlFor = input.id; w.append(label, input); return w; }

function contractsView(main) {
  const panel = el("section", "panel"); panel.append(el("div", "eyebrow", "Owner-reviewed only"), el("h2", "Offer and contract drafts"), el("p", "Create a plain-language draft with scope, price, timing, and payment terms. APIP cannot send, sign, accept, or enforce a contract. Have the actual client approve the final terms through their marketplace or payment provider."));
  const warning = el("div", "note warning", "Do not put bank numbers, account credentials, private client data, or legal identity documents here. Saved drafts are private to your authenticated APIP account. A draft is not a signed agreement."); panel.append(warning);
  const form = document.createElement("form"); form.className = "panel nested-panel"; form.append(el("h3", "job-title", "New service offer draft"));
  const grid = el("div", "form-grid");
  const lead = document.createElement("select"); lead.className = "select"; const unlinked = document.createElement("option"); unlinked.value = ""; unlinked.textContent = "Unlinked draft"; lead.append(unlinked);
  for (const saved of savedJobs()) { const option = document.createElement("option"); option.value = saved.jobId; option.textContent = `${saved.title} — ${saved.company || "source unknown"}`; lead.append(option); }
  const title = document.createElement("input"); title.className = "field"; title.required = true; title.maxLength = 160; title.placeholder = "Offer title";
  const price = document.createElement("input"); price.className = "field"; price.type = "number"; price.min = "0"; price.step = "0.01"; price.required = true; price.placeholder = "Price";
  const currency = document.createElement("select"); currency.className = "select"; for (const c of ["USD", "NGN", "GBP", "EUR"]) { const o = document.createElement("option"); o.value = c; o.textContent = c; currency.append(o); }
  const deadline = document.createElement("input"); deadline.className = "field"; deadline.type = "text"; deadline.maxLength = 80; deadline.placeholder = "Delivery estimate (e.g. 24 hours)";
  const scope = document.createElement("textarea"); scope.maxLength = 2000; scope.required = true; scope.placeholder = "Deliverable, limits, revision count, client inputs required";
  const payment = document.createElement("textarea"); payment.maxLength = 1000; payment.placeholder = "Payment milestone / provider terms (no private account details)";
  grid.append(fieldWrap("Related opportunity", lead), fieldWrap("Offer name", title), fieldWrap("Proposed price", price), fieldWrap("Currency", currency), fieldWrap("Delivery estimate", deadline), fieldWrap("Scope and exclusions", scope), fieldWrap("Payment terms draft", payment)); form.append(grid);
  const actions = el("div", "form-actions"); const submit = document.createElement("button"); submit.className = "button primary"; submit.textContent = "Save draft only"; actions.append(submit, el("span", "draft-banner", "NOT SENT · NOT SIGNED")); form.append(actions);
  form.addEventListener("submit", async (event) => { event.preventDefault(); try { await addEvent({ type: "offer.draft", jobId: lead.value, title: title.value.trim(), price: Number(price.value), currency: currency.value, delivery: deadline.value.trim(), scope: scope.value.trim(), paymentTerms: payment.value.trim() }); form.reset(); toast("Draft saved; nothing was sent"); } catch (error) { toast(error.message); } }); panel.append(form);
  const list = el("div", "contract-list");
  for (const draft of newestByType("offer.draft")) { const card = el("article", "contract-card"); const left = el("div"); left.append(el("div", "contract-name", draft.title), el("div", "contract-meta", `${money(draft.price, draft.currency)} · ${draft.delivery || "Delivery TBD"} · Draft only`), el("div", "smallprint", draft.scope)); const tag = el("span", "draft-banner", "NOT SENT"); card.append(left, tag); list.append(card); }
  if (!newestByType("offer.draft").length) list.append(el("div", "empty", "No offer drafts yet.")); panel.append(list); main.append(panel);
}

function paymentsView(main) {
  const panel = el("section", "panel"); panel.append(el("div", "eyebrow", "You control your payout accounts"), el("h2", "Payment routes and receipt evidence"), el("p", "APIP does not open accounts, hold balances, or transfer money. Choose a route you personally configure with the provider. This screen stores only the provider name and your setup checkbox—never account or card numbers."));
  panel.append(el("div", "note", "To receive marketplace earnings, connect a payout method inside that marketplace. Direct-to-local-bank, Payoneer, or Western Union availability varies by country, provider, client, and transaction purpose. Confirm settlement in your own bank/provider before calling income verified."));
  const routes = el("div", "route-list"); const existing = newestByType("payment.route");
  for (const [id, name, desc] of PROVIDERS) {
    const route = existing.find((e) => e.providerId === id); const row = el("article", "route-card"); const left = el("div"); left.append(el("div", "route-name", name), el("div", "route-desc", desc));
    const right = el("div", "route-state"); const label = el("label", ""); const check = document.createElement("input"); check.type = "checkbox"; check.checked = Boolean(route?.ownerMarkedConfigured); check.addEventListener("change", async () => { try { await addEvent({ type: "payment.route", providerId: id, ownerMarkedConfigured: check.checked }); toast("Provider setup status saved"); } catch (error) { check.checked = !check.checked; toast(error.message); } }); label.append(check, document.createTextNode(" I set this up")); right.append(label); row.append(left, right); routes.append(row);
  }
  panel.append(routes);
  const form = document.createElement("form"); form.className = "panel nested-panel"; form.append(el("h3", "job-title", "Record a payment report"), el("p", "smallprint", "This records your report only. APIP will continue to show verified receipts as zero until a secure provider/bank verification integration exists."));
  const grid = el("div", "receipt-row"); const amount = document.createElement("input"); amount.className = "field"; amount.type = "number"; amount.min = "0.01"; amount.step = "0.01"; amount.required = true; amount.placeholder = "Amount";
  const currency = document.createElement("select"); currency.className = "select"; for (const c of ["NGN", "USD", "GBP", "EUR"]) { const o = document.createElement("option"); o.value = c; o.textContent = c; currency.append(o); }
  const source = document.createElement("input"); source.className = "field"; source.maxLength = 100; source.required = true; source.placeholder = "Payer/provider name";
  const submit = document.createElement("button"); submit.className = "button primary"; submit.textContent = "Record owner report"; grid.append(amount, currency, source, submit); form.append(grid);
  form.addEventListener("submit", async (event) => { event.preventDefault(); try { await addEvent({ type: "payment.reported", amount: Number(amount.value), currency: currency.value, payer: source.value.trim(), evidenceType: "owner_report_unverified" }); form.reset(); toast("Saved as unverified owner report"); } catch (error) { toast(error.message); } }); panel.append(form);
  for (const receipt of newestByType("payment.reported")) { const row = el("article", "route-card"); row.append(el("div", "route-name", `${money(receipt.amount, receipt.currency)} · ${receipt.payer}`), el("span", "draft-banner", "OWNER REPORTED · NOT VERIFIED")); panel.append(row); }
  main.append(panel);
}

function render() {
  if (!state.user) { authView(); return; }
  const frame = shell();
  const hero = el("section", "hero"); const text = el("div"); text.append(el("div", "eyebrow", "Evidence first · owner in control"), el("h1", "Turn opportunities into receipts."), el("p", "APIP finds public leads, tracks your next move, drafts offers and contract terms, and keeps payment claims separate from verified money received."));
  hero.append(text, el("div", "live-status", "●  PRIVATE WORKSPACE · NO AUTO-SUBMISSIONS")); frame.append(hero, createStats());
  frame.append(el("div", "note warning", "Current stage: prototype. Job feed is limited to a permitted public API; marketplace accounts, offer submission, signatures, and money movement are not connected. A listing or draft is not income."));
  frame.append(navTabs()); const main = el("div");
  if (state.tab === "discover") discoverView(main); else if (state.tab === "pipeline") pipelineView(main); else if (state.tab === "contracts") contractsView(main); else paymentsView(main);
  frame.append(main, el("p", "footer", `Private APIP owner app · source sync ${state.sourceUpdated || "not yet run"} · payment verification not connected · signed in as ${state.user.email || "owner"}`));
}

async function ready() {
  render();
  try { await loadData(); render(); }
  catch (error) { authView(`Workspace load failed: ${error.message}`); }
}

async function boot() {
  try {
    const result = await handleAuthCallback();
    if (result?.type === "invite" && result.token) { state.invite = { token: result.token, email: result.user?.email }; authView(); return; }
    state.user = await getUser();
    onAuthChange(async (_event, user) => { state.user = user; if (user) await ready(); else render(); });
    if (state.user) await ready(); else authView();
  } catch (error) { authView(error.message || "Netlify Identity is not configured yet. Enable it for the site and use an invited owner account."); }
}

boot();
