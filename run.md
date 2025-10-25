# Project Quorum: Backend Setup and Developer Guide

This guide provides comprehensive instructions for setting up, running, and developing the Project Quorum backend.

## 1. Prerequisites

Before you begin, ensure you have the following installed:

-   **Python 3.9+**
-   **Git** for version control.
-   A package manager for Python, such as `pip`, which comes with Python.

## 2. Backend Setup

Follow these steps to get the backend running on your local machine.

### Step 1: Clone the Repository

If you haven't already, clone the project repository to your local machine.

### Step 2: Navigate to the Backend Directory

Open your terminal or command prompt and navigate to the `backend` directory:

```bash
cd backend
```

### Step 3: Create and Activate a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies.

**On Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

**On macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

Install all the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

## 3. Configuration

The backend uses a `.env` file for configuration.

### Step 1: Create the `.env` File

Create a `.env` file by copying the example file:

**On Windows:**

```bash
copy .env.example .env
```

**On macOS/Linux:**

```bash
cp .env.example .env
```

### Step 2: Generate an Encryption Key

For security, the application uses an encryption key. A script is provided to generate one.

```bash
python utils/key_generator.py
```

Copy the generated key from the console.

### Step 3: Update the `.env` File

Open the `.env` file and paste the generated key as the value for `ENCRYPTION_KEY`. You can also adjust other settings in this file if needed.

```dotenv
# .env
ENCRYPTION_KEY=your_generated_key_here
# ... other settings
```

## 4. Running the Backend Server

Once the setup and configuration are complete, you can start the backend server.

### Start the Server

From within the `backend` directory, run the following command:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

-   `--host 0.0.0.0`: Makes the server accessible from your local network (e.g., for frontend testing from a different device).
-   `--port 8000`: Runs the server on port 8000.
-   `--reload`: Automatically restarts the server when code changes are detected.

You should see output from `uvicorn` indicating that the server is running.

### Accessing the API

The backend API will be available at `http://localhost:8000`.

The interactive API documentation (Swagger UI) is available at `http://localhost:8000/docs`. This is the best place to view all available endpoints, their parameters, and test them directly from your browser.

## 5. Frontend Integration

For frontend developers, the process is straightforward:

1.  Ensure the backend server is running.
2.  Make API calls from the frontend application to `http://localhost:8000`.
3.  Refer to the API documentation at `http://localhost:8000/docs` for details on each endpoint.

**CORS:** Cross-Origin Resource Sharing (CORS) is enabled by default for `http://localhost:3000` (the default for Vite/React development servers). If your frontend is running on a different port, you will need to add its origin to the `ALLOWED_HOSTS` variable in the `.env` file.

## 6. Developer Guidelines

To maintain code quality and consistency, please follow these guidelines when contributing to the backend:

-   **Documentation:** If you add or modify backend functionality that the frontend depends on, please document these changes. Create a new Markdown file in the `backend/docs` directory (e.g., `changes_yourname_date.md`) detailing:
    -   What was changed or created.
    -   The reason for the change.
    -   The specific frontend components that will be affected or will use this new functionality.
-   **Code Style:** Follow existing code style and conventions.
-   **Directory Structure:** Do not change the existing directory structure without team consensus.

## 7. Project Structure

Here is an overview of the current project structure:

```
e:/SIH/
├── .gitignore
├── REPORT.md
├── run.md
├── backend/
│   ├── .env.example
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── core/
│   │   ├── database.py
│   │   ├── detection_engine.py
│   │   ├── isolation_validator.py
│   │   ├── security.py
│   │   ├── soup_handlers.py
│   │   └── utils.py
│   ├── data/
│   │   ├── duckdb/
│   │   ├── logs/
│   │   ├── mitre_attack/
│   │   │   └── ttp_patterns.json
│   │   ├── models/
│   │   │   ├── iforest_model.pkl
│   │   │   └── tfidf_vectorizer.pkl
│   │   ├── rules/
│   │   │   └── detection_rules.json
│   │   ├── temp/
│   │   └── threat_intel/
│   │       └── indicators.json
│   ├── docs/
│   │   ├── API_ENDPOINTS.md
│   │   ├── deployment_modes.md
│   │   ├── fetaures.md
│   │   ├── offline_training.md
│   │   └── progress_report.md
│   ├── routes/
│   │   ├── analysis.py
│   │   ├── health.py
│   │   ├── logs.py
│   │   ├── quorum_private.pem
│   │   ├── quorum_public.pem
│   │   └── soup.py
│   ├── scripts/
│   │   └── verify_offline_ready.py
│   ├── services/
│   │   ├── ai_engine.py
│   │   ├── collector_service.py
│   │   ├── parser_service.py
│   │   ├── report_service.py
│   │   └── storage_service.py
│   └── utils/
│       └── key_generator.py
├── frontend/
│   ├── .gitignore
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.cjs
│   ├── README.md
│   ├── tailwind.config.cjs
│   ├── vite.config.js
│   ├── public/
│   └── src/
│       ├── App.css
│       ├── App.jsx
│       ├── index.css
│       ├── main.jsx
│       ├── assets/
│       ├── components/
│       ├── data/
│       ├── lib/
│       ├── pages/
│       ├── styles/
│       └── utils/
├── PS with Solution/
│   ├── PS.md
│   ├── PS.txt
│   ├── Solution_ppt.pdf
│   ├── solution.md
│   └── soultion.txt
└── training_model_code/
    ├── enhanced_training.py
    └── Quorum.ipynb
```