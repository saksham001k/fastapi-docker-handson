import logging
import time

from fastapi import FastAPI, Request

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("student-api")
app = FastAPI(title="Student API")

students = [
    {"id": 1, "name": "Aarav", "course": "Backend Development"},
    {"id": 2, "name": "Diya", "course": "Backend Development"},
]


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("%s %s status=500 duration_ms=%.2f", request.method,
                         request.url.path, (time.perf_counter() - start) * 1000)
        raise
    logger.info("%s %s status=%s duration_ms=%.2f", request.method,
                request.url.path, response.status_code,
                (time.perf_counter() - start) * 1000)
    return response


@app.get("/")
def home():
    return {"application": "Student API", "framework": "FastAPI", "status": "running",
            "name": "Saksham Katiyar", "sap_id": "590015169", "location": "Dehradun"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/students")
def get_students():
    return students
