# 🎯 Blast Radius

**Every code change has a blast radius. See it before production does.**

An AI-powered impact analysis engine that answers the one question every AI coding tool guesses at: *"What breaks if I change this?"*

Built for the OpenAI Codex Hackathon × NamasteDev.

---

## 🌟 The Problem

Every existing AI coding assistant — Copilot, Cursor, ChatGPT, even RAG-based tools — works the same way under the hood: retrieve text that *looks* similar, generate an answer, hope it's right.

Ask any of them: *"What happens if I change this function's signature?"* — and you'll get a vague guess based on embedding similarity, not a real answer. That's because none of them actually understand your codebase's structure. They see text. They don't see the graph.

This is how production incidents happen. A developer changes a function that "looked safe," and three services quietly break because nobody could see the dependency chain.

## 💡 The Solution

Blast Radius parses your repository into a real Abstract Syntax Tree, builds a call graph and import graph from it, and **traverses actual code relationships** — not text similarity — to identify the code most likely to be impacted by a change.

Blast Radius combines AST-based static analysis with graph traversal to surface real dependencies, rather than guessing from what "looks similar." (Static analysis has real limits — reflection, dynamic imports, `eval()`, and dependency injection can introduce runtime edges a static graph won't catch. Blast Radius is a much stronger signal than text-similarity search, not an oracle.)

Then Codex turns that graph traversal into a plain-English risk summary a human can act on in seconds.

---

## ✨ Features

### ✅ Core (Implemented)

- **Repository ingestion** — clone and scan any public GitHub repo
- **AST-based parsing** — Tree-sitter parsing for Python, JavaScript, and TypeScript
- **Symbol extraction** — functions, classes, methods, imports, and exports indexed per file
- **Call graph construction** — real edges between callers and callees, not inferred from text
- **Import graph construction** — file-to-file dependency edges
- **Impact traversal engine** — given any function or class, returns:
  - Direct callers
  - Transitive callers (configurable depth)
  - Files that import the changed symbol
  - A computed "risk score" based on fan-out, centrality, and test coverage
- **🔥 Diff-based analysis (the killer feature)** — paste a git diff instead of manually picking a function:
  1. Blast Radius automatically detects which symbols changed
  2. Traces every affected file and caller
  3. Highlights high-risk areas (e.g. payment flows, low test coverage)
  4. Generates a PR-review-style summary — **and a suggested mitigation**, not just a warning
  5. Reports a **confidence score** alongside the risk score, based on how much of the call graph was statically resolvable

- **Blast radius visualization** — an interactive radiating graph showing impact spreading outward from the selected symbol, color-coded by severity
- **Clickable node details** — clicking any node in the graph shows why it's affected, its file path and line number, the full call chain back to the changed symbol, and its individual risk level
- **AI risk summary** — Codex converts the traversal result into a clear, human-readable explanation of what's at risk and why
- **Repository overview dashboard** — a quick "table stakes" view after scanning any repo: language breakdown, function/class/import counts, total call-graph edges, and which services look most critical by fan-in
- **One-click "Copy PR Review Comment"** — formats the existing Codex risk summary into ready-to-paste GitHub review comment text

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Backend | Node.js, Express |
| AI Service | FastAPI |
| Parsing | Tree-sitter (official parser + Query API) |
| Graph | In-memory adjacency graph |
| LLM | OpenAI Codex |
| Deployment | Docker |

---

## 📂 Project Structure

```
blast-radius/
│
├── frontend/                  # Next.js UI — symbol picker, graph visualization
│   └── app/
│       ├── blast-radius/     # Main Blast Radius application
│       │   └── page.tsx      # Full-featured impact analysis UI
│       ├── page.tsx          # Marketing landing page
│       └── layout.tsx        # Root layout
│
├── backend/                   # API layer, orchestration
│   └── src/
│       ├── controllers/
│       ├── routes/
│       └── services/
│
├── ai-service/                # Core analysis engine
│   ├── analysis/
│   │   ├── scanner.py
│   │   ├── language_detector.py
│   │   ├── parser_factory.py
│   │   ├── repository_parser.py
│   │   ├── parsers/
│   │   │   ├── python_parser.py
│   │   │   ├── javascript_parser.py
│   │   │   └── typescript_parser.py
│   │   ├── queries/
│   │   │   ├── python.py
│   │   │   ├── javascript.py
│   │   │   ├── typescript.py
│   │   │   └── registry.py
│   │   ├── extractors/
│   │   │   ├── base_extractor.py
│   │   │   ├── function_extractor.py
│   │   │   ├── class_extractor.py
│   │   │   ├── import_extractor.py
│   │   │   ├── export_extractor.py
│   │   │   └── variable_extractor.py
│   │   └── diff_parser.py      # Parse git diffs to extract changed symbols
│   │
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── node.py            # Graph node representation
│   │   ├── edge.py            # Graph edge representation
│   │   ├── graph.py           # Graph data structure
│   │   ├── call_graph_builder.py    # Build call graphs
│   │   ├── import_graph_builder.py  # Build import graphs
│   │   └── impact_traversal.py      # Impact analysis engine
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── parser.py
│   │   ├── repository.py
│   │   └── blast_radius.py    # Blast Radius API endpoints
│   │
│   ├── schemas/
│   │   └── response.py
│   │
│   └── app.py                 # FastAPI application
│
├── docs/
├── docker/
└── README.md
```

---

## 🚀 How It Works — End to End

1. **Submit a repo URL** — Blast Radius clones and scans it, immediately showing a repo overview dashboard (languages, function/class counts, call-graph size, critical services)
2. **Parsing** — Tree-sitter builds an AST for every source file
3. **Extraction** — functions, classes, and imports are pulled out via Tree-sitter queries
4. **Graph construction** — call edges and import edges are built from the extracted symbols
5. **Paste a git diff** (primary flow) — or manually select a function/class in the UI
6. **Traversal** — the engine walks the graph outward from the changed symbol(s), collecting every real dependent and computing a confidence score based on how much of the graph was statically resolvable
7. **AI summary** — Codex turns the raw graph path into a plain-English risk explanation, PR-review style, plus a suggested mitigation
8. **Visualize** — the blast radius renders as a color-coded, pulsing radiating graph; clicking any node shows its file, line, call chain, and risk level
9. **Copy PR comment** — one click formats the summary into a ready-to-paste GitHub review comment

---

## 🎬 Demo Script (3 minutes)

1. **0:00–0:20** — Problem framing: AI tools today explain code, but none of them tell you what breaks when you change it. Every developer has shipped a "safe-looking" change that quietly broke something downstream
2. **0:20–1:00** — Paste a repo URL → instantly show the repo overview dashboard (languages, function count, call-graph size) so judges see this is real, substantial analysis, not a toy
3. **1:00–2:00** — Paste a real git diff (e.g. adding a parameter to `processPayment`) → Blast Radius detects the changed symbol, shows the hero risk card (HIGH risk, 94% confidence, 17 callers, 5 files, suggested fix), and the pulsing red/yellow/green graph expands outward. Click one red node live to show file, line, and call chain — this is the interactive moment judges remember
4. **2:00–2:40** — Click "Copy PR Review Comment" → show the ready-to-paste GitHub comment. This is the "developers would actually use this" beat
5. **2:40–3:00** — Close on the tagline: "AI can tell you what your code does. Blast Radius tells you what your change will break. Know what breaks — before you ship."

---

## 📌 Minimum Winning Scope

The biggest risk to this project isn't the idea — it's trying to build too much in four days. This is the smallest version that still demonstrates the core innovation, feels premium, and hits every judging criterion:

1. ✅ Clone a GitHub repository + show a basic repo overview (languages, function/class counts)
2. ✅ Parse Python, JavaScript, and TypeScript with Tree-sitter
3. ✅ Build a call graph and import graph
4. ✅ Accept a pasted git diff (or manual function selection as fallback)
5. ✅ Traverse dependencies, compute a risk score and confidence score
6. ✅ Generate a Codex summary with a suggested mitigation
7. ✅ Display an interactive, color-coded, clickable blast-radius graph
8. ✅ A "Copy PR Review Comment" button

---

## 🎨 Design Principles

- Dark theme, generous whitespace, one accent color (used for the risk badges and graph, not scattered everywhere)
- One large, obvious "Analyze" action — no cluttered nav
- Smooth transitions when the graph expands outward (this is the moment people remember — don't let it be a jump-cut)
- Clean, modern typography — no default browser fonts
- The hero risk card (risk, confidence, callers, fix) should be the first thing visible after analysis — no scrolling required

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 22+
- Git
- Docker (optional, for deployment)

### Backend Setup

```bash
cd backend
npm install
npm run dev
```

### AI Service Setup

```bash
cd ai-service

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Tree-sitter and language parsers
pip install tree-sitter

# Build language parsers (if needed)
tree-sitter build

# Run the service
uvicorn app:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the ai-service directory:

```env
# OpenAI API Key for Codex integration
OPENAI_API_KEY=your_api_key_here

# Server configuration
HOST=0.0.0.0
PORT=8000

# Repository cloning
GITHUB_TOKEN=your_github_token_here
```

---

## 📋 API Endpoints

### Blast Radius API

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/blast-radius/analyze` | Analyze impact of a single symbol |
| POST | `/api/blast-radius/analyze-diff` | Analyze impact of a git diff |
| POST | `/api/blast-radius/repository-overview` | Get repository overview statistics |
| POST | `/api/blast-radius/generate-pr-comment` | Generate a GitHub PR review comment |

### Request Examples

#### Analyze Single Symbol

```bash
curl -X POST http://localhost:8000/api/blast-radius/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "/path/to/repo",
    "symbol_name": "processPayment",
    "symbol_type": "function",
    "max_depth": 3
  }'
```

#### Analyze Git Diff

```bash
curl -X POST http://localhost:8000/api/blast-radius/analyze-diff \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "/path/to/repo",
    "diff": "diff --git a/src/payments.py b/src/payments.py\n...",
    "max_depth": 3
  }'
```

#### Generate PR Comment

```bash
curl -X POST http://localhost:8000/api/blast-radius/generate-pr-comment \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "/path/to/repo",
    "diff": "diff --git a/src/payments.py b/src/payments.py\n..."
  }'
```

---

## 🧪 Testing

### Run Tests

```bash
cd ai-service
python -m pytest tests/ -v
```

### Test Files

- `tests/test_function_extractor.py` — Test function extraction
- `tests/test_class_extractor.py` — Test class extraction
- `tests/test_symbol_table.py` — Test symbol table functionality

---

## 📊 Example Output

### Diff Analysis Example

**Input:**
```diff
diff --git a/src/payments.py b/src/payments.py
index abc123..def456 100644
--- a/src/payments.py
+++ b/src/payments.py
@@ -10,7 +10,7 @@ class PaymentService:
     
 @app.route('/process', methods=['POST'])
-def process_payment(user):
+def process_payment(user, currency):
     # Process payment logic
     amount = calculate_amount(user)
     return charge_user(user, amount)
```

**Output:**
```json
{
  "success": true,
  "results": [
    {
      "changed_symbol": "process_payment",
      "changed_symbol_type": "function",
      "changed_file": "src/payments.py",
      "direct_callers": 17,
      "transitive_callers": 23,
      "affected_files": ["src/payments.py", "src/api.py", "src/checkout.py", "tests/test_payments.py"],
      "risk_level": "HIGH",
      "risk_score": 45.5,
      "confidence_score": 0.94,
      "ai_summary": "Adding the required currency parameter will break 17 call sites across 5 files. Three of the affected callers are payment workflows, making this a high-risk change.",
      "suggested_fix": "Introduce currency=\"USD\" as a default before making it required. 17 call sites won't need to change immediately."
    }
  ],
  "summary": {
    "total_changed_symbols": 1,
    "total_callers": 40,
    "total_files": 5,
    "overall_risk": "HIGH",
    "average_confidence": 0.94
  }
}
```

### PR Comment Example

```markdown
## 🚨 Blast Radius Analysis

**Risk: 🟠 HIGH**  **Confidence: 94%**

- **1 symbols changed**  
- **40 callers affected**  
- **5 files impacted**

### Changed Symbols:
- 🔄 `process_payment` (function) in `src/payments.py`

### Impact Details:
**1. `process_payment`** 🟠
   - Direct callers: 17
   - Transitive callers: 23
   - Risk score: 45.5

### Suggested Actions:
- 🛑 **DO NOT MERGE** without addressing the high-risk changes
- Add comprehensive tests for affected functionality
- Consider breaking this into smaller, safer PRs

---
*Generated by [Blast Radius](https://github.com/CodeManBist/Arka)*
```

---

## 🎯 What's Next (Post-Hackathon)

- Expand language support (Go, Java, Rust)
- Persist graphs in Neo4j for larger repos
- Test-coverage overlay — highlight affected callers with no test coverage
- CI integration — flag high-risk PRs automatically before merge
- IDE extension — see blast radius inline while editing
- Live GitHub PR integration — OAuth + webhook, auto-posts the review comment directly on a real PR

---

## 📄 License

MIT

---

## 🤝 Contributing

We welcome contributions from developers, AI engineers, and open-source enthusiasts.

If you'd like to contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a Pull Request

Please ensure your code follows the project's coding standards and includes appropriate documentation.

---

## 🙏 Acknowledgments

- Built with ❤️ for the OpenAI Codex Hackathon × NamasteDev
- Powered by Tree-sitter for AST parsing
- Inspired by the need for better code understanding tools

---

**Every code change has a blast radius. See it before production does.**
