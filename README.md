# FastAPI Docker Hands-on

Saksham Katiyar · SAP ID: 590015169

Unit 4: containerize a small Student API, publish it to Docker Hub, observe requests and run two instances behind Nginx.

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

The student list is sample data in Python, not a database. No CRUD, login or extra application features are added.

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

The root response includes SAP ID `590015169` and location `Dehradun`, the tutorial's visible update. After a successful workflow run, pull and run the published image:

```bash
docker compose down
docker pull "$DOCKERUSERNAME/fastapi-app:v0.1"
docker run -d --name fastapi-app -p 127.0.0.1:8000:8000 "$DOCKERUSERNAME/fastapi-app:v0.1"
curl http://localhost:8000/
docker logs fastapi-app
docker rm -f fastapi-app
```

For a separate source-change demonstration, change a visible value in `home()`, commit and push, wait for Actions, and repeat these pull/run commands. A source change affects a container only after rebuilding its image and recreating the container.

## How it works

1. A browser or curl sends an HTTP request.
2. Uvicorn receives it and passes it to FastAPI.
3. Middleware starts a timer; the matching route returns a Python dictionary or list.
4. FastAPI converts that value into a JSON response; middleware logs the status and duration.
5. Docker packages the app and dependencies. Docker Hub stores the built image.
6. GitHub Actions runs the checks and publishes updated images.
7. Nginx distributes requests between two running copies of the API.

## Validation status

Verified on 17 November 2026 in [GitHub Actions run #1](https://github.com/saksham001k/fastapi-docker-handson/actions/runs/44056397908):

| Check | Result |
| --- | --- |
| Five API tests | Passed locally and in Actions |
| Docker image build | Passed in Actions |
| Two healthy API containers and Nginx startup | Passed in Actions |
| Twenty requests through Nginx | Passed; both upstream instances received requests |
| Docker Hub publishing | Blocked: one or both required Actions secrets are missing |
| Pull and run the published image / source-update demonstration | Pending successful publishing |

Add `DOCKERUSERNAME` and `DOCKERTOKEN` using the setup above. Then open the failed run in Actions and choose **Re-run all jobs**. After it succeeds, use the pull/run commands above on your Mac.

Tutorial: https://upessocs.github.io/#d=/Lectures/Backend%20Development/Theory/Unit%204/&f=Hands%20On%20Task.md
