# 🚀 Arka

> **An AI-powered code understanding platform that goes beyond traditional RAG using ASTs, Knowledge Graphs, and Repository Intelligence.**

![Status](https://img.shields.io/badge/status-active_development-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Node.js](https://img.shields.io/badge/Node.js-22+-green)

---

## 🌟 Vision

Modern AI assistants can explain small code snippets, but they struggle to understand **entire software projects**.

Arka aims to change that.

Instead of treating source code as plain text, Arka understands a repository's **structure, relationships, dependencies, and architecture** before answering developer questions.

Our mission is to build an AI software engineering assistant that truly understands codebases—not just documents.

---

# ✅ Current Capabilities

Arka is currently capable of:

- ✅ Clone GitHub repositories
- ✅ Scan repositories recursively
- ✅ Detect programming languages
- ✅ Parse JavaScript, TypeScript and Python source files
- ✅ Generate Abstract Syntax Trees (AST) using the official Tree-sitter parser
- ✅ Extract functions and classes using Tree-sitter Query and QueryCursor
- ✅ Build a repository symbol index via `RepositoryParser`
- ✅ Language plugin architecture for adding new grammars via `queries/<language>.py`
- ✅ Expose parsing functionality through a FastAPI service

> **Current Stage:** Repository Symbol Extraction

## ❌ The Problem

Large Language Models have limited context windows.

Traditional Retrieval-Augmented Generation (RAG) retrieves relevant code snippets using embeddings, but code is **not just text**.

Traditional RAG often loses:

- Function relationships
- Class hierarchies
- Import dependencies
- Call chains
- Project architecture
- Repository context

This frequently leads to incomplete or hallucinated answers.

---

## 💡 Our Solution

Arka combines multiple layers of repository understanding:

```text
                        GitHub Repository
                                │
                                ▼
                      Repository Service
                                │
                                ▼
                        Clone Repository
                                │
                                ▼
                      Repository Scanner
                                │
                                ▼
                     Language Detection
                                │
                                ▼
                         Parser Factory
                                │
          ┌─────────────────────┼──────────────────────┐
          ▼                     ▼                      ▼
 JavaScript Parser      TypeScript Parser      Python Parser
          │                     │                      │
          └─────────────────────┼──────────────────────┘
                                ▼
                     Tree-sitter Abstract Syntax Tree
                                │
                                ▼
              Tree-sitter Query + QueryCursor
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
        FunctionExtractor               ClassExtractor
                │                               │
                └───────────────┬───────────────┘
                                ▼
                       Repository Index
                                │
                                ▼
                       Knowledge Graph (Upcoming)
                                │
                                ▼
                        Hybrid Retrieval (Upcoming)
                                │
                                ▼
                             Large Language Model
```

Instead of retrieving random code chunks, Arka retrieves **repository knowledge**.

---

# ✨ Features

## ✅ Implemented

- GitHub Repository Cloning
- Repository Scanner
- Language Detection
- Parser Factory
- Official Tree-sitter Integration
- AST Generation
- Tree-sitter Query-based Symbol Extraction
- Function and Class Extraction
- Repository Parser and Symbol Index
- Language Query Plugins (JavaScript, TypeScript, Python)
- FastAPI Parsing API

---

## 🚧 Upcoming

- Import and Export Extraction
- Dependency Analysis
- Knowledge Graph
- Vector Search
- Repository Chat
- Hybrid Retrieval
- GraphRAG

# 📂 Current Project Structure

```text
arka/
│
├── frontend/
│
├── backend/
│   ├── src/
│   │   ├── controllers/
│   │   ├── routes/
│   │   ├── services/
│   │   └── ...
│
├── ai-service/
│   ├── analysis/
│   │   ├── scanner.py
│   │   ├── language_detector.py
│   │   ├── parser_factory.py
│   │   ├── repository_parser.py
│   │   ├── parsers/
│   │   ├── queries/
│   │   │   ├── javascript.py
│   │   │   ├── typescript.py
│   │   │   ├── python.py
│   │   │   └── registry.py
│   │   └── extractors/
│   │       ├── base_extractor.py
│   │       ├── function_extractor.py
│   │       └── class_extractor.py
│   │
│   ├── api/
│   ├── schemas/
│   ├── tests/
│   └── app.py
│
├── docs/
│
└── docker/
```

---

# 🛠️ Tech Stack

| Layer | Technology |
|--------|------------|
| Frontend | Next.js, React, TypeScript |
| Backend | Node.js, Express.js |
| AI Service | FastAPI |
| Parser | Tree-sitter |
| Graph Database | Neo4j *(planned)* |
| Vector Database | Qdrant *(planned)* |
| Database | PostgreSQL *(planned)* |
| LLM | OpenAI / Open-source models |
| Deployment | Docker |

---

# 📌 Development Roadmap

## Phase 1 — Foundation

- [x] Monorepo setup
- [x] Backend initialization
- [x] Frontend initialization
- [x] AI service initialization
- [x] Architecture documentation

---

## Phase 2 — Repository Ingestion

- [x] GitHub repository cloning
- [x] URL validation
- [ ] Repository metadata
- [ ] Workspace management

---

## Phase 3 — Code Parsing

- [x] Repository Scanner
- [x] Language Detection
- [x] Parser Factory
- [x] Official Tree-sitter Integration
- [x] AST Generation
- [x] FastAPI Parser API

---

## Phase 4 — Symbol Extraction

- [x] Function Extraction (Tree-sitter Query API)
- [x] Class Extraction (Tree-sitter Query API)
- [x] Language Query Plugins
- [ ] Method Extraction
- [ ] Import Extraction
- [ ] Export Extraction
- [ ] Variable Extraction

---

## Phase 5 — Repository Index

- [x] Repository Parser Pipeline
- [x] Per-file Function and Class Index
- [ ] File Metadata
- [ ] Cross-file References

---

## Phase 6 — Knowledge Graph

- [ ] Neo4j Integration
- [ ] Dependency Graph
- [ ] Call Graph

---

## Phase 7 — AI Retrieval

- [ ] Hybrid retrieval
- [ ] GraphRAG
- [ ] Prompt construction

---

## Phase 8 — Developer Assistant

- [ ] Repository Chat
- [ ] Architecture Q&A
- [ ] Code Explanation
- [ ] Bug Investigation
- [ ] Refactoring Suggestions

---

# 🚀 Getting Started

## Clone the repository

```bash
git clone https://github.com/CodeManBist/Arka.git
```

---

## Backend

```bash
cd backend
npm install
npm run dev
```

---

## AI Service

```bash
cd ai-service

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

uvicorn app:app --reload
```

---

## Frontend

```bash
cd frontend
npm install
npm run dev
```

---

# 🎯 Long-term Goal

Arka is designed to become an intelligent software engineering assistant capable of:

- Understanding complete repositories
- Explaining project architecture
- Finding bugs
- Navigating large codebases
- Answering repository-specific questions
- Assisting developers throughout the software development lifecycle

---

# 🤝 Contributing

We welcome contributions from developers, AI engineers, and open-source enthusiasts.

If you'd like to contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a Pull Request

Please ensure your code follows the project's coding standards and includes appropriate documentation.

---

# 📖 Documentation

Project documentation is available in the `docs/` directory.

---

# 📜 License

This project is licensed under the MIT License.

---

# ⭐ Support the Project

If you find Arka interesting, consider:

- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 🤝 Contributing code
- 📢 Sharing the project with others

Together, let's build the future of AI-powered software engineering.
