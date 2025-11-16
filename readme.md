# Trip Planner Agent - AI-Powered Travel Itinerary Generator

A full-stack AI-powered travel itinerary planner built with LangGraph, OpenAI, and React. The system uses an agentic workflow to plan, research, generate, and refine travel itineraries through multiple revision cycles.

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Running the Project](#running-the-project)
- [API Endpoints](#api-endpoints)
- [Workflow](#workflow)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Development Notes](#development-notes)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────┐
│   React Frontend (Port 3000)    │
│   - Chat Interface              │
│   - Plan/Draft/Critique Tabs    │
│   - State History               │
└────────────────┬────────────────┘
                 │ HTTP/CORS
                 ▼
┌─────────────────────────────────┐
│   Flask Backend (Port 5000)     │
│   - REST API                    │
│   - Streaming NDJSON endpoints  │
│   - Thread management           │
└────────────────┬────────────────┘
                 │ Uses
                 ▼
┌─────────────────────────────────┐
│   LangGraph Agent               │
│   - NodePipeline (5 nodes)      │
│   - State checkpointing         │
│   - Memory-based threads        │
└────────────────┬────────────────┘
                 │ Calls
                 ▼
┌─────────────────────────────────┐
│   External APIs                 │
│   - OpenAI (gpt-4)              │
│   - Tavily (web search)         │
└─────────────────────────────────┘
```

---

## 🔧 Backend Setup

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Python | 3.10+ |
| **Framework** | Flask | 2.x |
| **Agent Framework** | LangGraph | 0.1+ |
| **LLM** | OpenAI (gpt-4) | Latest |
| **Search** | Tavily API | - |
| **State Management** | MemorySaver | LangGraph built-in |
| **CORS** | Flask-CORS | 4.x |

### Backend Technologies & Purpose

- **Flask**: Lightweight REST API server; serves /api/* endpoints for frontend consumption.
- **LangGraph**: Orchestrates multi-step agentic workflow (plan → research → generate → critique → refine).
- **OpenAI ChatOpenAI**: Powers LLM reasoning and content generation at each node.
- **Tavily Search**: Fetches real-time travel information (flights, hotels, attractions).
- **MemorySaver**: Stores conversation history and thread state in-memory; supports branching and rollback.
- **Flask-CORS**: Enables cross-origin requests from frontend.

### Backend Directory Structure

```
d:\MCP\agent-backend\
├── app.py                      # Flask server, streaming endpoints, thread mgmt
├── requirements.txt            # Python dependencies
├── .env                        # API keys (OPENAI_API_KEY, TAVILY_API_KEY)
└── src/
    ├── builder.py              # Graph builder; compiles LangGraph workflow
    ├── node_pipeline.py        # 5 agent nodes (plan, research, generate, critique, reflect)
    ├── agent_state.py          # AgentState TypedDict; defines shared state schema
    └── utils/
        ├── prompts.py          # System & user prompts for each node
        ├── tools.py            # Tool definitions (search, web scrape, etc.)
        └── helpers.py          # Utility functions (parsing, formatting)
```

### Backend Workflow

**5-Node Agentic Loop:**

1. **Planner Node** → Takes user task (trip request) and generates an initial structured plan.
2. **Research Plan Node** → Formulates web search queries based on the plan.
3. **Generation Node** → Writes a detailed draft itinerary using plan + research answers.
4. **Reflection Node** → Critiques the draft (tone, coverage, feasibility, missing details).
5. **Research Critique Node** → Researches critique feedback and generates final refined itinerary.

**State Machine Flow:**
- Loops up to `max_revisions` times (default: 2).
- Conditional edge: if critique is positive → END; else → loop back to Generation.
- Thread-based conversation memory with checkpointing.
- Each iteration creates a new snapshot in state history.

---

## 🎨 Frontend Setup

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | TypeScript | 5.x |
| **Framework** | React | 17.0.2 |
| **Router** | react-router-dom | 6.x |
| **Build Tool** | Webpack (via react-scripts) | 5.x |
| **HTTP Client** | Axios | Latest |
| **Styling** | CSS3 | - |

### Frontend Technologies & Purpose

- **React**: Component-based UI; manages local state (messages, thread history, selected states).
- **TypeScript**: Type-safe frontend code; catches errors at compile time.
- **Axios**: HTTP client; abstracts API calls to backend with error handling and streaming support.
- **react-router-dom v6**: Client-side routing (ready for multi-page expansion).
- **Webpack (react-scripts)**: Bundler; compiles TSX/CSS and manages dev server with hot reload.

### Frontend Directory Structure

```
d:\MCP\agent-gui-react\
├── public/
│   └── index.html              # Entry point
├── src/
│   ├── App.tsx                 # Root component
│   ├── index.tsx               # React DOM render
│   ├── components/
│   │   ├── ChatWindow.tsx       # Main chat UI; streams agent output
│   │   ├── PlanDisplay.tsx      # Tab: shows/edits plan
│   │   ├── ResearchPanel.tsx    # Tab: shows research queries/answers
│   │   ├── DraftPanel.tsx       # Tab: shows/edits draft itinerary
│   │   └── CritiquePanel.tsx    # Tab: shows/edits critique feedback
│   ├── services/
│   │   └── agentService.ts      # API calls (fetch/axios); streaming handler
│   ├── types/
│   │   └── index.ts            # TypeScript interfaces (AgentState, Message, etc.)
│   ├── hooks/
│   │   └── useAgentRunner.ts    # Custom hook; manages agent invocation & streaming
│   └── styles/
│       └── App.css             # Global styles
├── package.json                # Dependencies; build scripts
├── tsconfig.json               # TypeScript config
├── .env.local                  # REACT_APP_API_BASE_URL=http://localhost:5000
└── build/                      # (Generated after npm run build)
```

### Frontend Workflow

1. **User Input** → Types travel request in ChatWindow.
2. **Send to Backend** → Calls agentService.planVacation() → POST /api/stream-run.
3. **Stream NDJSON** → Backend yields JSON lines (partial, lnode, nnode, thread_id, revision_number, count).
4. **Update UI** → ChatWindow appends messages; tabs refresh with plan/draft/critique state.
5. **Thread History** → User can select prior states from dropdown; backend loads checkpoint.
6. **Modify & Retry** → Edit plan/draft/critique and re-invoke node with modified state.

---

## 🚀 Running the Project

### Prerequisites

- **Python 3.10+** installed and in PATH.
- **Node.js 18.x or 22.x** (with npm); if Node 22, use legacy OpenSSL provider.
- **API Keys**: OPENAI_API_KEY and TAVILY_API_KEY in `.env` file.
- **Git** (optional, for cloning).

### Backend Setup & Run

```powershell
# Navigate to backend directory
cd d:\MCP\agent-backend

# Create virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Ensure .env has API keys
# OPENAI_API_KEY=sk-...
# TAVILY_API_KEY=tvly-...
# MODEL=gpt-4
# PORT=5000

# Run Flask server
python app.py

# Expected output:
# * Serving Flask app 'app'
# * Running on http://127.0.0.1:5000
# Press CTRL+C to quit
```

### Frontend Setup & Run

```powershell
# Navigate to frontend directory
cd d:\MCP\agent-gui-react

# Install Node dependencies
npm install

# Install specific router version (if not already done)
npm install react-router-dom@6

# Create .env.local file
echo "REACT_APP_API_BASE_URL=http://localhost:5000" | Out-File -Encoding UTF8 .env.local

# For Node 22.x: set legacy OpenSSL provider
$env:NODE_OPTIONS="--openssl-legacy-provider"

# Start development server
npm start

# Expected output:
# Compiled successfully!
# You can now view agent-gui-react in the browser.
# Local: http://localhost:3000
```

### Verify Both Are Running

**Backend Health Check:**
```powershell
Invoke-RestMethod http://localhost:5000/health
# Expected response: { "status": "ok", "api": "agent-backend" }
```

**Frontend Access:**
- Open http://localhost:3000 in your browser.

**API Test (PowerShell):**
```powershell
$body = @{ task = "Plan a 3-day trip to Paris" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://localhost:5000/api/plan" `
  -Body $body -ContentType "application/json"
```

---

## 📡 API Endpoints

### Main Streaming Endpoint

**POST /api/stream-run**
- Streams NDJSON (newline-delimited JSON) output of agent execution.
- Request body:
  ```json
  {
    "task": "Plan a 5-day trip to Japan",
    "stop_after": ["planner", "research_plan"],
    "start": true,
    "max_iterations": 2
  }
  ```
- Response (each line is JSON):
  ```json
  {
    "partial": "Agent output so far...",
    "lnode": "planner",
    "nnode": "research_plan",
    "thread_id": 0,
    "revision_number": 1,
    "count": 3
  }
  ```

### REST Endpoints (for backward compatibility)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/plan | Generate initial plan |
| POST | /api/research | Research a plan |
| POST | /api/generate | Generate draft from plan |
| POST | /api/critique | Critique a draft |
| POST | /api/research-critique | Refine based on critique |
| GET | /api/get-state?thread_id=X | Fetch state of a thread |
| GET | /api/get-state-history?thread_id=X | Fetch history of a thread |
| GET | /health | Health check |
| GET | / | API info |

---

## 🔄 Workflow (End-to-End)

### Example: User Plans a Trip

1. **User enters**: "Plan a 5-day trip to Japan in October, I want to make friends."
2. **Frontend calls**: POST /api/stream-run with task, start=true.
3. **Backend execution**:
   - **Planner Node**: "Here's a 5-day itinerary focusing on social activities in Tokyo, Kyoto, and Osaka..."
   - **Research Node**: Searches for:
     - "Japan October weather and attractions"
     - "Tokyo social activities and meetup events"
     - "Best budget-friendly hostels in Japan"
   - **Generation Node**: Writes detailed itinerary with dates, spots, estimated costs, transportation.
   - **Reflection Node**: "The itinerary is comprehensive but lacks specific restaurant recommendations and local cultural insights."
   - **Critique Research**: Searches for:
     - "Top restaurants in Tokyo, Kyoto"
     - "Local cultural experiences Japan"
   - **Final Refinement**: Updates itinerary with restaurant details and cultural activities.
4. **Frontend streams** each step and updates tabs (Plan, Draft, Critique).
5. **User can**:
   - View final itinerary in ChatWindow.
   - Edit the plan/draft/critique directly in respective tabs.
   - Click "Modify" to update a node's output and re-run from there.
   - Switch threads to compare different conversation branches.
   - View state history and rollback to prior checkpoints.

---

## 📦 Dependencies

### Backend (Python)

```
langchain>=0.1.0
langgraph>=0.1.0
langchain-openai>=0.0.1
langchain-community
tavily-python
python-dotenv
flask>=2.0
flask-cors
requests
```

Install via:
```powershell
cd d:\MCP\agent-backend
pip install -r requirements.txt
```

### Frontend (Node)

```json
{
  "dependencies": {
    "react": "^17.0.2",
    "react-dom": "^17.0.2",
    "react-router-dom": "^6.x",
    "axios": "^1.x"
  },
  "devDependencies": {
    "typescript": "^5.x",
    "react-scripts": "5.x"
  }
}
```

Install via:
```powershell
cd d:\MCP\agent-gui-react
npm install
```

---

## ⚙️ Configuration

### Backend (.env)

Create a `.env` file in `d:\MCP\agent-backend\`:

```env
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_KEY_HERE
TAVILY_API_KEY=tvly-dev-YOUR_TAVILY_KEY_HERE
MODEL=gpt-4
PORT=5000
```

### Frontend (.env.local)

Create a `.env.local` file in `d:\MCP\agent-gui-react\`:

```env
REACT_APP_API_BASE_URL=http://localhost:5000
```

---

## 🛠️ Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Flask 404 on GET / | Root endpoint returns JSON info, not HTML. | Expected behavior. Use /health or /api/* endpoints. |
| Node 22 webpack error (ERR_OSSL_EVP_UNSUPPORTED) | OpenSSL 3 incompatibility with older webpack. | Set `$env:NODE_OPTIONS="--openssl-legacy-provider"` before npm start, or downgrade to Node 18.x. |
| react-router-dom peer dependency error | Incorrect version specified. | Install v6: `npm install react-router-dom@6` |
| CORS errors from frontend | Flask CORS not enabled. | Ensure `CORS(app)` is called in app.py. |
| Streaming doesn't show output | Backend graph.invoke() is blocking or erroring. | Check Flask logs for errors; test /api/plan directly first. |
| Thread state not persisting | MemorySaver is in-memory only. | For persistence across restarts, replace MemorySaver with SqliteSaver (see Development Notes). |
| "Module not found: react-router-dom" | Package not installed. | Run `npm install react-router-dom@6`. |
| API calls return 400 Bad Request | JSON payload malformed. | Use `ConvertTo-Json` in PowerShell or proper JSON syntax in curl. |

---

## 📝 Development Notes

### Hot Reload & Development

- **Frontend**: npm start enables hot reload on file change. Changes to .tsx/.css reflect immediately (Ctrl+S).
- **Backend**: Flask debug=True enables auto-reload on Python file changes. Restart manually if needed.

### State & Checkpointing

- **MemorySaver**: In-memory storage; state cleared on backend restart.
- **Thread ID**: Each conversation has a unique thread_id; independent state branches.
- **Modify & Continue**: Edit any node's output (plan, draft, critique) and re-invoke from that checkpoint.

### Production Deployment

#### Frontend
- Build: `npm run build` → generates optimized build/ folder.
- Hosting options:
  - **Vercel**: `vercel deploy` (recommend).
  - **S3 + CloudFront**: Upload build/ folder to S3; use CloudFront as CDN.
  - **Flask serve**: Copy build/ to Flask static folder; Flask serves index.html on unknown routes.

#### Backend
- **WSGI Server**: Replace Flask dev server with Gunicorn:
  ```powershell
  pip install gunicorn
  gunicorn -w 4 -b 0.0.0.0:5000 app:app
  ```
- **Database**: Replace MemorySaver with SqliteSaver for state persistence:
  ```python
  from langgraph.checkpoint.sqlite import SqliteSaver
  memory = SqliteSaver(conn=sqlite3.connect("agent.db"))
  ```
- **Env Vars**: Use environment variables or secret manager (AWS Secrets Manager, GitHub Secrets) for API keys.
- **Docker** (optional): Containerize both backend and frontend for easy deployment.

### Performance Optimization

- **Streaming**: NDJSON streaming avoids waiting for full response.
- **Async**: Consider async/await for I/O-bound operations (API calls, DB queries).
- **Caching**: Cache research results (Tavily responses) if similar queries repeat.
- **Rate Limiting**: Add rate limiting to backend to prevent API quota exhaustion.

---

## 📄 License

MIT License — feel free to use for personal and commercial projects.

---

## 👥 Contributing

Contributions are welcome! Submit issues and pull requests on GitHub.

---

## 📧 Contact & Support

For questions or issues, open a GitHub issue or contact the project maintainers.

---

## 🎯 Roadmap

- [ ] Persist state to SQLite database.
- [ ] Add user authentication & session management.
- [ ] Support multiple trip types (business, adventure, luxury, budget).
- [ ] Integrate calendar/booking APIs (Expedia, Booking.com).
- [ ] Mobile app (React Native).
- [ ] Multi-language support.
- [ ] Export itinerary as PDF/Markdown.

---

**Happy Planning! 🌍✈️🗺️**
.idea/
*.vscode/
*.md
*.ps1
*.sh
