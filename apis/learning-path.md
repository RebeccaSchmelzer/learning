# APIs: a five-hour learning path

## Assumptions

- Starting point: beginner with APIs; basic programming familiarity is helpful but not required for the first three sessions.
- Time: five hours over one week.
- Goal: practical usage. By the end, you should be able to explain an API request, use an HTTP API, diagnose common failures, and build a small API.
- Project language: Python with FastAPI. The HTTP concepts transfer to any language or framework.

## Topic type

- **Primary type:** Broad technical concept.
- **Secondary types:** Protocol/API foundation, external API integration, API design, and introductory system design.
- **Why this fits:** “API” names a way for software to interact, not one product or library. Learning it well requires a mental model, the HTTP rules commonly used on the web, practice consuming an external API, and practice designing a small one.

## Learning depth

- **Desired depth:** Practical usage.
- **Competence by the end:** You can identify the client, server, resource, endpoint, method, headers, body, and status code in a real exchange; make and modify requests; read API documentation; distinguish likely client and server failures; and explain the design of a small CRUD-style API.

## Curriculum emphasis

- 20% mental model and vocabulary
- 25% HTTP and documentation reading
- 25% calling and debugging APIs
- 25% building and designing a small API
- 5% review and explanation

Deferred for a later path: OAuth flows, production authentication, webhooks, GraphQL, gRPC, API gateways, distributed tracing, deployment, and large-scale reliability.

## Core mental model

An API is a contract between two pieces of software. For a web API, a client sends an HTTP request to an endpoint and a server returns an HTTP response.

```text
client
  │  request: method + URL + headers + optional body
  ▼
server
  │  response: status + headers + optional body
  ▼
client
```

A useful first question is always: “What exact request was sent, and what exact response came back?”

## Session 1 — See the exchange (45 minutes)

### Read

1. [MDN: Overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
2. Skim [MDN: HTTP request methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods)

### Learn

Define these in your own words: client, server, resource, endpoint, request, response, method, URL, header, body, JSON, and status code.

### Do

Open this URL in a browser:

```text
https://jsonplaceholder.typicode.com/todos/1
```

Before opening it, predict:

- Who is the client?
- Who is the server?
- Which resource is requested?
- Which method will the browser use?
- What shape might the response have?

Record the result in [exercises.md](exercises.md). Then use your browser’s developer tools, if available, to find the request method, status, response headers, and response body.

### Checkpoint

Without notes, explain the request/response cycle in 60 seconds.

## Session 2 — Make and change requests (60 minutes)

### Read

1. [JSONPlaceholder guide](https://jsonplaceholder.typicode.com/guide/)
2. Use [MDN’s method reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods) when a verb is unfamiliar.

### Do

Run these in a terminal. Predict the status and body before each request.

```bash
curl -i https://jsonplaceholder.typicode.com/posts/1
curl -i "https://jsonplaceholder.typicode.com/posts?userId=1"
curl -i -X POST https://jsonplaceholder.typicode.com/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"learn APIs","body":"trace every exchange","userId":1}'
```

Then deliberately alter one part at a time:

- Request a missing resource such as `/posts/999999`.
- Remove or misspell the `Content-Type` header.
- Send malformed JSON.
- Change `POST` to `GET` while keeping a body.

For each result, record the request, your prediction, the actual response, and your explanation.

### Checkpoint

Explain how the URL, method, headers, and body play different roles.

## Session 3 — Read contracts and debug failures (60 minutes)

### Read

1. [MDN: HTTP status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)
2. [OpenAPI introduction](https://learn.openapis.org/introduction.html)

Focus on these codes: `200`, `201`, `204`, `400`, `401`, `403`, `404`, `409`, `422`, `429`, and `500`.

### Do

For each scenario below, write the first thing you would inspect:

1. The response is `401`.
2. The response is `404`.
3. The response is `422`.
4. The response is `429`.
5. The response is `500`.

Then inspect the interactive API documentation from the project in Session 4. Find:

- available endpoints
- required path and body fields
- possible response schemas
- a way to send a test request

### Debugging routine

Use this order:

1. Reproduce the failure.
2. Capture the exact request and response.
3. Compare them with the API contract.
4. Change one variable.
5. Retry and record what changed.
6. Explain the cause before changing more code.

## Session 4 — Build a tiny API (90 minutes)

Use the scaffold in [project](project/README.md) and the [official FastAPI first steps](https://fastapi.tiangolo.com/tutorial/first-steps/).

Build a task API with this contract:

| Method | Path | Purpose | Expected success |
|---|---|---|---|
| GET | `/health` | Check that the service is running | `200` |
| GET | `/tasks` | List tasks | `200` |
| POST | `/tasks` | Create a task | `201` |
| GET | `/tasks/{task_id}` | Fetch one task | `200` or `404` |
| DELETE | `/tasks/{task_id}` | Remove one task | `204` or `404` |

Work in this order:

1. Run the starter and call `GET /health`.
2. Read `main.py` and predict what `GET /tasks` returns.
3. Add `POST /tasks`.
4. Add `GET /tasks/{task_id}`.
5. Add `DELETE /tasks/{task_id}`.
6. Use the generated `/docs` page to test every endpoint.
7. Send invalid input and inspect the error response.

Keep data in memory. A database would distract from the API concepts in this time box.

## Session 5 — Test your understanding (45 minutes)

### Failure drills

Try at least three:

- Send a string where a numeric ID is expected.
- Fetch a task that does not exist.
- Create a task without a required field.
- Send invalid JSON.
- Call an endpoint with an unsupported method.

For each, write:

- your prediction
- the actual status and body
- whether the client, server, or contract caused the issue
- the smallest reasonable fix

### Final demonstration

In five minutes, show and explain:

1. A successful request.
2. A deliberately failed request.
3. How the API contract describes both.
4. One design choice you made.
5. One limitation of the project.

You are done when you can explain the exchange without relying on framework vocabulary.

## What to study next

Choose based on your goal:

- **Use third-party APIs:** authentication, API keys, pagination, rate limits, retries, and SDKs.
- **Build backend services:** validation, databases, tests, authentication, logging, and deployment.
- **Design APIs:** resource modeling, idempotency, versioning, error formats, and OpenAPI.
- **Build frontend apps:** JavaScript `fetch`, browser security, CORS, loading states, and error handling.
