<div align="center">
  
  # 🏥 Diagnōsis
  
  ### *Secure Clinical Dataset Analytics & AI-Driven Cohort Narratives*
  
  [![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg?style=for-the-badge)](https://github.com/ranjeet22/diagnosis)
  [![License](https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge)](LICENSE)
  [![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![Gemini](https://img.shields.io/badge/Gemini_AI-8E75C2?style=for-the-badge&logo=google-gemini&logoColor=white)](https://deepmind.google/technologies/gemini/)

  <p align="center">
    A premium, clinical-grade data intelligence platform that ingests medical cohorts, maps variables onto standardized healthcare schemas, executes high-speed local data aggregations, and uses Google Gemini to generate isolated AI narratives.
  </p>

  ---

  <a href="https://diagnosis-frontend-fvg5.onrender.com">
    <img src="https://img.shields.io/badge/🚀_Launch_Live_Console-2563EB?style=for-the-badge&logoWidth=40" alt="Launch Live Console" />
  </a>
  &nbsp;&nbsp;
  <a href="https://github.com/ranjeet22/diagnosis">
    <img src="https://img.shields.io/badge/📂_Explore_Repository-0F172A?style=for-the-badge&logo=github&logoColor=white" alt="Explore Codebase" />
  </a>

  ---
</div>

## 🌟 Key Features

* **🛡️ HIPAA-Aligned Data Privacy**: Zero persistent database storage for patient logs. Clinical metrics and aggregates are computed entirely in-memory for secure analytics.
* **📊 Local DAG Aggregations Engine**: Instantly builds analytical filters, custom KPIs, and cross-variable comparison graphs (e.g., patient age cohorts vs. medical conditions).
* **🧠 Gemini-Powered Healthcare Ontology**: Resolves raw CSV column headers into standardized medical parameters and recommends tailored visualization charts.
* **💬 Conversational Cohort Insights**: Natural language query interface allowing users to "talk to their data" and extract isolated trends.
* **🎨 Fully Responsive Premium Design**: Modern workspace design with a sliding drawer navigation layout, customizable theme color schemes, and seamless light/dark modes.

---

## 🛠️ Technology Stack

<table align="center" width="100%">
  <tr>
    <td width="50%" align="center"><b>🖥️ Frontend (Vite App)</b></td>
    <td width="50%" align="center"><b>⚙️ Backend (FastAPI Server)</b></td>
  </tr>
  <tr>
    <td valign="top">
      <ul>
        <li><b>Framework:</b> React 19 + TypeScript</li>
        <li><b>Styling:</b> Tailwind CSS v4 + Vanilla Custom Themes</li>
        <li><b>Animations:</b> Framer Motion & Lottie-Web</li>
        <li><b>Routing:</b> React Router DOM</li>
        <li><b>Icons:</b> Lucide React</li>
      </ul>
    </td>
    <td valign="top">
      <ul>
        <li><b>Framework:</b> FastAPI (Python 3.12+)</li>
        <li><b>Data Processing:</b> Pandas</li>
        <li><b>AI Orchestration:</b> Gemini AI SDK (Header Authorization)</li>
        <li><b>Testing:</b> Pytest</li>
        <li><b>Server:</b> Uvicorn</li>
      </ul>
    </td>
  </tr>
</table>

---

## 📂 Project Structure

```text
diagnosis/
├── app/                        # FastAPI Application Package
│   ├── api/                    # API Routing and Controller Endpoints
│   │   └── v1/                 # API Version 1 Routers
│   ├── analytics/              # Local Analytics planning & execution engines
│   │   ├── executor/           # Aggregations, distribution, and trends engine
│   │   └── planner/            # Grid layout composition planner
│   ├── core/                   # System configurations and logger initializers
│   ├── schemas/                # Pydantic data schemas
│   └── services/               # Core business services (Ingestion, Planning, Chat)
├── frontend/                   # React Single Page Application (Vite project)
│   ├── src/
│   │   ├── components/         # Reusable UI components & layouts
│   │   ├── pages/              # Landing page and main Workspace console
│   │   └── index.css           # Styling directives and custom color systems
│   └── vite.config.ts          # Vite build config with watcher directives
├── requirements.txt            # Python dependencies
└── pyproject.toml              # Python project settings & poetry configuration
```

---

## 🚀 Getting Started

Follow these instructions to run the project locally on your machine.

### Prerequisites
* **Python 3.12+**
* **Node.js 18+**
* **Google Gemini API Key**

### 1. Backend Server Setup
Navigate to the root directory and create a `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000
```

Install the dependencies and boot the FastAPI dev server:
```bash
# Install packages
pip install -r requirements.txt

# Run server
python -m uvicorn app.main:app --port 8000 --reload
```
The server will start at `http://localhost:8000`. You can view interactive docs at `http://localhost:8000/docs`.

### 2. Frontend client Setup
Open a new terminal window, navigate to the `frontend/` directory, and install node packages:
```bash
cd frontend
npm install
```

Configure your Vite watcher if building on Windows to prevent `EBUSY` sync conflicts:
```bash
npm run dev
```
The client will start at `http://localhost:5173`.

---

## 🌐 Production Deployment

This project is optimized for deployment on **Render**:

1. **Backend Web Service**:
   * Build Command: `pip install -r requirements.txt`
   * Start Command: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
   * Environment Variable: `GEMINI_API_KEY` (Set your key)
2. **Frontend Static Site**:
   * Root Directory: `frontend`
   * Build Command: `npm run build`
   * Publish Directory: `dist`
   * **Rewrite Rule**: Redirect `/api/*` to `https://your-backend-api.onrender.com/api/*`

---

<div align="center">
  <p>Developed with ❤️ for secure medical analytics.</p>
</div>
