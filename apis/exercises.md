# API exercise journal

Use this file for predictions and observations. The prediction is the important part: it makes gaps in your mental model visible.

## Session 1: first exchange

- Client:
- Server:
- Resource:
- Predicted method:
- Predicted response:
- Actual method:
- Actual status:
- Interesting request headers:
- Interesting response headers:
- Response body:
- What surprised me:

## Session 2: request experiments

Copy this block for every experiment.

### Experiment

- Question:
- Exact request:
- Prediction:
- Actual status:
- Actual response:
- Explanation:
- One variable to change next:

## Session 3: failure diagnosis

| Scenario | First thing to inspect | Likely meaning | Next test |
|---|---|---|---|
| 401 | | | |
| 404 | | | |
| 422 | | | |
| 429 | | | |
| 500 | | | |

## Session 4: endpoint checklist

| Endpoint | Happy path works | Invalid input tried | Notes |
|---|---:|---:|---|
| GET /health | ☐ | ☐ | |
| GET /tasks | ☐ | ☐ | |
| POST /tasks | ☐ | ☐ | |
| GET /tasks/{task_id} | ☐ | ☐ | |
| DELETE /tasks/{task_id} | ☐ | ☐ | |

## Session 5: explain it

Answer without looking up definitions:

1. What is an API?
2. What makes an endpoint different from a URL?
3. What does an HTTP method communicate?
4. What is the difference between a request header and body?
5. Why is a status code useful if the response also has a body?
6. What makes an error a client error or a server error?
7. What does an OpenAPI description add?
8. What would need to change before your task API could be used in production?
