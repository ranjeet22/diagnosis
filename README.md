# Diagnōsis - AI-powered Healthcare Analytics and Decision Support Platform

Diagnōsis is an intelligent healthcare analytics platform designed for professionals, researchers, hospitals, public health organizations, and medical analysts. It allows users to upload structured healthcare datasets, cleans and analyzes the datasets deterministically, generates interactive dashboard configurations, and produces AI-generated insights.

---

## 🏛 Architecture & Tech Stack

This project is built using a **Deterministic AI Architecture** with a strict **Clean Architecture** layout. 

### Core Tech Stack
* **Language:** Python 3.12
* **Framework:** FastAPI (with Pydantic v2 & Pydantic Settings)
* **Storage:** Abstract Local / Google Cloud Storage (GCS)
* **Database/Warehousing:** BigQuery (for scalable analytical queries)
* **Data Processing:** cuDF / Pandas Fallback (GPU/CPU)
* **LLM Engine:** Gemini (cognitive explanations, Q&A, reporting)
* **Testing:** pytest

### Clean Architecture Layers

```text
               ┌────────────────────────┐
               │    Presentation (API)   │
               └───────────┬────────────┘
                           │ (Request / Response)
                           ▼
               ┌────────────────────────┐
               │      Application       │
               │  (Services / Schemas)  │
               └───────────┬────────────┘
                           │ (Business Logic)
                           ▼
               ┌────────────────────────┐
               │         Domain         │
               │   (Models / Entities)  │
               └────────────────────────┘
                           ▲
                           │ (Interfaces / DI)
               ┌───────────┴────────────┐
               │     Infrastructure     │
               │ (Storage / Repos / BQ) │
               └────────────────────────┘
```

1. **Presentation Layer (`app/api/`)**: Handles HTTP requests, CORS, serialization, request/response validation, and routing. No business logic resides here.
2. **Application Layer (`app/services/` & `app/schemas/`)**: Orchestrates use cases and business workflows.
3. **Domain Layer (`app/models/` & `app/exceptions/`)**: Contains core domain concepts, entities, and validation models.
4. **Infrastructure Layer (`app/storage/`, `app/database/`, `app/gemini/`)**: Integrates with external systems (filesystem, Google Cloud Storage, BigQuery, Gemini API).

---

## 📂 Folder Responsibilities

* `app/api/`: FastAPI routers and endpoints (v1 routes, health checks).
* `app/core/`: Central settings (Pydantic Settings), logging framework, and exception definitions.
* `app/middleware/`: CORS settings, custom request/response logging, and global exception mapping.
* `app/dependencies/`: Dependency injection providers for storage interfaces, repositories, and services.
* `app/storage/`: Storage abstractions (`StorageInterface`) and concrete drivers (Local, GCS).
* `app/database/`: Database/BigQuery connectivity wrapper.
* `app/gemini/`: LLM client wrappers for summaries, report writing, and cognitive agents.
* `app/services/`: Concrete implementations of core system flows (e.g. UploadService).
* `app/schemas/`: API validation schemas and internal data structures.
* `app/analytics/`: Deterministic statistics and aggregations engine (independent of LLM).
* `app/semantic/`: Data profiling and column mapping service.
* `app/dashboard/`: ECharts visualization configurations.
* `app/reporting/`: PDF/Excel/HTML report formatting.
* `app/agents/`: Cognitive/LLM agents for interactive Q&A and conversational analytics.
* `app/models/`: Internal structures and database schema mapping objects.
* `app/utils/`: Generic utility helpers.

---

## ⚙️ Development Workflow

### Prerequisites
* Python 3.12+
* Poetry

### Local Setup
1. **Clone the repository** and navigate to the project directory:
   ```bash
   cd Diagnōsis
   ```
2. **Copy the environment configuration**:
   ```bash
   cp .env.example .env
   ```
3. **Install dependencies** using Poetry:
   ```bash
   poetry install
   ```
4. **Run the local development server**:
   ```bash
   make run
   # OR: poetry run uvicorn app.main:app --reload --port 8000
   ```
5. **Run test suite**:
   ```bash
   make test
   ```

---

## 🔄 Dataset Lifecycle

The dataset ingestion pipeline flows as follows:

```text
 [Client Upload]
       │
       ▼
 [API Layer] ──────► Validate MIME type & file extension
       │
       ▼
 [Upload Service] ──► Parse encoding and delimiter (chardet & csv.Sniffer)
       │          ──► Compute rows, columns, and extract column headers
       │
       ▼
 [Storage Interface] ──► Write raw CSV file to Local/GCS storage
       │             ──► Write metadata.json to storage
       ▼
 [Return Response] ──► UUID and initial metadata structure
```

---

---

## 🔍 Analytics & Planning Lifecycle

The backend processes the uploaded datasets through a three-stage deterministic pipeline:

```text
[Dataset Uploaded] ──► original.csv + metadata.json
       │
       ▼
[Profiling Engine] ──► Heuristic logical type detection (EMAIL, ZIPCODE, DATE)
       │           ──► Mathematical statistics (mean, median, IQR outliers)
       │           ──► Saves profile.json
       ▼
[Semantic Mapping] ──► Mapped to medical ontology concepts (DISEASE, AGE, GENDER)
       │           ──► Detects clinical relationships (stays, demographics)
       │           ──► Saves semantic_model.json
       ▼
[Planning Engine]  ──► Configures KPIs, tasks, filters, and dashboard layout
                   ──► Builds Execution DAG (dependency nodes/edges)
                   ──► Saves analytics_plan.json
```

### 1. Intelligent Dataset Profiling Engine (Prompt 3)
Determines logical column types and metrics CPU/GPU duck-typed via cuDF/Pandas fallback.
* **Logical Type Detection**: Matches regex structures for `EMAIL`, `PHONE`, `ZIPCODE`, and standard parses for `DATE`, `DATETIME`, `TIME`, `BOOLEAN`, `INTEGER`, `FLOAT`, `CATEGORY`, `TEXT`.
* **Outlier Detection**: Extracts IQR limits (Lower bound = Q1 - 1.5 * IQR, Upper bound = Q3 + 1.5 * IQR) for numerical variables.
* **Quality Score**: Computes an overall cleanliness score based on missing values, outliers, duplicate rows, and type inconsistencies.

### 2. Healthcare Semantic Mapping Engine (Prompt 4)
Uses a deterministic mapping layer under `app/config/semantic/` to understand what each column represents without using an LLM.
* **Synonym Matcher**: Lowers headers and checks synonym dictionaries to map custom headings (e.g. `Visit_Date`, `bp`) to canonical terms (e.g. `ADMISSION_DATE`, `BLOOD_PRESSURE`).
* **Ontology Lookup**: Attaches clinical groups (Patient, Encounter, Vitals, Outcomes) and expected units.
* **Relationship Detector**: Automatically infers stay durations (`ADMISSION_DATE` + `DISCHARGE_DATE`) and cross-tab distributions (e.g., `AGE` + `DISEASE`).
* **Semantic Validation**: Rejects/flags models with conflicts or missing target variables.

### 3. Intelligent Analytics Planning Engine (Prompt 5)
Translates the semantic model and profile into a complete query execution blueprint. Does not execute the math itself; only maps the pipeline:
* **Analysis Rule Engine**: Generates required `AnalysisTask` definitions (e.g., Disease distribution, Age histograms, weekly admission trends) dynamically based on mapped columns.
* **KPI Planner**: Resolves high-level overview metrics (e.g., Recovery Rate, Unique Diagnoses, Patient Count, Stay Averages) detailing computational formulas and priorities.
* **Visualization Planner**: Configures ECharts suggestion parameters (chart families like Bar/Line/Pie/Box Plot, recommended grid sizes, placements, and click interactions).
* **Aggregation Planner**: Maps unique aggregations (Average, Median, Distinct Count, Growth Rate, Moving Average) to columns.
* **Priority Engine**: Computes priority ratings using weighted criteria:
  $$\text{Priority Score} = \text{Business Value Weight} (40.0\text{ max}) + \text{Vis Importance Weight} (40.0\text{ max}) + \text{Confidence} \times 20.0 - \text{Cost Penalty}$$
* **Execution Graph**: Builds a Directed Acyclic Graph (DAG) mapping task execution order to avoid redundant aggregations.
* **Downstream Execution**: Future modules will consume `analytics_plan.json`, traverse the Execution Graph using topological sorting, run the aggregations on GPU/CPU, and render the recommended charts inside the themed sections on the dashboard layout.

---

---

## ⚡ Analytics Execution Lifecycle (Prompt 6)

The **Analytics Execution Engine** is the computational heart of Diagnōsis. It executes the Directed Acyclic Graph (DAG) analytics blueprint generated in `analytics_plan.json` deterministically, caching intermediate results in memory and outputting a standardized results JSON.

```text
[analytics_plan.json] ──► Read execution graph and planned tasks
         │
         ▼
[Topological Sort]   ──► Sort tasks to satisfy dependency ordering
         │
         ▼
[Execution Engine]   ──► Vectorized runs (cuDF with CPU pandas fallback)
         │           ──► Shared in-memory intermediate cache
         ▼
[Results Generator]  ──► Compiles KPIs, trends, comparisons, and correlations
         │
         ▼
[analytics_results.json] ──► Saved to disk for downstream dashboards
```

### 1. Execution Flow & DAG Orchestration
* **Topological Dependency Resolution**: Traverses task nodes topologically using Kahn's algorithm, ensuring parent calculations (like daily counts) execute before dependent nodes (like weekly rolling averages or growth trends).
* **Caching Strategy**: Maintains an in-memory cache of intermediate Series/DataFrames. For example, if both `top_diseases` and `disease_ranking` need the disease value counts, the engine runs the distribution once, stores it in the cache, and serves the subsequent requests instantly.
* **Vectorized Data Handling**: All calculations (aggregations, box-plot percentiles, cross-tabulations, growth rates, rolling windows) are fully vectorized using Pandas/cuDF CPU-GPU duck-typed operations to support hundreds of thousands of rows efficiently without Python loops.

### 2. Analytical Calculations & Engines
* **KPI Engine**: Computes high-level overview metrics (e.g. Unique Diagnoses, Patient Count, Average/Median Age, Average Stay Duration, and Recovery/Mortality Rates based on clinical status keywords).
* **Distribution Engine**: Computes label counts and percentages for categorical variables, including standard age bracket binning (0-18, 19-35, 36-50, 51-65, 65+) driven dynamically by `age_groups.json`.
* **Trend Engine**: Analyzes timeline workloads into daily, weekly, monthly, quarterly, and yearly trends, and computes rolling averages, running totals, interval growth rates, and seasonality metadata (e.g., peak weekdays/months).
* **Comparison Engine**: Performs multi-variable comparisons. Generates cross-tabulation matrices for categorical pairs and computes 5-number box-plot numeric stats (min, Q1, median, Q3, max) grouped by category.
* **Correlation Engine**: Computes Pearson and Spearman correlation matrices across numeric metrics (vitals like heart rate, temperature, age, BMI) and extracts strong positive (> 0.70), strong negative (< -0.70), and weak relationships.
* **Metric Calculator**: Assesses overall quality stats, compiling completeness indexes, duplicate counts, outlier densities, consistency indexes, and validity scores.

### 3. Downstream Dashboard Consumption
The output results are saved as **`analytics_results.json`** inside the dataset's storage directory. Subsequent dashboard generators, report builders, and conversational AI agents will load this file directly to render charts and write summaries instantly, ensuring zero database recalculations during user interactions.

---

---

## 🎨 Visualization Recommendation Lifecycle (Prompt 7)

The **Visualization Recommendation Engine** processes the analytical findings from `analytics_results.json` and produces **`visualization_plan.json`**. This layout configures ECharts series variables, legends, tooltips, grid responsiveness, and W3C accessibility compliance parameters.

```text
[analytics_results.json] ──► Consume counts, averages, and comparisons
         │
         ▼
[Chart Recommendation]  ──► Map ECharts types (Bar, Pie, Line, Heatmap, Boxplot)
         │
         ▼
[Theme & Palette Engine]──► Choose Medical Blue, Green, or Colorblind palettes
         │
         ▼
[Accessibility Engine]  ──► Compile dynamic ARIA labels and detailed alt-text
         │
         ▼
[visualization_plan.json]──► Saved to disk for downstream frontend rendering
```

### 1. Selection Rules & Engines
* **Chart Recommendation Engine**: Translates data shapes into standard visual types:
  * Categorical lists ($\le 6$ values) $\rightarrow$ **Pie Chart** (proportional distribution).
  * Categorical lists ($> 6$ values) $\rightarrow$ **Horizontal Bar Chart** (to prevent label overlap).
  * Standard distributions $\rightarrow$ **Vertical Bar Chart**.
  * Chronological dates $\rightarrow$ **Line Chart / Area Chart** (timeline trends).
  * Numeric comparisons $\rightarrow$ **Box Plot**.
  * Multi-variable numeric groups $\rightarrow$ **Scatter Plot**.
  * Correlation Matrix $\rightarrow$ **Heatmap**.
* **Color Palette & Theme Engine**: Handles layout styles (Light, Dark, High-Contrast, Print) and applies contrast-compliant palettes (Medical Blue, Medical Green, Color Blind Friendly Okabe-Ito, High Contrast).
* **Layout Recommendation Engine**: Maps screen width weights (e.g. 25% for KPI cards, 50% for standard charts, 100% for timeline trends), row/col indices, and display categories (Overview, Clinical Analyses, Demographics, Temporal Trends).
* **Interaction Planner**: Configures user event attributes like timeline zooming, brush-selecting, cross-filtering, and resets.

### 2. Accessibility & ARIA Support
* **Dynamic Alt Text generator**: Automatically extracts maximum and minimum values from the computed results to generate alt-text summaries, for example:
  > *"Bar chart displaying caseload frequencies of Disease Distribution across 3 categories. Flu has the highest volume with 3 records (60.0%), while Cold represents the minimum volume with 1 records (20.0%)."*
* **WCAG Compliance**: Enforces keyboard navigation tags and maps color contrast ratios (e.g., $7.0$ for high contrast, $4.5$ for default light theme).

### 3. Downstream Dashboard consumption
The output configuration **`visualization_plan.json`** is saved inside the dataset's storage directory. Future dashboard client engines load this file directly to construct ECharts datasets, legends, and series series arrays, ensuring absolute decoupling of business logic from frontend layout rendering code.

---

## 🖥 Dashboard Composition Lifecycle (Prompt 8)

The **Dashboard Composition Engine** combines the visual mappings in `visualization_plan.json` with the semantic variables of `semantic_model.json` to generate **`dashboard.json`**. This document serves as the layout and state contract for the frontend rendering framework.

```text
[visualization_plan.json] ──► Read widget layouts and visual recomendations
         │
         ▼
[Dashboard Builder]      ──► Group widgets into pages and sections
         │
         ▼
[Layout Grid Engine]     ──► Allocate coordinates (desktop, tablet, mobile)
         │
         ▼
[Validation Service]     ──► Validate widget IDs, bounds, and references
         │
         ▼
[dashboard.json]         ──► Saved to disk for direct frontend rendering
```

### 1. Page & Section Grouping
* **Dashboard Pages**: Automatically structures the layout into multiple distinct pages:
  * `Overview`: Overall clinical summary cards (KPI Cards) and main timeline workloads.
  * `Demographics`: Age binnings and gender shares.
  * `Disease Analytics`: Clinical prevalences and diagnosis caseload rankings.
  * `Hospital Analytics`: Stay durations and admission counts.
  * `Trend Analysis`: Multi-line timeline workload moving averages.
  * `Regional Analysis`: Location zipcodes comparison matrices.
  * `Data Quality`: Ingestion scorecards and field completeness metrics.
* **Dashboard Sections**: Pages are segmented into section cards (e.g. `Prevalence & Caseloads`) containing collections of widgets. Empty pages are automatically omitted to keep the dashboard view clean.

### 2. Grid Sizing & Filters
* **Layout Grid Engine**: Uses a standard **12-column responsive layout** to map coordinate configurations:
  * **Desktop**: KPI cards span 3 columns (4 per row); medium charts span 6 columns (2 per row); large timeline trends span 12 columns (full row).
  * **Tablet**: KPI cards span 6 columns (2 per row); charts span 12 columns.
  * **Mobile**: All widgets stack vertically (width 12).
  * Stateful cursors prevent overlaps and wrap columns automatically.
* **Global Filter Architecture**: Maps dataset variables into dropdown sidebar filters (Age Cohorts, Gender, Facility Hospital, Diagnosis, Zipcode / Region, Outcome Status, Timeline Period). Each widget declares supported and ignored filters (to prevent self-filtering on primary category columns).

### 3. Frontend Rendering via React & Apache ECharts
The frontend consumes `dashboard.json` directly to construct layouts and widgets:
* **Layout Rendering**: React layout managers (such as Grid or Flexbox) parse the widget coordinates to render responsive card components.
* **Chart Rendering**: Widgets pass their pre-formatted `chart_config` directly to Apache ECharts instances, injecting custom color palettes and tooltips.
* **Export & Customization**: The React client handles downloading formats (PNG, PDF, CSV, JSON, Excel) and layout modifications (moving, hiding, resizing, renaming cards) using the metadata properties stored in `dashboard.json`.

---

## 🧠 AI Insight Generation Engine (Prompt 9)

The **AI Insight Generation Engine** translates raw, deterministic analytics results into professional, medical natural-language insights. It isolates the AI layer from calculations, keeping the analytical computations completely deterministic.

```text
[analytics_results.json] ──► Summarize and filter metrics
          │
          ▼
[Insight Context Builder] ──► Compress data into structured token-efficient payload
          │
          ▼
[Prompt Builder]         ──► Render system personas and instructions templates
          │
          ▼
[Gemini Client / API]    ──► Structured generation (application/json MIME type)
          │
          ▼
[Validation Service]     ──► Validate JSON output properties and schemas
          │
          ▼
[insights.json]          ──► Saved to disk for downstream medical reports
```

### 1. Privacy & Security: Why Raw Datasets Are Never Sent
* **HIPAA & Privacy Compliance**: Raw healthcare CSV data columns containing patient names, medical history records, or individual identifiers are **never sent to Gemini**.
* **Token Optimization & Cost**: Individual patient lists can easily span thousands of rows, leading to large token consumption and excessive costs.
* **Deterministic Aggregations**: The backend acts as a strict summarization layer, sending only aggregated medical counts, high-level demographic distributions, time-series intervals, correlation coefficient lists, and data quality metrics to the LLM.

### 2. Prompt Template Engineering & Versioning
* **Prompt Configuration**: Prompts are stored and managed inside a structured JSON file `app/config/prompts/insight_prompts.json`.
* **Persona Constraints**: System templates instruct Gemini to act as a senior medical statistician. Persona guidelines strictly forbid fabricating statistics, speculating on missing variables, or drawing conclusions not backed by deterministic evidence.
* **Response Formatting**: Configures Gemini to return a structured JSON response conforming exactly to the Pydantic schemas, mapping the executive summaries and observation arrays.

### 3. Retry Strategy & Robust Cache Layer
* **Rate Limits & Throttling**: Implements `RetryManager` supporting exponential backoff. If a rate limit block (HTTP 429) or network timeout is encountered, the call automatically retries with progressive sleeping delays.
* **Graceful Fallbacks**: If the external Gemini API is unreachable or fails repeatedly, the system automatically falls back to a local pre-compiled **Deterministic Insights Generator**. This generator creates standard observations from the context variables, guaranteeing that endpoints never fail.
* **Cache Management**: Persists results inside `insights.json`. If requests are made subsequently and `analytics_results.json` has not changed (verifying timestamps), the engine bypasses Gemini entirely.

---

## 💬 Conversational Analytics & LLM Intent Router (Prerequisite)

Before exposing a conversational chatbot, Diagnōsis routes natural language questions through a semantic **LLM Intent Router** which translates user inputs into structured query filters and actions. This design decouples semantic query parsing from execution, preventing hallucinations and preserving 100% deterministic mathematical calculations.

```text
User Question: "Show me the top 5 diseases among females over 60."
          │
          ▼
[Intent Router (LLM)]   ──► Parses query into structured intent parameters:
                            {
                              "action": "FILTER_AND_RANK",
                              "filters": {"gender": "Female", "age": ">60"},
                              "group_by": "disease",
                              "limit": 5
                            }
          │
          ▼
[Intent Executor (DF)]  ──► Executes filters and rankings deterministically on DataFrame
          │
          ▼
[Gemini Explanation]    ──► Translates calculated data records into clinical explanation narrative
          │
          ▼
Conversational Response ──► Returns query, structured intent, execution details, and clinical summary
```

### 1. Intent Action Classification
* **`KPI_QUERY`**: Routes requests targeting pre-compiled dashboard Key Performance Indicators (e.g. "Total Records", "Average Stay"). Looks up the values directly in `analytics_results.json` to ensure consistency.
* **`FILTER_AND_RANK`**: Routes complex filtered queries. Captures comparison operators (e.g. `>`, `<`, `<=`, `>=`, `=`), applies groupings, metric operations (count, average, sum, min, max), sorts, and slices records.
* **`TIME_TREND`**: Routes requests looking for chronological workloads and time series.
* **`GENERAL_EXPLANATION`**: Routes open-ended explanation requests (e.g. "why did Flu caseloads spike?").

### 2. Agnostic Semantic Mappings
* The **Intent Router** prompt is injected with active dataset semantic column metadata (column keys and semantic types) and planned KPIs. This forces Gemini to map filters to exact dataset keys (e.g. mapping "females" to `gender == Female`, and "diseases" to `group_by = disease`), preventing hallucinated columns.
* Parses prefix filter comparison operations (e.g. `age > 60` or `gender == F`) and executes them on the pandas DataFrame.

### 3. Graceful Narrative Explanations
* The query execution outcomes are fed back to Gemini to explain the results in a 2-3 sentence professional clinical summary referencing exact calculated counts and rates. If the API key is not set or rate limits are reached, the service falls back to a deterministic fallback describer.

---

## 🔮 Extending the Project in Future Prompts

This project layout is highly decoupled to allow seamless expansion:

1. **Adding Google Cloud Storage (GCS)**:
   * Implement the `StorageInterface` in `app/storage/gcs.py` implementing Google Cloud SDK methods.
   * Update `app/dependencies/storage.py` to return the `GCSStorageProvider` when `STORAGE_TYPE=gcs`.
2. **Adding BigQuery Integration**:
   * Implement DB clients under `app/database/` and inject them via `app/dependencies/db.py`.
3. **Conversational Chatbot Interface**:
   * Build the UI chatbot component consuming the `/api/v1/datasets/{dataset_id}/query` endpoint.
4. **React Frontend Integration**:
   * Build the UI dashboard component consuming the `/api/v1/datasets/{dataset_id}/dashboard` config file.
