# Ainstien Project: Complete Structured Overview

## 1. PROJECT SUMMARY

**Project Name:** Ainstien  
**Type:** Flask-based Web Application with Machine Learning Integration  
**Purpose:** Analyze company fundamental data and suggest potential trades for Swedish Mid-Cap stocks on Nasdaq Stockholm  
**Status:** Active Development  
**Python Version:** >=3.14  
**Package Manager:** uv (modern high-performance Python package manager)

---

## 2. TECHNOLOGY STACK

### Backend

- **Framework:** Flask 3.1.3
- **ORM:** SQLAlchemy 1.8.0 via Flask-SQLAlchemy 3.1.1
- **Database:** SQLite (company.db)
- **Data Processing:** Pandas 3.0.2
- **Machine Learning:** scikit-learn 1.8.0
- **API Integration:** yfinance 1.2.2 (live market data)
- **Environment Config:** python-dotenv 1.2.2
- **Data Parsing:** lxml 6.1.1

### Frontend

- **Template Engine:** Jinja2 (Flask default)
- **CSS Framework:** Bootstrap 5.3.0 (CDN)
- **Styling:** Custom CSS with design tokens and semantic classes
- **JavaScript:** Vanilla JavaScript (ES6+)
- **Charting:** Canvas API (prepared for integration)

### Infrastructure

- **Port:** 5001
- **Debug Mode:** Enabled for development
- **Database Location:** `/app/data/company.db`
- **Static Files:** `/app/client/static/`
- **Templates:** `/app/client/templates/`

---

## 3. FOLDER STRUCTURE & ARCHITECTURE

### Root Level

```
Ainstien/
├── pyproject.toml          # Project configuration (uv)
├── uv.lock                 # Exact package versions (DO NOT EDIT MANUALLY)
├── README.md              # Setup instructions
├── run.py                 # Application entry point
├── seed.py                # Database seeding script
├── app/                   # Main application package
├── data/                  # Database storage
└── seed_db/               # Database seed scripts
```

### `/app` - Application Package

The Flask app is organized using a **client-server separation pattern**:

```
app/
├── __init__.py            # Flask app factory (create_app function)
├── client/                # Frontend (templates + static assets)
│   ├── static/
│   │   ├── css/
│   │   │   ├── base.css              # Global styles
│   │   │   ├── dashboard.css
│   │   │   ├── company.css
│   │   │   ├── run_models.css
│   │   └── js/
│   │       ├── api.js                # Backend caller
│   │       ├── dashboard.js
│   │       ├── company.js
│   │       └── run_models.js
│   └── templates/        # HTML templates (Jinja2)
│       ├── base.html             # Master layout (navigation, footer)
│       ├── dashboard.html
│       ├── company.html
│       ├── run_models.html
│       └── trades.html
└── server/                # Backend API & business logic
    ├── database.py        # SQLAlchemy database initialization
    ├── db_queries.py      # Database query functions
    ├── live_market.py     # yfinance integration for real-time market data
    ├── routes.py          # Flask route handlers (endpoints)
    └── models/            # Machine learning models
        ├── fundamental_model.py
        ├── fundamental_ridge_model.py
        ├── metric_model.py
        ├── metric_ridge_model.py
        └── run_models.py               # Model executer
```

### `/data` - Database Storage

- **company.db:** SQLite database containing company fundamentals and metrics
- Created automatically on first run
- Populated by `seed.py` script using YahooFinance

### `/seed_db` - Database Seeding

- **seed_fundamentals.py:** Fetches and stores fundamental data
- **seed_metrics.py:** Calculates and stores financial metrics
- **seed_reports.py:** Generates historical reports

---

## 4. FRONTEND ARCHITECTURE (DETAILED)

### 4.1 Frontend Design Philosophy

The frontend follows a **layered, decoupled architecture**:

1. **API Layer (`api.js`):** Abstracts all HTTP communication to backend
2. **Logic Layer (`*.js`):** Page-specific business logic and DOM orchestration
3. **Presentation Layer (Templates + CSS):** View rendering and styling
4. **Design System (CSS tokens):** Consistent visual language across pages

### 4.2 Master Layout (base.html)

**Structure:**

- Global `<head>`: Bootstrap 5.3.0 CDN, base.css, page-specific CSS blocks
- Navigation bar: Dark custom navbar with links to Dashboard, Trades, ML Predictions, Run Models
- Flash message system: Bootstrap alerts for user feedback
- Footer: Copyright notice
- Script loading: Bootstrap JS, api.js (global), page-specific JS

**Key Features:**

- Uses Jinja2 template inheritance via `{% extends "base.html" %}`
- Block system for page-specific content, CSS, and scripts
- Responsive navbar with hamburger menu (Bootstrap toggle)
- Centralized navigation prevents duplication

### 4.3 API Client Layer (api.js)

**Purpose:** Single source of truth for all backend communication. Eliminates scattered fetch calls across pages.

**Core Functions:**

| Function                            | Endpoint                        | Method | Purpose                                                       |
| ----------------------------------- | ------------------------------- | ------ | ------------------------------------------------------------- |
| `fetchMarketSummary()`              | `/api/market-summary`           | GET    | Retrieves summary metrics for all companies (dashboard table) |
| `fetchMarketData(ticker)`           | `/api/market-data/{ticker}`     | GET    | Gets live market data, stock chart data, price, industry      |
| `fetchCompanyDetails(ticker)`       | `/api/company-details/{ticker}` | GET    | Fetches full fundamental history + company info               |
| `fetchCorrelationMatrix(features)`  | `/api/correlation`              | POST   | Computes correlation matrix for ML features                   |
| _(Additional ML endpoints planned)_ | _(Various)_                     | POST   | Model execution, predictions                                  |

**Error Handling:**

- Try-catch blocks for network errors
- HTTP status validation (`!response.ok`)
- Console logging for debugging
- Returns `null` on failure (graceful degradation)

**Configuration:**

- `const host = "/api";` — Centralized API base path
- All routes relative to `host` for easy environment switching

### 4.4 Page Implementation Pattern

All page-specific JS files follow this standardized pattern:

#### Dashboard (`dashboard.js`)

1. **Initialization Function:** `initDashboard()`
   - Calls `fetchMarketSummary()` from api.js
   - Handles loading states and errors
   - Updates status indicator badge
   - Renders company table rows

2. **Logic Functions:**
   - `displayCompanies(companies)` — Clears table, loops companies, builds rows
   - `createTableRow(company)` — Creates single `<tr>` DOM element with:
     - Ticker, Company Name, Revenue, EBIT
     - Dynamic color coding (quant-up/quant-down classes based on EBIT)
     - Analysis button linking to `/company/{ticker}`
   - `updateStatus(text, state)` — Updates badge with loading/success/error states

3. **Event Listeners:**
   - Row click handler: Navigates to company detail page if not clicking anchor
   - `DOMContentLoaded` event: Triggers `initDashboard()` when page loads

4. **Data Flow:**
   ```
   DOMContentLoaded → initDashboard() → fetchMarketSummary()
   → displayCompanies() → createTableRow() for each company
   ```

#### Company Detail (`company.js` & `company.html`)

1. **Template Structure:**
   - Hidden input stores ticker: `<input type="hidden" id="companyTicker" value="{{ ticker }}" />`
   - Header container (dynamically populated)
   - Market Performance Chart section (canvas ready)
   - Income Statement table (Income header styling)
   - Balance Sheet table (Balance header styling)

2. **Expected JavaScript Logic:**
   - Extract ticker from hidden input
   - Call `fetchCompanyDetails(ticker)` and `fetchMarketData(ticker)`
   - Render financial tables with historical data
   - Initialize canvas chart for price performance

3. **Styling:** Custom header classes (income-header, balance-header) for semantic color coding

### 4.5 CSS & Design System (base.css + page-specific CSS)

**Design Tokens (CSS Variables):**

```css
--ainstien-dark: #1a1d20 /* Dark navy for nav/text */ --ainstien-blue: #0056b3
  /* Primary action color */ --ainstien-success: #28a745
  /* Green for positive data */ --ainstien-danger: #dc3545
  /* Red for negative data */ --bg-global: #f4f7f6 /* Light bg for body */;
```

**Semantic CSS Classes:**

- `.quant-up` — Applied to positive metrics (green text)
- `.quant-down` — Applied to negative metrics (red text)
- `.status-fetching` — Badge state: loading spinner animation
- `.status-success` — Badge state: green success indicator
- `.status-error` — Badge state: red error indicator
- `.stock-row` — Table row with hover effects and transitions
- `.financial-data` — Table styling for consistency
- `.custom-navbar` — Navigation bar overrides
- `.custom-card-header` — Card headers with semantic subclasses (income-header, balance-header)

**Layout Principles:**

- Bootstrap 5.3.0 grid system (rows, cols)
- Card-based components with consistent shadows
- Responsive tables with `table-responsive` wrapper
- Right-aligned numerical columns (`text-end`)
- Clean spacing (mt-4, mb-5, py-3, px-3)

### 4.6 Page Routes & Navigation

| Route               | Template        | JS Logic              | Purpose                                          |
| ------------------- | --------------- | --------------------- | ------------------------------------------------ |
| `/`                 | —               | (Redirect)            | Redirects to `/dashboard`                        |
| `/dashboard`        | dashboard.html  | dashboard.js          | Market screener with company table               |
| `/company/<ticker>` | company.html    | company.js            | Company detail: fundamentals, charts, financials |
| `/run-models`       | run_models.html | run_models.js         | ML model execution interface                     |
| `/trades`           | trades.html     | (Not yet implemented) | Trading recommendations (placeholder)            |

### 4.7 Frontend Data Flow (Complete)

```
Browser Load (any page)
    ↓
Jinja2 renders base.html template
    ├→ Include Bootstrap CSS/JS from CDN
    ├→ Include base.css (global styles + design tokens)
    ├→ Include page-specific CSS block
    ├→ Render navigation bar
    ├→ Render {% block content %} (page-specific HTML)
    └→ Load api.js (global API client)

    ↓ (e.g., for dashboard)

JavaScript DOMContentLoaded event fires
    ↓
dashboard.js initDashboard() executes
    ├→ Calls api.js: fetchMarketSummary()
    ├→ GET /api/market-summary (backend processes, returns JSON)
    ├→ displayCompanies() loops through returned data
    ├→ createTableRow() creates each <tr> element
    ├→ Applies .quant-up or .quant-down class based on data
    ├→ Adds click listener to each row
    └→ updateStatus() changes badge to success state

User Interaction
    ├→ Hover on row → .stock-row CSS hover effect triggers
    ├→ Click row → Navigate to /company/{ticker}
    └→ Click Analysis button → Same navigation

Company Page Loads
    ├→ Jinja2 renders company.html with {{ ticker }} passed from routes.py
    ├→ HTML includes: hidden ticker input, chart canvas, income/balance tables
    ├→ company.js executes on DOMContentLoaded
    ├→ Extracts ticker from hidden input
    ├→ Calls api.js: fetchCompanyDetails(ticker) + fetchMarketData(ticker)
    ├→ GET /api/company-details/{ticker} and /api/market-data/{ticker}
    ├→ Populates tables and renders chart with returned data
    └→ Page displays full company analysis
```

### 4.8 Frontend Communication Protocol

**Request Format (all requests):**

```javascript
fetch(url, {
    method: "GET" or "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify(data) // For POST only
})
```

**Response Format (expected):**

```json
{
    "data": [...],
    "status": "success" or error details
}
```

**Error Handling Flow:**

1. Network error or `!response.ok` caught
2. Error logged to console
3. Function returns `null`
4. Calling page checks for null
5. Display error message or fallback UI
6. Update status badge if applicable

---

## 5. BACKEND ROUTES (API Endpoints)

### Standard HTML Routes (Page Serving)

- `GET /` — Redirects to dashboard
- `GET /dashboard` — Render dashboard.html
- `GET /company/<ticker>` — Render company.html with ticker parameter
- `GET /run-models` — Render run_models.html

### API Endpoints (JSON Data)

- `GET /api/market-summary` — Returns array of all companies with revenue, EBIT, ticker, name
- `GET /api/market-data/<ticker>` — Returns live market data (price, chart, industry) via yfinance
- `GET /api/company-details/<ticker>` — Returns fundamental history from database (income statement, balance sheet, metrics)

### Planned/Stub Endpoints

- `POST /api/correlation` — Compute correlation matrix for ML features
- Additional model execution endpoints (in development)

---

## 6. DATABASE STRUCTURE

**Database File:** `/app/data/company.db`  
**Engine:** SQLite  
**Initialization:** `db.create_all()` in `create_app()` factory function

**Tables (inferred from code):**

- **Companies:** Ticker, Name, Industry, other metadata
- **Fundamentals:** Revenue, EBIT, EBITDA, Net Income (historical records)
- **Balance Sheet:** Assets, Liabilities, Equity, Cash, Inventory, etc.
- **Metrics:** Calculated ratios and financial indicators

**Seeding Process:**

1. `seed.py` called manually by developer
2. Fetches data from SimFin API (requires `SIMFIN_API_KEY` in `.env`)
3. Populates company fundamentals into database
4. `seed_metrics.py` calculates derived metrics
5. `seed_reports.py` generates historical snapshots

---

## 7. DEVELOPMENT WORKFLOW

### First-Time Setup

```bash
# Install uv (once)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create environment and install dependencies
uv sync

# Activate environment
source .venv/bin/activate

# Seed the database
python seed.py

# Start the app
python run.py
```

### Running the Application

```bash
source .venv/bin/activate
python run.py
# Visit http://localhost:5001 in browser
```

### Adding Dependencies

```bash
# Use uv, not pip
uv add package_name
```

### After Git Pull

```bash
uv sync  # Sync uv.lock to ensure versions match
```

---

## 8. KEY FILES QUICK REFERENCE

| File                                  | Purpose                                                      |
| ------------------------------------- | ------------------------------------------------------------ |
| `run.py`                              | Entry point; creates Flask app and starts development server |
| `seed.py`                             | Database population script (manual run)                      |
| `app/__init__.py`                     | Flask app factory; configures database                       |
| `app/server/routes.py`                | Route handlers (page serving + API endpoints)                |
| `app/server/database.py`              | SQLAlchemy database initialization                           |
| `app/server/db_queries.py`            | Database query helper functions                              |
| `app/server/live_market.py`           | yfinance integration for market data                         |
| `app/server/models/*.py`              | Machine learning model implementations                       |
| `app/client/templates/base.html`      | Master template with navigation                              |
| `app/client/templates/dashboard.html` | Dashboard page template                                      |
| `app/client/templates/company.html`   | Company detail page template                                 |
| `app/client/static/js/api.js`         | Global API client functions                                  |
| `app/client/static/js/dashboard.js`   | Dashboard page logic                                         |
| `app/client/static/css/base.css`      | Global styles + design tokens                                |

---

## 9. KNOWN PATTERNS & CONVENTIONS

### Naming Conventions

- **Python:** snake_case for functions/variables, PascalCase for classes
- **JavaScript:** camelCase for functions/variables
- **CSS:** kebab-case for classes
- **Routes:** lowercase with hyphens (e.g., `/run-models`)

### File Organization

- Logic separated from presentation (MVC-influenced pattern)
- API client centralized (api.js) — no scattered fetch calls
- Page-specific assets (CSS/JS) co-located by feature
- Design tokens defined once in base.css

### Error Handling

- Frontend: `try-catch` blocks, console logging, graceful null returns
- Backend: Flask error handling (implied, expand if needed)
- User feedback: Bootstrap alert messages via Flask flash system

### Performance Considerations

- Bootstrap CDN for CSS/JS (no build step required)
- Vanilla JavaScript (no framework overhead)
- SQLite adequate for development; migration path for scaling

---

## 10. TECHNICAL DEBT & NOTES

- **trades.html & run_models.html:** Placeholder pages, logic not yet implemented
- **ML Model Endpoints:** API routes commented out or stubs, require backend implementation
- **Chart Library:** Canvas API ready but no charting library (Chart.js, Plotly) currently integrated
- **Authentication:** No user auth system implemented (development-only currently)
- **Error Boundaries:** Frontend error handling is basic; could be enhanced
- **Mobile Responsiveness:** Bootstrap provides baseline; test on actual devices

---

## 11. NEXT STEPS FOR NEW DEVELOPERS

1. **Understand the Flow:** Start with dashboard.html → dashboard.js → api.js → routes.py
2. **Run Locally:** Follow "First-Time Setup" in section 7
3. **Inspect Network:** Open DevTools (F12) → Network tab → trigger API calls to see real responses
4. **Review Database:** Query company.db directly or via db_queries.py to understand data structure
5. **Add Features:** Follow established patterns (template inheritance, centralized API calls, semantic CSS)
6. **Test Pages:** Each page should follow the dashboard.js pattern: fetch → display → error handling

---

## 12. ENVIRONMENT VARIABLES

**Required:**

- `SIMFIN_API_KEY` — SimFin API key for data fetching

**File Location:** `.env` in project root (not committed to git)

---

## 13. IMPORTANT COMMANDS REFERENCE

```bash
# Activate environment
source .venv/bin/activate

# Run app
python run.py

# Seed database
python seed.py

# Add package
uv add package_name

# Sync after git pull
uv sync

# Deactivate environment
deactivate
```

---

**Last Updated:** 2026-06-18  
**For Questions:** Refer to README.md or explore `/app` directory structure
