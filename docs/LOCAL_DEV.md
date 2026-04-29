it give me Error loading email# Running Locally

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and docker-compose

That's it.

---

## Steps

**1. Clone and enter the project**

```bash
git clone <repo-url>
cd BUA_Labs_Attendance
```

**2. Set up the environment file**

```bash
cp backend/.env.example backend/.env
```

Open `backend/.env` and set `GOOGLE_SERVICE_ACCOUNT_JSON` to the full JSON content of your Google service account key file. Everything else can stay as-is for local use.

**3. Start**

```bash
docker-compose up --build
```

First run takes a few minutes (downloads the Python image and installs dependencies). Subsequent starts are fast.

---

## URLs

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:8080        |
| Backend  | http://localhost:8000        |
| API docs | http://localhost:8000/docs   |

---

## Stop

```bash
docker-compose down
```

---

## Notes

- The backend hot-reloads on file changes inside `backend/`.
- Frontend changes (in `frontend/`) are served immediately by nginx — just refresh the browser.
- If you don't have a Google service account yet, see the [Google Cloud setup section in README.md](../README.md#1-google-cloud-service-account-setup).
