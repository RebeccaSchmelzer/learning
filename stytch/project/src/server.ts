import "dotenv/config";
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import * as stytch from "stytch";

const projectId = process.env.STYTCH_PROJECT_ID;
const secret = process.env.STYTCH_SECRET;
const callbackUrl = process.env.STYTCH_CALLBACK_URL;

if (!projectId || !secret || !callbackUrl) {
  throw new Error("Set STYTCH_PROJECT_ID, STYTCH_SECRET, and STYTCH_CALLBACK_URL in .env");
}

const client = new stytch.Client({ project_id: projectId, secret });
const cookieName = "stytch_session_jwt";

function send(res: ServerResponse, status: number, body: string, headers: Record<string, string> = {}) {
  res.writeHead(status, { "content-type": "text/plain; charset=utf-8", ...headers });
  res.end(body);
}

function readCookie(req: IncomingMessage, name: string): string | undefined {
  const raw = req.headers.cookie?.split("; ").find((part) => part.startsWith(`${name}=`));
  return raw ? decodeURIComponent(raw.slice(name.length + 1)) : undefined;
}

async function readBody(req: IncomingMessage): Promise<string> {
  let body = "";
  for await (const chunk of req) {
    body += chunk;
    if (body.length > 4096) throw new Error("request_too_large");
  }
  return body;
}

function errorCode(error: unknown): string {
  if (typeof error === "object" && error !== null && "error_type" in error) {
    return String(error.error_type);
  }
  return error instanceof Error ? error.message : "unknown_error";
}

createServer(async (req, res) => {
  const url = new URL(req.url ?? "/", "http://localhost:3000");

  try {
    if (req.method === "GET" && url.pathname === "/") {
      res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
      res.end(`<h1>Stytch learning lab</h1><form method="POST" action="/send"><label>Email <input name="email" type="email" required></label><button>Send magic link</button></form>`);
      return;
    }

    if (req.method === "POST" && url.pathname === "/send") {
      const email = new URLSearchParams(await readBody(req)).get("email")?.trim();
      if (!email) return send(res, 400, "Enter an email address.");
      await client.magicLinks.email.loginOrCreate({
        email,
        login_magic_link_url: callbackUrl,
        signup_magic_link_url: callbackUrl,
      });
      return send(res, 200, "Check your email for a magic link.");
    }

    if (req.method === "GET" && url.pathname === "/callback") {
      const token = url.searchParams.get("token");
      if (!token) return send(res, 400, "Missing magic-link token.");
      const result = await client.magicLinks.authenticate({ token, session_duration_minutes: 60 });
      res.writeHead(303, {
        location: "/me",
        "set-cookie": `${cookieName}=${encodeURIComponent(result.session_jwt)}; HttpOnly; SameSite=Lax; Path=/; Max-Age=3600`,
      });
      res.end();
      return;
    }

    if (req.method === "GET" && url.pathname === "/me") {
      const jwt = readCookie(req, cookieName);
      if (!jwt) return send(res, 401, "No session. Start at /.");
      const result = await client.sessions.authenticateJwt({ session_jwt: jwt });
      return send(res, 200, `Authenticated user: ${result.session.user_id}`);
    }

    send(res, 404, "Not found");
  } catch (error) {
    // Never log or return raw credentials, link tokens, or session JWTs.
    const code = errorCode(error);
    console.error("Stytch learning lab error:", code);
    send(res, code === "request_too_large" ? 413 : 400, `Request failed: ${code}`);
  }
}).listen(3000, () => console.log("Open http://localhost:3000"));
