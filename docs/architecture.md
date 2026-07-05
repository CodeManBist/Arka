# 🚀 Arka

<div align="center">

### AI-Powered Code Understanding Platform

**Beyond Traditional RAG with ASTs, Knowledge Graphs, and Repository Intelligence**

![Status](https://img.shields.io/badge/status-active_development-blue)
![Version](https://img.shields.io/badge/version-v0.1-green)
![License](https://img.shields.io/badge/license-MIT-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Node.js](https://img.shields.io/badge/Node.js-22+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)

---

**Arka is an AI-powered code understanding platform that analyzes repositories using Abstract Syntax Trees (ASTs), structural relationships, and knowledge graphs before querying Large Language Models.**

Instead of treating source code as plain text, Arka understands the architecture of a software project.

</div>

---

# 📖 Table of Contents

- Vision
- Why Arka?
- Current Capabilities
- The Problem
- Our Solution
- High-Level Architecture
- Features
- Current Project Structure
- Technology Stack
- Development Roadmap
- Getting Started
- API
- Why Tree-sitter?
- Long-term Vision
- Contributing
- Documentation
- License

---

# 🌟 Vision

Modern AI coding assistants are excellent at explaining **individual files** or **small code snippets**.

However, they struggle to understand an **entire software project**.

Large repositories contain:

- hundreds of files
- thousands of functions
- complex dependency graphs
- architectural relationships
- hidden business logic

Traditional AI systems cannot fully reason about these relationships because they treat code as text.

Arka changes this.

Instead of sending raw code to an LLM, Arka first builds a structural understanding of the repository using compiler techniques and graph-based reasoning.

The long-term goal is to build an AI Software Engineering Assistant capable of understanding complete repositories with the accuracy of static analysis tools and the reasoning ability of modern LLMs.

---

# 🎯 Why Arka?

Most Retrieval-Augmented Generation (RAG) systems work like this:

```

User Question
│
▼
Embedding Search
│
▼
Random Code Chunks
│
▼
LLM

```

This approach ignores the structure of software.

Arka instead follows this pipeline:

```

GitHub Repository
│
▼
Repository Scanner
│
▼
Tree-sitter Parser
│
▼
Abstract Syntax Tree
│
▼
Knowledge Extraction
│
▼
Knowledge Graph
│
▼
Vector Search
│
▼
Hybrid Retrieval
│
▼
LLM

```

This enables the AI to understand:

- Function ownership
- Class hierarchies
- Imports and exports
- Dependency relationships
- Cross-file references
- Project architecture

instead of simply retrieving text.

---

# ✅ Current Capabilities

As of **Day 3**, Arka can:

- ✅ Clone GitHub repositories
- ✅ Scan repositories recursively
- ✅ Detect supported programming languages
- ✅ Parse JavaScript repositories
- ✅ Parse TypeScript repositories
- ✅ Parse Python repositories
- ✅ Generate Abstract Syntax Trees using the official Tree-sitter parser
- ✅ Expose parsing functionality through FastAPI
- ✅ Modular parser architecture using the Factory Pattern

---

# 🚧 Current Status

Current development stage:

```

Repository
│
▼
Scanner ✅
│
▼
Language Detection ✅
│
▼
Parser Factory ✅
│
▼
Tree-sitter AST ✅
│
▼
Symbol Extraction ⏳
│
▼
Knowledge Graph ⏳
│
▼
Embeddings ⏳
│
▼
Repository Chat ⏳

```

Arka has completed its repository ingestion and parsing infrastructure.

The next milestone is building repository knowledge from ASTs.

---

# ❌ The Problem

Large Language Models have limited context windows.

A modern enterprise repository may contain:

- 5,000+ files
- 100,000+ lines of code
- hundreds of modules
- thousands of functions

Traditional RAG improves retrieval but still treats code as plain text.

This results in:

- Missing dependency information
- Broken call chains
- No architectural understanding
- Lost function relationships
- Hallucinated answers
- Poor reasoning across multiple files

Software is **not documents**.

Software is a graph.

Arka is designed around this principle.

---

# 💡 Our Solution

Arka combines static code analysis with AI to understand repositories before asking an LLM to reason about them.

Instead of embedding arbitrary chunks of code, Arka builds a structured representation of the repository.

The complete pipeline looks like this:

```text
                         GitHub Repository
                                  │
                                  ▼
                        Repository Service
                                  │
                           Clone Repository
                                  │
                                  ▼
                        Repository Scanner
                                  │
                                  ▼
                        Language Detector
                                  │
                                  ▼
                           Parser Factory
                                  │
          ┌───────────────────────┼────────────────────────┐
          ▼                       ▼                        ▼
 JavaScript Parser       TypeScript Parser         Python Parser
          │                       │                        │
          └───────────────────────┼────────────────────────┘
                                  ▼
                    Tree-sitter Abstract Syntax Tree
                                  │
                                  ▼
                        Symbol Extraction (Upcoming)
                                  │
                                  ▼
                         Repository Knowledge
                                  │
                   ┌──────────────┴──────────────┐
                   ▼                             ▼
             Knowledge Graph              Vector Database
                   │                             │
                   └──────────────┬──────────────┘
                                  ▼
                           Hybrid Retrieval
                                  │
                                  ▼
                          Large Language Model
                                  │
                                  ▼
                         AI-Powered Developer Assistant
```

Every stage enriches the repository with more knowledge before an LLM is involved.

---

# ✨ Features

## ✅ Implemented

### Repository Management

- Clone GitHub repositories
- Validate repository URLs
- Local repository workspace
- Repository scanning

### Language Support

- JavaScript
- TypeScript
- Python

### Parsing Engine

- Official Tree-sitter integration
- Modular parser architecture
- Language detection
- Parser Factory pattern
- AST generation

### AI Service

- FastAPI backend
- File parsing API
- Language-aware parsing
- Modular analysis layer

---

## 🚧 Upcoming

### Repository Intelligence

- Function extraction
- Class extraction
- Interface extraction
- Variable extraction
- Import analysis
- Export analysis

### Repository Knowledge

- Symbol Table
- Repository Index
- Cross-file References
- Call Graph
- Dependency Graph

### AI Features

- Knowledge Graph
- Embeddings
- Hybrid Retrieval
- GraphRAG
- Repository Chat
- Architecture Understanding
- Code Navigation
- Bug Investigation
- Refactoring Suggestions

---

# 📂 Project Structure

```text
arka/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── ...
│
├── backend/
│   ├── src/
│   │
│   ├── controllers/
│   ├── routes/
│   ├── services/
│   ├── repositories/
│   └── ...
│
├── ai-service/
│
│   ├── api/
│   │      parser.py
│   │
│   ├── analysis/
│   │
│   │      scanner.py
│   │      language_detector.py
│   │      parser_factory.py
│   │
│   │      parsers/
│   │      │
│   │      ├── base_parser.py
│   │      ├── javascript_parser.py
│   │      ├── typescript_parser.py
│   │      └── python_parser.py
│   │
│   │      extractors/
│   │
│   │      graph/
│   │
│   ├── schemas/
│   │
│   ├── utils/
│   │
│   └── app.py
│
├── docs/
│
├── docker/
│
├── docker-compose.yml
│
└── README.md
```

---

# 🛠 Technology Stack

| Layer | Technology |
|--------|------------|
| Frontend | Next.js, React, TypeScript |
| Backend | Node.js, Express.js, TypeScript |
| AI Service | Python, FastAPI |
| Parsing | Tree-sitter |
| Repository Analysis | Custom Analysis Engine |
| Graph Database | Neo4j *(Planned)* |
| Vector Database | Qdrant *(Planned)* |
| Database | PostgreSQL *(Planned)* |
| Containerization | Docker |
| Version Control | Git & GitHub |
| AI Models | OpenAI / Open-source Models |

---

# 🌳 Why Tree-sitter?

Traditional AI systems tokenize source code as text.

Tree-sitter parses source code into an **Abstract Syntax Tree (AST)** that preserves the structure of the programming language.

Example:

Source Code

```javascript
function add(a, b) {
    return a + b;
}
```

Tree-sitter AST

```text
Program
└── FunctionDeclaration
      ├── Identifier
      ├── Parameters
      └── ReturnStatement
```

This allows Arka to understand:

- Function declarations
- Classes
- Interfaces
- Imports
- Exports
- Variables
- Method calls
- Project structure

instead of treating code as plain text.

---

# 🌐 API

## Parse a Source File

### Endpoint

```
POST /parse-file
```

### Request

```json
{
    "file_path": "/path/to/repository/app.js"
}
```

### Response

```json
{
    "success": true,
    "language": "javascript",
    "file": "app.js",
    "root_node": "(program ...)"
}
```

The backend will eventually call this endpoint after cloning a repository.

---

# 📌 Development Roadmap

## ✅ Phase 1 — Foundation

- Monorepo setup
- Backend initialization
- Frontend initialization
- AI Service initialization
- Documentation

---

## ✅ Phase 2 — Repository Ingestion

- GitHub Repository Cloning
- URL Validation
- Repository Service

---

## ✅ Phase 3 — Parsing Pipeline

- Repository Scanner
- Language Detection
- Parser Factory
- JavaScript Parser
- TypeScript Parser
- Python Parser
- Official Tree-sitter Integration
- AST Generation
- FastAPI Parser API

---

## 🚧 Phase 4 — Symbol Extraction

- Function Extraction
- Class Extraction
- Interface Extraction
- Method Extraction
- Variable Extraction
- Import Extraction
- Export Extraction

---

# 🚀 Getting Started

## Prerequisites

Before running Arka, ensure you have:

- Node.js 22+
- Python 3.11+
- Git
- npm
- pip

---

## Clone the Repository

```bash
git clone https://github.com/<your-username>/arka.git

cd arka
```

---

## Backend

```bash
cd backend

npm install

npm run dev
```

Backend will start on:

```
http://localhost:5000
```

---

## AI Service

```bash
cd ai-service

python -m venv venv
```

Activate virtual environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run FastAPI

```bash
uvicorn app:app --reload
```

AI Service

```
http://localhost:8000
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend

```
http://localhost:3000
```

---

# 🎯 Long-term Vision

Arka aims to become an intelligent Software Engineering Assistant capable of:

- Understanding complete repositories
- Explaining project architecture
- Navigating large codebases
- Answering repository-specific questions
- Detecting dependency relationships
- Finding bugs
- Suggesting refactoring opportunities
- Assisting developers throughout the software development lifecycle

Instead of replacing developers, Arka is designed to augment their understanding of complex software systems.

---

# ❤️ Open Source Philosophy

Arka is built in public.

The goal is not only to create an AI-powered repository understanding platform but also to document every architectural decision along the journey.

Whether you're interested in AI, compilers, static analysis, graph databases, or modern software architecture, contributions and discussions are welcome.

If you're learning, feel free to explore the codebase, ask questions, or improve documentation.

---

# 🤝 Contributing

We welcome contributions from developers, AI engineers, researchers, and open-source enthusiasts.

To contribute:

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/amazing-feature
```

3. Commit your changes

```bash
git commit -m "feat: add amazing feature"
```

4. Push your branch

```bash
git push origin feature/amazing-feature
```

5. Open a Pull Request

Before submitting, please ensure:

- Code follows the project structure
- New functionality is documented
- Existing functionality is not broken
- Commit messages follow conventional commits

---

# 📖 Documentation

Project documentation lives inside the `docs/` directory.

Current documents:

- Architecture
- Future design documents
- Implementation notes

---

# 📜 License

This project is licensed under the MIT License.

---

# ⭐ Support the Project

If you like Arka, consider:

- ⭐ Starring the repository
- 🍴 Forking the project
- 🐛 Reporting bugs
- 💡 Suggesting new ideas
- 🤝 Contributing code
- 📢 Sharing it with the community

Every contribution helps make Arka a better platform for developers.

---

<div align="center">

### Built with ❤️ by developers, for developers.

**Understanding software before asking AI to understand it.**

</div>