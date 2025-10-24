# Frontend Report

This document provides a detailed overview of the frontend codebase, including component-wise working, frontend-backend integration, component interactions, folder structure, running instructions, and features.

## 1. Folder Structure

The frontend folder is structured as follows:

```
frontend/
├── .gitignore
├── eslint.config.js
├── index.html
├── package-lock.json
├── package.json
├── postcss.config.cjs
├── README.md
├── tailwind.config.cjs
├── vite.config.js
└── src/
    ├── App.jsx
    ├── index.css
    ├── main.jsx
    ├── assets/
    │   └── react.svg
    ├── components/
    │   ├── common/
    │   │   ├── Badge.jsx
    │   │   ├── Badge.module.css
    │   │   ├── Button.jsx
    │   │   ├── Button.module.css
    │   │   ├── Card.jsx
    │   │   ├── Card.module.css
    │   │   ├── Modal.jsx
    │   │   └── Modal.module.css
    │   ├── dashboard/
    │   │   ├── ActivityFeed.jsx
    │   │   ├── ActivityFeed.module.css
    │   │   ├── StatCard.jsx
    │   │   ├── StatCard.module.css
    │   │   ├── ThreatChart.jsx
    │   │   └── ThreatChart.module.css
    │   ├── layout/
    │   │   └── Sidebar.jsx
    │   ├── threats/
    │   │   ├── ThreatCard.jsx
    │   │   └── ThreatCard.module.css
    │   └── ui/
    │       ├── badge.jsx
    │       ├── button.jsx
    │       ├── card.jsx
    │       ├── dialog.jsx
    │       ├── input.jsx
    │       ├── select.jsx
    │       └── toaster.jsx
    ├── data/
    │   └── mockData.js
    ├── lib/
    │   └── utils.js
    ├── pages/
    │   ├── Dashboard.jsx
    │   ├── Dashboard.module.css
    │   ├── LogCollection.jsx
    │   ├── LogCollection.module.css
    │   ├── Reports.jsx
    │   ├── Reports.module.css
    │   ├── SoupUpdates.jsx
    │   ├── SoupUpdates.module.css
    │   ├── SystemStatus.jsx
    │   ├── SystemStatus.module.css
    │   ├── ThreatAnalysis.jsx
    │   └── ThreatAnalysis.module.css
    ├── styles/
    │   └── theme.css
    └── utils/
        ├── api.js
        ├── enums.js
        └── formatters.js
```

## 2. Running Instructions

To run the frontend application, follow these steps:

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install the dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
4.  Open your browser and navigate to `http://localhost:5173` (or the address shown in the terminal).

## 3. Features

The frontend application provides the following features:

*   **Dashboard:** An overview of the system's status, including statistics and recent activity.
*   **Log Collection:** A user interface for collecting logs from various sources.
*   **Threat Analysis:** A view for analyzing threats and anomalies.
*   **Reports:** A section for generating and viewing reports.
*   **SOUP Updates:** A mechanism for applying Secure Offline Update Protocol (SOUP) packages.
*   **System Status:** A page for monitoring the health and isolation status of the system.

## 4. Component-wise Working and Interaction

The frontend is built using React and Vite. It uses a component-based architecture, with components organized into `common`, `dashboard`, `layout`, `threats`, and `ui` directories.

### 4.1. `App.jsx`

This is the main component of the application. It sets up the routing using `react-router-dom` and renders the `Sidebar` and the main content area.

### 4.2. `components/layout/Sidebar.jsx`

The `Sidebar` component provides navigation to the different pages of the application.

### 4.3. `pages/`

This directory contains the main pages of the application:

*   **`Dashboard.jsx`:** Displays a dashboard with statistics and charts. It uses the `StatCard`, `ThreatChart`, and `ActivityFeed` components.
*   **`LogCollection.jsx`:** Provides a UI for uploading and collecting logs.
*   **`ThreatAnalysis.jsx`:** Displays a list of threats using the `ThreatCard` component.
*   **`Reports.jsx`:** Allows users to generate and view reports.
*   **`SoupUpdates.jsx`:** Provides a UI for applying SOUP updates.
*   **`SystemStatus.jsx`:** Displays the system's health and isolation status.

### 4.4. `components/`

This directory contains reusable components:

*   **`common/`:** Contains basic UI components like `Badge`, `Button`, `Card`, and `Modal`.
*   **`dashboard/`:** Contains components specific to the dashboard, such as `ActivityFeed`, `StatCard`, and `ThreatChart`.
*   **`threats/`:** Contains components for displaying threat information, such as `ThreatCard`.
*   **`ui/`:** Contains more complex UI components like `badge`, `button`, `card`, `dialog`, `input`, `select`, and `toaster`.

### 4.5. `utils/`

This directory contains utility files:

*   **`api.js`:** This file is responsible for all communication with the backend API. It uses the `axios` library to make HTTP requests.
*   **`enums.js`:** Contains enumerations for various constants used in the application.
*   **`formatters.js`:** Contains functions for formatting data, such as dates and numbers.

## 5. Frontend-Backend Integration

The frontend and backend are connected via a REST API. The frontend uses the `axios` library (configured in `utils/api.js`) to make HTTP requests to the backend.

The backend is a FastAPI application that exposes several endpoints. The frontend interacts with these endpoints to fetch data, trigger actions, and update the UI.

Here's a mapping of the main frontend components to the backend endpoints they interact with:

| Frontend Component | Backend Endpoint(s) | Description |
| --- | --- | --- |
| `Dashboard.jsx` | `/logs/status` | Fetches statistics for the dashboard. |
| `LogCollection.jsx` | `/logs/upload`, `/logs/collect`, `/logs/collect/directory`, `/logs/collect/ssh`, `/logs/collect/winrm`, `/logs/collect/network`, `/logs/collect/usb`, `/logs/collect/usb/detect` | Handles log collection from various sources. |
| `ThreatAnalysis.jsx` | `/analysis/analyze/comprehensive` | Triggers a comprehensive analysis of the logs. |
| `Reports.jsx` | `/reports/export/csv`, `/reports/export/pdf` | Exports reports in CSV and PDF formats. |
| `SoupUpdates.jsx` | `/soup/update`, `/soup/status`, `/soup/history`, `/soup/rollback` | Manages SOUP updates. |
| `SystemStatus.jsx` | `/health/`, `/health/isolation` | Fetches system health and isolation status. |

The `utils/api.js` file centralizes all the API calls, making it easy to manage and update the frontend-backend communication.
