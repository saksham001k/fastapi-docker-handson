# Unit 4 — Combined Hands-on PBL

This extends the existing Docker repository with the [Student Management API from Theory Task 3](https://github.com/saksham001k/Backend-Development-/tree/main/Theory/Task3). The Dockerfile, Compose stack and Nginx are reused.

| Method and path | Expected output |
| --- | --- |
| GET / | App details, SAP ID, Dehradun and `demo: unit4-combined-task3` |
| GET /health | 200 and `{"status":"healthy"}` |
| GET /students | Student list; optional `?branch=CSE` filter |
| GET /students/{id} | Student or 404 |
| POST /students | 201 and the new student; 422 for missing fields |
| PUT /students/{id} | 200 and the updated student |
| DELETE /students/{id} | 204, then GET returns 404 |

## Run and check

```bash
docker compose up -d --build --wait
curl -fsS http://localhost:8080/
curl -fsS http://localhost:8080/students
BASE_URL=http://127.0.0.1:8001 python3 automationTesting.py
for i in {1..20}; do curl -fsS http://localhost:8080/health >/dev/null; done
docker compose logs --tail=25 nginx
docker compose down
```

Nginx distributes read requests across both instances; the logs show two upstream addresses. The previous app stores changes in RAM, so a write on one instance does not update the other and a restart resets the data. Run CRUD against port 8001 or 8002 directly. A real multi-instance CRUD app would use a shared database.

GitHub Actions runs the existing unit tests and the live HTTP suite before publishing to Docker Hub. After publishing, it pulls the exact commit-tagged image and repeats the route suite, including the new response marker. This verifies delivery of the change without auto-deploying to a production server.

For manual Docker build, push and pull commands, see the [main README](README.md). Logs show the method, path, status, and duration. Use latency and error rates to decide whether to investigate a bottleneck or scale.

## Verified result

[GitHub Actions run](https://github.com/saksham001k/fastapi-docker-handson/actions/runs/44730531624): 5 unit checks and 6 live HTTP checks passed, Nginx sent traffic to both instances, and images for AMD64 and ARM64 were published to Docker Hub. The runner pulled and ran the updated image and passed the live suite again.

[Course brief](https://upessocs.github.io/#d=/Lectures/Backend%20Development/Theory/Unit%204/&f=001%20Combined%20Hands%20On%20Task.md)
