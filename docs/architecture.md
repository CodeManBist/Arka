# Arka - Project Architecture

## Project Vision

Arka is an AI-powered code understanding platform that helps developers explore, understand, and reason about large codebases. Instead of treating source code as plain text, Arka analyzes the structure of a repository, builds relationships between code elements, and enables accurate AI-powered code search, explanation, and navigation.

The long-term goal is to build an intelligent software engineering assistant capable of answering repository-specific questions with a deep understanding of project architecture.

---

# Problem Statement

Modern Large Language Models have limited context windows and cannot understand an entire software project at once. Traditional Retrieval-Augmented Generation (RAG) improves this by retrieving relevant code snippets, but it still treats code as text rather than structured software.

This causes several problems:

- Loss of relationships between functions, classes, and files.
- Difficulty understanding call chains.
- Poor navigation across large repositories.
- Hallucinated answers due to missing project context.

Arka solves this by combining source code parsing, structural analysis, and semantic retrieval to provide repository-aware AI assistance.

---

# High-Level Architecture

```
                GitHub Repository
                       │
                       ▼
              Repository Service
                       │
                 Clone Repository
                       │
                       ▼
                 Source Code Parser
                 (Tree-sitter)
                       │
              Generate Abstract Syntax Tree
                       │
       Extract Functions, Classes, Imports,
         Variables, Calls and Dependencies
                       │
                       ▼
      Knowledge Graph + Vector Database
                       │
                       ▼
              Retrieval Engine (RAG)
                       │
                       ▼
                  Large Language Model
                       │
                       ▼
               AI Response to Developer
```

---

# Components

## 1. Frontend

Responsibilities:

- User authentication
- Repository management
- Chat interface
- Repository dashboard
- Search interface
- Visualization of code relationships

Technology:

- Next.js
- React
- TypeScript
- Tailwind CSS

---

## 2. Backend

Responsibilities:

- Authentication
- Repository management
- GitHub integration
- API layer
- Communication with AI Service
- Database management

Technology:

- Node.js
- Express.js
- TypeScript

---

## 3. AI Service

Responsibilities:

- Parse source code
- Build AST
- Extract repository knowledge
- Generate embeddings
- Query vector database
- Construct prompts
- Interact with LLM

Technology:

- Python
- FastAPI

---

## 4. Parser

Responsibilities:

- Parse source code
- Generate Abstract Syntax Tree (AST)
- Detect functions
- Detect classes
- Detect imports
- Detect dependencies
- Extract repository structure

Technology:

- Tree-sitter

---

## 5. Database

Stores:

- User information
- Repository metadata
- Parsed code information
- Embeddings
- Knowledge graph
- Chat history

Technologies (planned):

- PostgreSQL
- Neo4j
- Vector Database (Qdrant)

---

# Folder Structure

```
arka/
│
├── frontend/
│
├── backend/
│
├── ai-service/
│
├── docker/
│
├── docs/
│
├── docker-compose.yml
│
└── README.md
```

---

# Future Pipeline

## Phase 1

- Project setup
- Backend
- Frontend
- AI Service

---

## Phase 2

- GitHub repository cloning
- Repository management

---

## Phase 3

- Tree-sitter integration
- AST generation

---

## Phase 4

- Knowledge extraction
- Dependency graph generation

---

## Phase 5

- Embedding generation
- Vector database indexing

---

## Phase 6

- Knowledge Graph creation

---

## Phase 7

- Retrieval-Augmented Generation (RAG)

---

## Phase 8

- AI Chat
- Code explanation
- Architecture analysis
- Code navigation
- Repository Q&A

---

# Technology Stack

| Layer | Technology |
|--------|------------|
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | Node.js, Express.js, TypeScript |
| AI Service | Python, FastAPI |
| Parser | Tree-sitter |
| Graph Database | Neo4j |
| Vector Database | Qdrant |
| Relational Database | PostgreSQL |
| Containerization | Docker |
| Version Control | Git, GitHub |
| LLM | OpenAI / Open-source models (planned) |

---

# Day 1 Status

## Completed

- Project architecture defined
- Monorepo structure created
- Backend initialized
- Frontend initialized
- AI service initialized
- Documentation created

## Upcoming

- Repository ingestion
- Tree-sitter integration
- AST generation
- Knowledge extraction
- Vector database
- Knowledge Graph
- RAG pipeline