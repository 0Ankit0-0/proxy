# How to Run the Backend 
# Note:
1. Do not change backend code or directory structure.
2. If you modify or create any file, document it in a new .md file (e.g., changes_yourname_date.md) under /docs.
3. Always include:
   1. What you created/modified
   2. Why it was done
   3. What frontend components depend on it


This guide provides instructions on how to set up and run the Project Quorum backend server.

## Prerequisites

-   Python 3.9+
-   A virtual environment tool (like `venv`)

## 1. Setup and Installation

1.  **Navigate to the backend directory:**

    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**

    On Windows:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

    On macOS/Linux:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## 2. Configuration

1.  **Create a `.env` file** in the `backend` directory by copying the example file:

    On Windows:
    ```bash
    copy .env.example .env
    ```
    On macOS/Linux:
    ```bash
    cp .env.example .env
    ```

2.  **Generate an encryption key** (optional but recommended for security). You can use the provided script:

    ```bash
    python utils/key_generator.py
    ```
    This will generate a key and print it to the console.

3.  **Update the `.env` file** with the generated `ENCRYPTION_KEY` and other configurations as needed.

    ```
    # .env
    ENCRYPTION_KEY=your_generated_key_here
    # ... other settings
    ```

## 3. Running the Server

1.  **Start the FastAPI server** using `uvicorn` from within the `backend` directory:

    ```bash
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload
    ```
    -   `--host 0.0.0.0` makes the server accessible on your local network.
    -   `--port 8000` runs the server on port 8000.
    -   `--reload` automatically restarts the server when code changes are detected (useful for development).

2.  **Access the API documentation:**

    Once the server is running, you can access the interactive API documentation (Swagger UI) at:
    [http://localhost:8000/docs](http://localhost:8000/docs)

## 4. Workflow for Your Friend (Frontend Developer)

1.  **Run the backend server** as described above.
2.  **Use the API documentation** at `http://localhost:8000/docs` to understand the available endpoints, their request formats, and responses.
3.  **The frontend application can now make API calls** to the backend at `http://localhost:8000`. For example, to upload a log file, the frontend would make a `POST` request to `http://localhost:8000/logs/upload`.
4.  **CORS is enabled** for the default frontend development server (`http://localhost:3000`), so there should be no cross-origin issues. If the frontend is running on a different port, you may need to update the `ALLOWED_HOSTS` in the `.env` file.

**File Structure(JO nhi haui vo file bana lena or AI train nhi hai to kal karu )** 
SIH\
├── .gitignore
├── REPORT.md
├── run.md
├── backend\
│   ├── .env.example
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── core\
│   │   ├── database.py
│   │   ├── detection_engine.py
│   │   ├── isolation_validator.py
│   │   ├── security.py
│   │   ├── soup_handlers.py
│   │   └── utils.py
│   ├── data\
│   │   ├── duckdb\
│   │   ├── logs\
│   │   ├── mitre_attack\
│   │   │   └── ttp_patterns.json
│   │   ├── models\
│   │   ├── rules\
│   │   │   └── detection_rules.json
│   │   ├── temp\
│   │   ├── threat_intel\
│   │   │   └── indicators.json
│   │   └── updates\
│   ├── docs\
│   │   ├── API_ENDPOINTS.md
│   │   ├── deployment_modes.md
│   │   ├── fetaures.md
│   │   ├── offline_training.md
│   │   └── progress_report.md
│   ├── routes\
│   │   ├── analysis.py
│   │   ├── health.py
│   │   ├── logs.py
│   │   ├── quorum_private.pem
│   │   ├── quorum_public.pem
│   │   └── soup.py
│   ├── scripts\
│   │   └── verify_offline_ready.py
│   ├── services\
│   │   ├── ai_engine.py
│   │   ├── collector_service.py
│   │   ├── parser_service.py
│   │   ├── report_service.py
│   │   └── storage_service.py
│   ├── utils\
│   │   └── key_generator.py
│   └── venv\
├── frontend\
│   ├── .gitignore
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── README.md
│   ├── vite.config.js
│   ├── public\
│   └── src\
├── PS with Solution\
└── training_model_code\
    ├── enhanced_training.py
    └── Quorum.ipynb
