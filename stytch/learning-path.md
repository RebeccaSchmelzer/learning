# Stytch in one hour

**Goal:** explain where Stytch fits, trace a login through its API, and integrate a consumer email magic-link flow in a small TypeScript/Node app. Set a 60-minute timer. Start with [Exercise 1](exercises.md), then open the notes as you go.

## Topic type

- **Primary:** external API/platform. Stytch runs identity services; the Node library is an SDK for its API.
- **Secondary:** specific library/framework and security concept. You need to learn SDK calls and trust boundaries together.

## Learning depth

**Target:** practical usage with a first step toward professional fluency. By the end, you should be able to choose a Stytch product, send and redeem a magic link, verify a session before serving a protected route, locate the corresponding raw HTTP endpoint, and explain two common failure cases. One hour is not enough for production mastery.

## Curriculum emphasis

- 15 minutes: product choice and login mental model
- 15 minutes: official API and SDK reading
- 25 minutes: run, trace, and change the example
- 5 minutes: retrieval and next integration decision

**Defer:** SSO/SCIM, advanced RBAC, fraud tooling, WebAuthn, OAuth provider configuration, and production deployment. Read those only when your application needs them.

## What Stytch does best

Stytch provides authentication and session infrastructure through APIs and SDKs. Its **Consumer** product centers on individual users and supports methods such as magic links, passcodes, OAuth, passwords, and WebAuthn. Its **B2B** product centers on organizations and members, with organization settings, SSO, and role-based access. For this hour, use **Consumer** so the core request flow stays small. If your real app sells to companies with separate tenants, start from B2B instead; its data model and SDK client differ. [Node SDK overview](https://github.com/stytchauth/stytch-node) · [B2B overview](https://stytch.com/b2b)

## The model to keep in mind

```text
browser → your Node server → Stytch API: send email magic link
inbox → browser callback → your Node server → Stytch API: authenticate one-time token
Stytch → your server: user + session JWT
later browser request → your server: verify session JWT → allow protected content
```

The **project ID and secret** belong on the server. The email link token is short-lived proof from one login attempt. The session JWT represents an ongoing session. Authenticating a user proves identity; authorizing an action asks whether that identity may do it. Treat all three as different things. [Magic-link authenticate API](https://stytch.com/docs/api-reference/consumer/api/magic-links/authenticate) · [Session JWT API](https://stytch.com/docs/api-reference/consumer/api/sessions/authenticate-jwt)

## Timed route

| Time | Do this | Evidence you should have |
| --- | --- | --- |
| 0–8 min | Read the model above and [Stytch's quickstart](https://stytch.com/docs/get-started/quickstart). Do Exercise 1. | A six-step login trace in your own words. |
| 8–18 min | Read the [Node SDK example](https://github.com/stytchauth/stytch-node#example-b2c-usage) and the [login-or-create endpoint](https://stytch.com/docs/api-reference/consumer/api/magic-links/via-email/log-in-or-create-user). Do Exercise 2. | Know which SDK method maps to which HTTP request. |
| 18–28 min | Read [authenticate magic link](https://stytch.com/docs/api-reference/consumer/api/magic-links/authenticate) and [authenticate JWT](https://stytch.com/docs/api-reference/consumer/api/sessions/authenticate-jwt). Predict what happens for expired and reused links. | Know the token → session transition and failure path. |
| 28–48 min | Follow [project/README.md](project/README.md). Run the sample with a Stytch **test** Consumer project. If you have no credentials, trace `project/src/server.ts` and answer the same prompts without live calls. | A successful `/me` response or an annotated code trace. |
| 48–55 min | Do the two changes in Exercise 3 and diagnose one intentional error. | One edited flow and a written error diagnosis. |
| 55–60 min | Answer the recall prompts in [notes/stytch-notes.md](notes/stytch-notes.md). | A short integration checklist for your own app. |

## API map for your own integration

| Job | Node SDK | Raw API route | Input → result |
| --- | --- | --- | --- |
| Start login or signup | `client.magicLinks.email.loginOrCreate(...)` | `POST /v1/magic_links/email/login_or_create` | Email and redirect URLs → link sent, user ID in response |
| Redeem link | `client.magicLinks.authenticate(...)` | `POST /v1/magic_links/authenticate` | One-time token → user, session token, session JWT |
| Check protected request | `client.sessions.authenticateJwt(...)` | SDK helper with local JWT validation and API fallback | Session JWT → authenticated session/user |

The server SDK wraps HTTPS requests. The raw API uses the project ID and secret for authentication; your browser must never receive the secret. A missing default redirect URL can cause `loginOrCreate` to fail unless you pass configured login and signup redirect URLs. [Login-or-create reference](https://stytch.com/docs/api-reference/consumer/api/magic-links/via-email/log-in-or-create-user) · [Node SDK](https://github.com/stytchauth/stytch-node)

**After the hour:** transplant the `send → callback → session check` sequence into one route in your actual app. Then decide where your app stores the session, which routes require it, and whether you need Consumer users or B2B organizations/members.
