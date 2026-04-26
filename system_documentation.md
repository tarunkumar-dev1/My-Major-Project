# AI-Based Skill Gap Analyzer - Technical Documentation

This document provides a comprehensive overview of the AI-Based Skill Gap Analyzer for Students, detailing its architecture, components, features, and setup instructions.

---

> [!NOTE]
> This application leverages Python Flask for the backend, Vanilla HTML/CSS/JS for the frontend, MongoDB for data storage, and the Google Gemini LLM API to generate dynamic, personalized learning roadmaps based on a user's current skills and desired career goals.

## Table of Contents
1. [System Architecture](#1-system-architecture)
2. [Frontend Architecture (UI/UX)](#2-frontend-architecture-uiux)
3. [Backend Architecture & API Endpoints](#3-backend-architecture--api-endpoints)
4. [Database Structure](#4-database-structure)
5. [AI Integration (Gemini)](#5-ai-integration-gemini)
6. [Local Deployment Setup](#6-local-deployment-setup)

---

## 1. System Architecture

The project follows a standard decoupled Client-Server architecture:
*   **Frontend Client:** A lightweight, pure HTML/CSS/JS client relying completely on AJAX (Fetch API) requests for dynamic rendering. No templating engine (like Jinja) is restricting the UI.
*   **Backend API:** A RESTful backend built with **Flask** providing structured endpoints.
*   **Database Engine:** **MongoDB** documents, offering flexibility over user nested profile data and roadmap objects.
*   **External Service:** **Google Gemini API**, heavily utilized by the backend's AI Module logic to generate content based on complex skill comparisons.

---

## 2. Frontend Architecture (UI/UX)

The user interfaces are designed as a clean, modern SaaS layout featuring light/dark mode logic with responsive glassmorphism containers.

### Core Interface Pages:

| Page | Description | Key Elements |
| :--- | :--- | :--- |
| `index.html` | The landing page of the application introducing the tool. | Hero Section, Features summary, Call-to-actions to Auth flows. |
| `signup.html` | User registration page. | Form tracking Name, Email, Password. Connects with `/api/auth/signup`. |
| `dashboard.html` | Central hub for the student. | Navigation Sidebar, Quick Summary Cards (Current Skills, Goal), recent activities. |
| `analyze.html` | The core "Input" engine. | Form for users to enter their current comma-separated explicitly known skills, plus their target career role. |
| `progress.html` | The dynamic learning roadmap UI. | Fetches the AI-generated JSON learning path and recursively dynamically renders it as a nested tree/timeline of modules, checking off completed tasks. |
| `profile.html` | User settings modification. | Form to update name and career goals (`PUT /api/student/profile`). |
| `admin.html` | Administrator dashboard. | Displays aggregate trends across system users (e.g., most popular career goals) using visual charts and tabular user records. |

---

## 3. Backend Architecture & API Endpoints

The core logic lies in `/backend/app/`. The standard routing operates under an `api` prefix.

### Authentication Endpoints (`/api/auth`)
*   `POST /signup`: Registers a new user inside the MongoDB `users` collection. Requires `name`, `email`, and `password`. Passwords are encrypted before storing.
*   `POST /login`: Authenticates user credentials. Returns a JWT Token used as a Bearer Token for subsequent requests.

### Student Interface Endpoints (`/api/student`)
> [!IMPORTANT]
> All student endpoints require a Valid JWT sent via the `Authorization: Bearer <token>` header.

*   `POST /submit-skills`: Expects `{ "skills": [], "career_goal": "" }`. This is the heavy lifting endpoint that talks to the `AnalysisService`, identifies skill shortages, and talks to the `RoadmapService` (and thereby Google Gemini) to generate the learning modules.
*   `GET /dashboard`: Dispatches user profile and metadata (omitting the hashed password) used to load the dashboard.
*   `GET /roadmap`: Fetches the currently persisted AI roadmap linked to the specific student.
*   `POST /mark-completed`: Expects a `{ "skill": "" }` payload. Appends to the user's `completed_skills` array within MongoDB to update progress.
*   `PUT /profile`: Updates basic user profile info.

### Administrative Endpoints (`/api/admin`)
*   `POST /add-career`: Inserts or Upserts base career templates into the system (`MongoDB: careers`) defining baseline required skills and a generalized difficulty.
*   `GET /users`: Aggregates trends using MongoDB's `$group` pipeline, revealing the most dominant career goals across registered students.

---

## 4. Database Structure

The standard structure implies two primary MongoDB document models:

### `users` Collection
Stores both credentials, user metrics, and the heavily nested generated roadmap objects.
```json
{
  "_id": ObjectId,
  "name": "Jane Example",
  "email": "jane@example.com",
  "hashed_password": "scrypt:...",
  "career_goal": "Frontend Developer",
  "completed_skills": ["HTML", "CSS"],
  "roadmap": {
    "modules": [
      {
        "title": "Module 1",
        "description": "...",
        "resources": [...]
      }
    ]
  }
}
```

### `careers` Collection
Stores baseline job-role assumptions defined by admins.
```json
{
  "_id": ObjectId,
  "career_name": "Data Scientist",
  "difficulty_level": "Advanced",
  "required_skills": ["Python", "SQL", "Pandas", "Math"]
}
```

---

## 5. AI Integration (Gemini)

The system bypasses basic hardcoded "If-Else" roadmap routing by incorporating generative AI.

1.  **Skill Comparison:** The application dynamically measures user input capabilities against a desired standard.
2.  **Prompt Engineering:** The backend constructs highly structured prompts dictating that the LLM engine return responses specifically formatted in strict JSON structure outlining specific training modules matching the detected gap.
3.  **Persistence:** The generated JSON blocks are loaded, verified, optionally structured by the `RoadmapService` and persisted directly to the User's MongoDB Document preventing excessive re-generation api calls.

---

## 6. Local Deployment Setup

To bring up the environment, follow these sequences:

### Prerequisite Environment
- Python 3.9+
- Activated local MongoDB Daemon (Running at `mongodb://localhost:27017` or configured via `.env`).
- Environment configuration `GEMINI_API_KEY` for LLM integrations. 

### Starting the Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate   # (Windows)
pip install -r requirements.txt
python app.py
```
> [!TIP]
> The Flask server typically reserves `http://localhost:5000`

### Starting the Frontend View
Since it is vanilla HTML, you merely need a local webserver pointing to the repository root avoiding direct `file://` CORS issues.
```bash
# Executed from project root
python -m http.server 8000
```
Then navigate to `http://localhost:8000/index.html`
