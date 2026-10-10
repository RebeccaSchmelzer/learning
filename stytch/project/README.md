# Stytch TypeScript mini-project

A small local Consumer email magic-link example for tracing an API integration. The server owns Stytch credentials; the browser receives an HTTP-only session cookie after the one-time callback token is authenticated. The only protected page is `/me`.

## Run with a Stytch test project

1. Use Node 20 or later. Create a **Consumer test project** in the [Stytch Dashboard](https://stytch.com/dashboard), then copy the test project ID and secret into a local `.env` based on `.env.example`.
2. In the Stytch Dashboard, allow `http://localhost:3000/callback` as the login and signup redirect URL. The exact URL must match `STYTCH_CALLBACK_URL`. [Redirect URL requirements](https://stytch.com/docs/api-reference/consumer/api/magic-links/via-email/log-in-or-create-user)
3. From this `project/` directory, install and run:

   ```sh
   npm install
   npm run dev
   ```

4. Open `http://localhost:3000`, submit an email you can access, click the received magic link, then open `/me`. Test project delivery rules may affect which addresses receive email; use an address permitted by your Stytch test settings.
5. Return to [the exercise](../exercises.md) and change the flow yourself.

No Stytch account? Read `src/server.ts` and trace each boundary. You can still complete every prediction and lookup exercise except the live observation.

## Route map

| Route | Purpose | Stytch call |
| --- | --- | --- |
| `GET /` | Show email form | none |
| `POST /send` | Ask Stytch to send a link | `magicLinks.email.loginOrCreate` |
| `GET /callback` | Redeem the one-time token | `magicLinks.authenticate` |
| `GET /me` | Check cookie before showing user ID | `sessions.authenticateJwt` |

This is an isolated learning app. Before using the pattern in production, add CSRF protection and rate limiting to the send route, set `Secure` on cookies under HTTPS, choose a session refresh and logout policy, and add authorization checks for business actions. [Session JWT behavior](https://stytch.com/docs/api-reference/consumer/api/sessions/authenticate-jwt)
