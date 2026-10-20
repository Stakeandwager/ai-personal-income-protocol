# APIP Netlify owner app v0.1

## Product milestone

This is the first hosted-app build target for APIP: private owner workspace; current jobs imported from a permitted public API; sourced leads and owner-recorded pipeline; offer/contract drafts; payout-route setup markers; and owner-reported payments kept distinct from verified receipts.

It is an early personal prototype, not a validated product and not an autonomous job-application, contract-signing, escrow, or payment app. No buyer account is connected. Never describe draft amounts as revenue.

## Netlify setup

1. Connect this GitHub repository to a new Netlify site and use the repository root as the base directory. Netlify reads `netlify.toml`: `npm run build`, `dist`, and `netlify/functions`.
2. Enable Netlify Identity on the site. Set registration to **invite only**. Invite only the account owner and people who should be able to access this workspace. Do not enable open signup.
3. Publish a deploy preview first. Confirm the invite/login callback works on the preview URL. `@netlify/identity` login callbacks and server verification require a deployed Netlify Identity site; `netlify dev` cannot prove these flows.
4. Only then promote a deployment. Netlify Blobs provisions from Functions at runtime; it stores the public job feed and per-Identity-user event records separately from Git.
5. To receive money, configure the payout account in the chosen marketplace/payment provider. APIP only stores a provider ID and a user-marked setup checkbox; it does not store account numbers, bank credentials, PINs, OTPs, or API keys.

## Opportunity source

The scheduled function requests the Remotive public job API every six hours (four executions per day, UTC), capped at 300 listings per refresh. Remotive says listings may be delayed 24 hours, requires attribution and a link back, advises no more than four requests a day, and prohibits using the feed to populate third-party job sites or capture signups. APIP uses the feed only inside the authenticated owner workspace and links each result to its Remotive listing. This is an allowlisted API integration, not unrestricted web crawling. It does not access Upwork or private pages.

At deployment, scheduled execution is **configured but unverified** until a successful Netlify function run writes the feed and the signed-in owner sees its timestamp.

## Approval boundaries

- Search and save source links: automatic, read-only.
- Mark lead stages, save an offer draft, and mark a payout route: authenticated owner record only.
- Submit a job application, contact a buyer, publish an offer, sign/accept a contract, make a purchase, or move money: not implemented. Each requires the proper official provider integration and an explicit owner-reviewed action.
- Payment reports entered in the dashboard are labelled **owner reported / not verified**. Verified-receipt count remains zero until an authorized payment-provider or bank evidence integration is built and independently checked.

## Current blockers

- This Codex session has no Netlify site deployment connector or authenticated Netlify control-plane access. The app has not been deployed; this repository contains no Netlify site ID, deploy token, provider OAuth, or payment account credential.
- The owner must connect the Git repository to Netlify, enable invite-only Identity, and invite the owner account. This is dashboard configuration; it cannot be completed by adding a repo token or pretending a production URL exists.
- Actual job applications and cross-platform outreach need an approved marketplace API or a supported user-controlled workflow. This build does not scrape login-protected sites or submit applications.
- Payment providers have distinct onboarding, country eligibility, fees, settlement delays, and compliance requirements. APIP does not control those.

## Verification

After dependencies are installed, run `npm run check` and `npm run build`. Then deploy a preview and test login, API access from an authenticated user, cross-user isolation, scheduled feed retrieval, event recording, and sign-out. Do not use real credentials in automated tests. No Netlify preview exists until a Netlify account owner connects and deploys the repository.
