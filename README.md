# FastAPI Docker Hands-on

Saksham Katiyar · SAP ID: 590015169

Unit 4: containerize a small Student API, publish it to Docker Hub, observe requests and run two instances behind Nginx.

## Coursework links

- [Main Backend Development repository](https://github.com/saksham001k/Backend-Development-)
- [Unit 4 reference](https://github.com/saksham001k/Backend-Development-/blob/main/Theory/Unit4/README.md)
- [Course website](https://saksham001k.github.io/Backend-Development-/#unit4)
- [Personal coursework portal](https://saksham001k.github.io/#unit4)

This separate repository contains the project code. The course repository and portals link here.

## Files

| File | Purpose |
| --- | --- |
| `main.py` | Three GET routes and request logging |
| `requirements.txt` | FastAPI and Uvicorn dependencies |
| `Dockerfile` | Python 3.12 container and health check |
| `compose.yaml` | Two API instances and Nginx |
| `nginx.conf` | Round-robin load balancing |
| `.github/workflows/ActionsYaml.yaml` | Test, build and publish on push to main |
| `tests/test_main.py` | API response and logging checks |

The Combined Hands-on PBL reuses the [Unit 1 Task 3 Student Management API](https://github.com/saksham001k/Backend-Development-/tree/main/Theory/Task3). See [Combined Hands-on](COMBINED-HANDSON.md) for the route tests and updated image checks.

## Run without Docker

Run from this repository's folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python -m uvicorn main:app --reload
```

Open http://localhost:8000, http://localhost:8000/students and http://localhost:8000/docs.

## Build and run a container

Start Docker Desktop first. Replace `YOUR_DOCKERHUB_USERNAME` with your Docker Hub username.

```bash
export DOCKERUSERNAME=YOUR_DOCKERHUB_USERNAME
docker build -t "$DOCKERUSERNAME/fastapi-app:v0.1" .
docker run -d --name fastapi-app -p 127.0.0.1:8000:8000 "$DOCKERUSERNAME/fastapi-app:v0.1"
curl http://localhost:8000/health
curl http://localhost:8000/students
curl -w '\nTime: %{time_total}s\n' http://localhost:8000/
for i in {1..20}; do curl -s http://localhost:8000/students; echo; done
docker logs fastapi-app
docker stats --no-stream fastapi-app
docker rm -f fastapi-app
```

Logging records the method, path, HTTP status and processing duration. Query strings are excluded. `curl` total time also includes connection and response transfer time.

## Publish to Docker Hub

Create a Docker Hub repository called `fastapi-app`. Generate a personal access token with permission to push. Use the token at the password prompt; do not save it in code or commit it.

```bash
docker login --username "$DOCKERUSERNAME"
docker push "$DOCKERUSERNAME/fastapi-app:v0.1"
```

In this GitHub repository, open **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret | Value |
| --- | --- |
| `DOCKERUSERNAME` | Your Docker Hub username |
| `DOCKERTOKEN` | Your Docker Hub access token |

Push to `main`, then open **Actions**. The test job checks the API and the Docker stack. The publish job pushes `v0.1` and a commit-specific tag to Docker Hub. Missing secrets cause a clear failure instead of a false successful publish. Both Intel/AMD and Apple Silicon images are built.

## Monitoring and scaling

```bash
docker compose up -d --build --wait
curl http://localhost:8001/health
curl http://localhost:8002/health
for i in {1..20}; do curl -s http://localhost:8080/students; echo; done
docker compose logs nginx
docker compose logs fastapi-1 fastapi-2
docker stats --no-stream
```

Open http://localhost:8080/students. Nginx sends requests to `fastapi-1` and `fastapi-2` in turn. The `upstream=` addresses in its logs identify which instance answered. Both instances return the same data. Docker's shared network lets Nginx use service names on macOS and Linux.

## Verify the published update

The updated root response includes SAP ID `590015169`, location `Dehradun`, and the marker `demo: unit4-combined-task3`. After a successful workflow run, pull and run the published image:

```bash
docker compose down
docker pull "$DOCKERUSERNAME/fastapi-app:v0.1"
docker run -d --name fastapi-app -p 127.0.0.1:8000:8000 "$DOCKERUSERNAME/fastapi-app:v0.1"
curl http://localhost:8000/
docker logs fastapi-app
docker rm -f fastapi-app
```

For a future source-change demonstration, update the marker in `read_root()` and its assertion in `automationTesting.py`, commit and push, wait for Actions, and repeat these pull/run commands. A source change affects a container only after rebuilding its image and recreating the container.

## How it works

1. A browser or curl sends an HTTP request.
2. Uvicorn receives it and passes it to FastAPI.
3. Middleware starts a timer; the matching route returns a Python dictionary or list.
4. FastAPI converts that value into a JSON response; middleware logs the status and duration.
5. Docker packages the app and dependencies. Docker Hub stores the built image.
6. GitHub Actions runs the checks and publishes updated images.
7. Nginx distributes requests between two running copies of the API.

## Original Docker demo verification

Verified on 17 November 2026 in [GitHub Actions run #2](https://github.com/saksham001k/fastapi-docker-handson/actions/runs/44060310292):

| Check | Result |
| --- | --- |
| Five API tests | Passed locally and in Actions |
| Docker image build | Passed in Actions |
| Two healthy API containers and Nginx startup | Passed in Actions |
| Twenty requests through Nginx | Passed; both upstream instances received requests |
| Docker Hub publishing | Passed for linux/amd64 and linux/arm64; v0.1 and commit tags pushed |
| Pull and run the published image | Passed in Actions; health, student list, SAP ID and Dehradun verified |

Local verification on my Mac on 17 November 2026 also confirmed both healthy API containers, Nginx, root/student/health/docs responses and requests reaching both upstreams. `docker compose down` stopped the stack successfully.

The full workflow passed. Docker Hub credentials are stored in Actions secrets. The workflow trims surrounding whitespace from the username before using it in image tags. Use the pull/run commands above to run the published image on your Mac.

Tutorial: https://upessocs.github.io/#d=/Lectures/Backend%20Development/Theory/Unit%204/&f=Hands%20On%20Task.md
