# EduManage Backend API Service

FastAPI-powered RESTful backend for the EduManage Student Management System, featuring MongoDB Atlas persistence, Argon2 password hashing, JWT authentication, authoritative RBAC, automated risk analytics, and Google Gemini AI integration with deterministic fallback.

---

## 🛠️ Architecture & Core Components

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py               # Dependency injection: get_db, get_current_user, require_admin, require_teacher_or_admin, require_student
│   │   └── v1/
│   │       ├── api.py            # Central router registering all endpoint modules
│   │       └── endpoints/        # Auth, Users, Students, Attendance, Marks, AI Insights, AI Assistant, Analytics, Reports
│   ├── core/
│   │   ├── config.py             # Runtime configuration loaded via python-dotenv
│   │   └── security.py           # Argon2 password hashing & PyJWT token generation/decoding
│   ├── db/
│   │   ├── init_db.py            # Unique & compound index initialization
│   │   └── mongodb.py            # MongoDBManager singleton with connection pooling & ping health
│   ├── models/                   # Pydantic v2 schemas and models
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── student.py
│   │   ├── attendance.py
│   │   ├── marks.py
│   │   ├── ai_insights.py
│   │   ├── ai_assistant.py
│   │   ├── analytics.py
│   │   └── reports.py
│   ├── services/                 # Core domain services & business logic
│   │   ├── user_service.py
│   │   ├── student_service.py
│   │   ├── attendance_service.py
│   │   ├── marks_service.py
│   │   ├── ai_insights_service.py
│   │   ├── ai_assistant_service.py
│   │   ├── analytics_service.py
│   │   └── reports_service.py
│   └── main.py                   # FastAPI app instance, Lifespan manager, and CORS middleware
├── tests/                        # 168+ automated unit and integration tests
├── requirements.txt              # Production Python package requirements
├── run.py                        # Local ASGI runner
└── .env.example                  # Environment variable reference
```

---

## 🔐 Security Architecture

1. **Password Storage**: Argon2 hasher via `pwdlib`. Plaintext passwords are never persisted, logged, or returned in API schemas.
2. **Access Tokens**: JWT Bearer tokens signed with HMAC-SHA256 (`HS256`) containing `sub`, `role`, and UTC expiration claims.
3. **RBAC Validation**: Server-side dependencies enforce role boundaries. No student can access administrative endpoints or other students' private records (IDOR protection).
4. **CORS Security**: Configurable `CORS_ORIGINS` loaded from environment variables with credentials support.
5. **AI Safety**: Multi-layer security filters block prompt injections, credentials disclosure, and unauthorized queries before reaching the LLM.

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` in the `backend/` directory:

| Variable | Description | Default |
|---|---|---|
| `MONGODB_URL` | MongoDB connection URI (Atlas or Local) | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | Database name | `edumanage` |
| `MONGODB_SERVER_TIMEOUT_MS` | Server selection timeout in milliseconds | `2000` |
| `JWT_SECRET_KEY` | Secret key for JWT signing | *(Required in production)* |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifespan in minutes | `60` |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins | `http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000` |
| `AI_PROVIDER` | AI provider selector (`gemini` or `fallback`) | `fallback` |
| `GEMINI_API_KEY` | Google Gemini API Key | *(Optional, fallback active if unset)* |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.5-flash-lite` |

---

## 📡 API Endpoints Overview

Interactive OpenAPI documentation is available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Key Endpoints:
- `POST /api/auth/login` — Authenticate and issue JWT access token.
- `GET /api/auth/me` — Retrieve current authenticated user profile.
- `GET /api/health` — API health check.
- `GET /api/db/health` — MongoDB database connectivity check.
- `POST /api/students/` — Create new student record (Admin only).
- `GET /api/students/` — List & search students (Admin & Teacher).
- `GET /api/students/me` — Retrieve authenticated student's profile (Student only).
- `POST /api/attendance/` — Record attendance (Admin & Teacher).
- `GET /api/attendance/me` — Student personal attendance history (Student only).
- `POST /api/marks/` — Enter assessment marks and calculate grades (Admin & Teacher).
- `GET /api/marks/me` — Student personal marks records (Student only).
- `GET /api/ai-insights/students` — Institutional risk radar summary (Admin & Teacher).
- `GET /api/ai-insights/me` — Personal risk analysis and recommendations (Student only).
- `POST /api/ai-assistant/chat` — Contextual academic AI chat (All authenticated roles).
- `GET /api/analytics/admin/overview` — Institutional overview metrics (Admin only).
- `GET /api/analytics/teacher/overview` — Faculty class metrics (Admin & Teacher).
- `GET /api/analytics/student/me` — Student personal analytics (Student only).
- `GET /api/reports/students/export` — Stream CSV students report.
- `GET /api/reports/attendance/export` — Stream CSV attendance report.
- `GET /api/reports/marks/export` — Stream CSV marks report.
- `GET /api/reports/student/{student_id}/pdf` — Generate official student ISO 32000-1 PDF report.

---

## 🧪 Testing

Run the full pytest test suite:
```bash
python -m pytest -q
```
*Current test suite: 168 tests, 100% pass rate.*
