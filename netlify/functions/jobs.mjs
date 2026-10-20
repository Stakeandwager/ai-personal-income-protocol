import { getUser } from "@netlify/identity";
import { getStore } from "@netlify/blobs";

const json = (data, status = 200) => Response.json(data, { status, headers: { "Cache-Control": "no-store" } });

export default async function handler() {
  const user = await getUser();
  if (!user) return json({ error: "Sign in required" }, 401);
  const store = getStore({ name: "apip-public-job-feed-v1" });
  const feed = await store.get("remotive/jobs.json", { type: "json" });
  if (!feed) return json({ jobs: [], updatedAt: null, source: "Remotive", message: "Waiting for the first scheduled feed refresh." });
  return json({ ...feed, source: "Remotive" });
}

export const config = { path: "/api/jobs", method: "GET" };
