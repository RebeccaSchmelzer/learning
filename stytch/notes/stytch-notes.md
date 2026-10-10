# My Stytch notes

Edit this page directly in your visual Markdown editor. Changes appear locally immediately; no compiling, committing, or pushing is needed to preview your notes. Do not write credentials, magic-link tokens, or session JWTs here.

## My one-sentence explanation

Stytch is…
a library for providing authentication and session infrastructure through apis and sdks. it's consumer product provides magic links, passcodes, and oauth. the b2b product centers around orgs and members, providing sso and role based access. helps to build secure user login systems.

## Login trace

1. Visitor enters an email: sends email to backend server, POST /login
2. My server: calls stytch magic link send api with that email then tells stytch where user should be redirected after clicking the link
3. Stytch: looks up or creates the stytch user, generates a single user magic link token, and sends the email containing the magic link
4. Visitor clicks the link: the browser follows the link and lands on the configured callbak url (ex/ `/auth/callback?token=...&stytch_token_type=magic_links`)
5. My server: extracts the magic link token and sends it to stytch's magic link authenticate api endpoint, stytch verifies the token and then returns the session token and the session jwt. the server then stores the session credential in a  secure cookie and then redirects the user to the app
6. On the next protected request: the browser automatically sends the session cookie, server reads it and validates it, gets the users authed id, allows or rejects the request. with stytch you can authenticate the opaque `session_token` against Stytch, or validate a `session_jwt` locally using Stytch's signing keys/SDK.

## Product choice

**Consumer fits when:**


**B2B fits when:**


## API map

**Send link — SDK method and HTTP path:**


**Authenticate link — SDK method and HTTP path:**


**Check session — SDK method and result:**


## Trust boundaries

**Server-only value:**


**One-time value:**


**Ongoing session value:**


## What I changed in the demo


## One failure I diagnosed

**Prediction:**


**Observed result or doc evidence:**


**Fix:**


## My app integration checklist

- [ ] Pick Consumer or B2B based on the user/member data model.
- [ ] Create a test project and configure approved redirect URLs.
- [ ] Keep the project secret in server environment variables.
- [ ] Send link and redeem callback token.
- [ ] Store session securely and verify it on protected requests.
- [ ] Add authorization checks for actual business actions.
- [ ] Test expired links, missing cookies, and API errors.

## Final recall, from memory

**What Stytch owns / what my app owns:**


**Why the link token and session JWT differ:**


**The three SDK calls:**


**Where authorization belongs:**


**What changes for organizations and SSO:**

