# Stytch exercises

Write answers in [notes/stytch-notes.md](notes/stytch-notes.md). Read the relevant official page first, predict behavior, then check the reference or run the sample.

## Exercise 1 — trace and choose (8 minutes)

1. Draw the six steps from entering an email to opening `/me`. Mark every hop that crosses your server's boundary.
2. Which data may exist in the browser: project ID, project secret, one-time link token, session JWT? Which must stay on the server?
3. Would you choose Consumer or B2B for (a) a personal finance app and (b) a SaaS product where each customer company controls its members and SSO? Explain the data-model reason.

**Check:** your trace must include *send link*, *callback token*, *authenticate token*, *session*, and *verify on the next request*.

## Exercise 2 — API reading (10 minutes)

Open [login or create](https://stytch.com/docs/api-reference/consumer/api/magic-links/via-email/log-in-or-create-user) and [authenticate](https://stytch.com/docs/api-reference/consumer/api/magic-links/authenticate).

1. Find each HTTP method and path. Find the matching camelCase SDK method in the [Node SDK](https://github.com/stytchauth/stytch-node).
2. Predict what `loginOrCreate` returns. Does that response itself log the browser in?
3. Find the `session_duration_minutes` parameter. What does it affect?
4. Find the `error_type` field in an error. Name one error you would show to the user as “please try again” rather than printing the raw response.

**Check:** the send response identifies the request/user; the authenticate response carries session material. A protected route needs a subsequent session check.

## Exercise 3 — investigate and change (25 minutes)

Open [project/src/server.ts](project/src/server.ts). Predict each route's result **before** running it.

1. Run the app using [project/README.md](project/README.md), or trace the file without credentials. Follow one request through `/send`, `/callback`, then `/me`. Record the `user_id` at the point the session is created and checked. Never paste tokens or secrets into notes.
2. Change the login page's heading, and change the callback's session duration from 60 to 30 minutes. Explain which output or cookie lifetime also needs updating.
3. Try `/me` in a fresh private browser window. Predict and observe the response.
4. Intentionally break the configured callback URL or use an invalid token in a **test** project. Locate the error boundary. Record the `error_type` and HTTP status if available; do not record credentials or tokens.

**Check:** an untrusted URL token cannot be accepted merely because it is present. The server authenticates it with Stytch, then issues a session cookie. `/me` independently checks that cookie. If the Stytch call fails, the app must not issue a valid session.

## Five-minute recall

Close the docs. In your notes, answer:

- What does Stytch own, and what does your app still own?
- Why are the link token and session JWT different?
- Which three SDK calls form the core example?
- Where would you add authorization for a protected business action?
- What changes if your app needs organization-level membership and SSO?
