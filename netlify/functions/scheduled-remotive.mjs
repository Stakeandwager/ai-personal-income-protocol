import { getStore } from "@netlify/blobs";

const SOURCE = "https://remotive.com/api/remote-jobs?limit=300";
const DESCRIPTION_MAX = 5000;

function stripHtml(value = "") {
  return String(value).replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<[^>]+>/g, " ").replace(/&nbsp;/gi, " ").replace(/&amp;/gi, "&").replace(/&lt;/gi, "<").replace(/&gt;/gi, ">").replace(/&#39;|&apos;/gi, "'").replace(/&quot;/gi, '"').replace(/\s+/g, " ").trim().slice(0, DESCRIPTION_MAX);
}

export default async function handler() {
  const response = await fetch(SOURCE, { headers: { "User-Agent": "APIP-income-radar/0.1 (+https://remotive.com/api/remote-jobs)" }, signal: AbortSignal.timeout(12000) });
  if (!response.ok) throw new Error(`Remotive returned HTTP ${response.status}`);
  const payload = await response.json();
  if (!Array.isArray(payload.jobs)) throw new Error("Remotive response had no jobs array");
  const jobs = payload.jobs.slice(0, 300).map((job) => ({
    id: `remotive-${String(job.id)}`,
    title: String(job.title || "").slice(0, 180),
    company: String(job.company_name || "Not listed").slice(0, 150),
    category: String(job.category || "").slice(0, 80),
    jobType: String(job.job_type || "").slice(0, 60),
    location: String(job.candidate_required_location || "Not listed").slice(0, 160),
    salary: String(job.salary || "Not listed").slice(0, 100),
    published: String(job.publication_date || "").slice(0, 40),
    url: String(job.url || ""),
    summary: stripHtml(job.description || ""),
    source: "Remotive",
    sourceNote: "Remotive public API; postings may be delayed by 24 hours. Verify eligibility and status at source.",
  })).filter((job) => /^https:\/\/remotive\.com\//.test(job.url));
  const feed = { jobs, updatedAt: new Date().toISOString(), sourceUrl: "https://remotive.com/api/remote-jobs", source: "Remotive", sourceDelay: "Listings may be delayed by 24 hours", count: jobs.length };
  const store = getStore({ name: "apip-public-job-feed-v1" });
  await store.setJSON("remotive/jobs.json", feed);
  console.log(JSON.stringify({ event: "feed_refresh_complete", source: "Remotive", count: jobs.length, at: feed.updatedAt }));
}

export const config = { schedule: "0 */6 * * *" };
