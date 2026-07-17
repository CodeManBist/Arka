Frontend
Next.js (React + TypeScript + Tailwind CSS)


 Express (Node.js Backend)


 FastAPI (AI Service)


 Repository Scanner


 Parser Factory


 AST (Tree-sitter)


 Extractors (Functions, Classes, Imports, Exports, Variables, References)


 Symbol Table Builder


 Graph Builders (Call Graph, Import Graph)


 Impact Traversal Engine (BFS/DFS with Risk Scoring)


 Diff Parser (Git diff analysis)


 Risk Engine (Fan-out, Criticality, Test Coverage)


 Blast Radius API Endpoints


 Codex (AI Summaries - planned)


Frontend (Visualization, Dashboards, PR Comments)

Detailed Flow:

1. User submits repository URL
    Repository Scanner clones and scans
    Parser Factory creates appropriate parser
    Tree-sitter generates AST
    Extractors pull out symbols
    Symbol Table Builder indexes everything
    Graph Builders create call and import graphs

2. User pastes git diff or selects symbol
    Diff Parser extracts changed symbols
    Impact Traversal Engine walks the graph
    Risk Engine calculates scores
    API returns structured impact analysis

3. Frontend displays results
    Repository Overview Dashboard
    Impact Analysis with risk cards
    Interactive Graph Visualization
    PR Comment Generation

Service Boundaries:
- Frontend: UI, user interaction, visualization
- Backend: API gateway, request routing
- AI Service: Core analysis, graph building, traversal