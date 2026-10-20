import { randomUUID } from "node:crypto";
import { getUser, verifyRequestOrigin } from "@netlify/identity";
import { getStore } from "@netlify/blobs";

const json = (data, status = 200) => Response.json(data, { status, headers: { "Cache-Control": "no-store" } });
const EVENT_TYPES = new Set(["opportunity.saved", "pipeline.status", "offer.draft", "contract.status", "payment.route", "payment.reported"]);
const PIPELINE = new Set(["saved", "qualified", "draft_ready", "proposal_sent_owner", "contract_funded_owner", "delivered_owner", "payment_reported_owner"]);
const PAYMENT_STATUS = new Set(["funded_owner", "completed_owner", "cancelled_owner"]);
const PROVIDERS = new Set(["upwork-local-bank", "payoneer-local-bank", "western-union", "other"]);
const MAX_BODY = 12_000;
const PRIVATE_KEYS = /(?:account(?:number|_number)?|iban|routing|swift|card(?:number|_number)?|cvv|pin|otp|password|secret|token|api[_-]?key)/i;
const PRIVATE_VALUE = /(?:\bpassword\b\s*[:=]|\bpin\b\s*[:=]|\botp\b\s*[:=]|\b(?:bank\s+)?account\s+(?:number|no\.?|#)\s*[:=]?\s*\d|\b(?:api[_ -]?key|secret)\b\s*[:=])/i;

function validateFields(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("Expected a JSON object");
  for (const key of Object.keys(value)) if (PRIVATE_KEYS.test(key)) throw new Error("Do not send bank numbers, credentials, PINs, OTPs, or API keys to APIP");
  for (const item of Object.values(value)) if (typeof item === "string" && PRIVATE_VALUE.test(item)) throw new Error("Remove sensitive payment or login details before saving this record");
}

function safeText(value, max = 2000) {
  return typeof value === "string" ? value.replace(/[\u0000-\u001f\u007f]/g, " ").trim().slice(0, max) : "";
}

function normalizeEvent(input, ownerId) {
  validateFields(input);
  if (!EVENT_TYPES.has(input.type)) throw new Error("Unsupported event type");
  const common = { id: randomUUID(), ownerId, type: input.type, createdAt: new Date().toISOString() };
  if (input.type === "opportunity.saved") {
    const url = safeText(input.url, 500);
    if (!/^https:\/\//i.test(url)) throw new Error("A public HTTPS source URL is required");
    const jobId = safeText(input.jobId, 120);
    const title = safeText(input.title, 180);
    if (!jobId || !title) throw new Error("Lead ID and title are required");
    return { ...common, jobId, title, company: safeText(input.company, 150), url, source: safeText(input.source, 80), budget: safeText(input.budget, 120), location: safeText(input.location, 160), evidenceNote: safeText(input.evidenceNote, 400) };
  }
  if (input.type === "pipeline.status") {
    if (!PIPELINE.has(input.status)) throw new Error("Unsupported pipeline status");
    return { ...common, jobId: safeText(input.jobId, 120), status: input.status, statusBasis: "owner-reported" };
  }
  if (input.type === "offer.draft") {
    const price = Number(input.price);
    if (!Number.isFinite(price) || price < 0 || price > 1000000000) throw new Error("Price is invalid");
    if (!/^(USD|NGN|GBP|EUR)$/.test(input.currency)) throw new Error("Unsupported currency");
    return { ...common, jobId: safeText(input.jobId, 120), title: safeText(input.title, 160), price, currency: input.currency, delivery: safeText(input.delivery, 80), scope: safeText(input.scope, 2000), paymentTerms: safeText(input.paymentTerms, 800), status: "draft_only" };
  }
  if (input.type === "contract.status") {
    if (!PAYMENT_STATUS.has(input.status)) throw new Error("Unsupported contract status");
    return { ...common, offerId: safeText(input.offerId, 120), status: input.status, statusBasis: "owner-reported" };
  }
  if (input.type === "payment.route") {
    if (!PROVIDERS.has(input.providerId)) throw new Error("Unknown provider route");
    return { ...common, providerId: input.providerId, ownerMarkedConfigured: input.ownerMarkedConfigured === true, statusBasis: "owner-reported" };
  }
  const amount = Number(input.amount);
  if (!Number.isFinite(amount) || amount <= 0 || amount > 1000000000) throw new Error("Amount is invalid");
  if (!/^(USD|NGN|GBP|EUR)$/.test(input.currency)) throw new Error("Unsupported currency");
  return { ...common, amount, currency: input.currency, payer: safeText(input.payer, 100), evidenceType: "owner_report_unverified", status: "not_verified" };
}

export default async function handler(request) {
  const user = await getUser();
  if (!user?.id) return json({ error: "Sign in required" }, 401);
  const store = getStore({ name: "apip-owner-workspace-v1", consistency: "strong" });
  const prefix = `users/${user.id}/events/`;

  if (request.method === "GET") {
    const { blobs } = await store.list({ prefix });
    const events = await Promise.all(blobs.map(async ({ key }) => store.get(key, { type: "json", consistency: "strong" })));
    return json({ events: events.filter(Boolean).sort((a, b) => a.createdAt.localeCompare(b.createdAt)).slice(-500) });
  }
  if (request.method !== "POST") return json({ error: "Method not allowed" }, 405);
  try { verifyRequestOrigin(request); }
  catch { return json({ error: "Request origin rejected" }, 403); }
  const raw = await request.text();
  if (raw.length > MAX_BODY) return json({ error: "Request too large" }, 413);
  let input;
  try { input = JSON.parse(raw); } catch { return json({ error: "Invalid JSON" }, 400); }
  let event;
  try { event = normalizeEvent(input, user.id); }
  catch (error) { return json({ error: error.message }, 400); }
  await store.setJSON(`${prefix}${event.id}.json`, event);
  return json({ event }, 201);
}

export const config = { path: "/api/workspace", method: ["GET", "POST"] };
