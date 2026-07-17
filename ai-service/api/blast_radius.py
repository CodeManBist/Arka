"""API endpoints for Blast Radius impact analysis."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from analysis.repository_parser import RepositoryParser
from analysis.diff_parser import DiffParser
from graph.call_graph_builder import CallGraphBuilder
from graph.import_graph_builder import ImportGraphBuilder
from graph.impact_traversal import ImpactTraversalEngine, ImpactResult

router = APIRouter(prefix="/api/blast-radius", tags=["blast-radius"])


class BlastRadiusRequest(BaseModel):
    """Request model for blast radius analysis."""
    repository_path: str
    symbol_name: str
    symbol_type: str = "function"
    file_path: Optional[str] = None
    max_depth: int = 3


class DiffAnalysisRequest(BaseModel):
    """Request model for diff-based analysis."""
    repository_path: str
    diff: str
    max_depth: int = 3


class RepositoryOverviewRequest(BaseModel):
    """Request model for repository overview."""
    repository_path: str


@router.post("/analyze")
async def analyze_impact(request: BlastRadiusRequest) -> Dict[str, Any]:
    """
    Analyze the impact of changing a specific symbol.
    
    This endpoint:
    1. Parses the repository
    2. Builds call and import graphs
    3. Traverses the graph to find affected code
    4. Returns impact analysis with risk scoring
    """
    try:
        # Parse the repository
        parser = RepositoryParser()
        repository_data = parser.parse_repository(request.repository_path)
        
        # Build graphs
        call_graph_builder = CallGraphBuilder()
        call_graph = call_graph_builder.build_from_repository(repository_data["repository"])
        
        import_graph_builder = ImportGraphBuilder()
        import_graph = import_graph_builder.build_from_repository(repository_data["repository"])
        
        # Analyze impact
        traversal_engine = ImpactTraversalEngine(call_graph, import_graph)
        impact_result = traversal_engine.analyze_impact(
            symbol_name=request.symbol_name,
            symbol_type=request.symbol_type,
            file_path=request.file_path,
            max_depth=request.max_depth
        )
        
        return {
            "success": True,
            "result": impact_result.to_dict(),
            "repository_stats": call_graph.get_statistics()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-diff")
async def analyze_diff_impact(request: DiffAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze the impact of a git diff.
    
    This is the killer feature: paste a git diff and get automatic
    impact analysis for all changed symbols.
    """
    try:
        # Parse the repository
        parser = RepositoryParser()
        repository_data = parser.parse_repository(request.repository_path)
        
        # Build graphs
        call_graph_builder = CallGraphBuilder()
        call_graph = call_graph_builder.build_from_repository(repository_data["repository"])
        
        import_graph_builder = ImportGraphBuilder()
        import_graph = import_graph_builder.build_from_repository(repository_data["repository"])
        
        # Parse the diff
        diff_parser = DiffParser()
        changed_symbols = diff_parser.parse_diff(request.diff)
        
        # Analyze impact for each changed symbol
        traversal_engine = ImpactTraversalEngine(call_graph, import_graph)
        impact_results = []
        
        for symbol_info in changed_symbols:
            impact_result = traversal_engine.analyze_impact(
                symbol_name=symbol_info.name,
                symbol_type=symbol_info.symbol_type,
                file_path=symbol_info.file_path,
                max_depth=request.max_depth
            )
            impact_results.append(impact_result.to_dict())
        
        # Aggregate results
        total_callers = sum(r["direct_callers"] + r["transitive_callers"] for r in impact_results)
        total_files = len(set(
            file for r in impact_results for file in r["affected_files"]
        ))
        
        # Determine overall risk level
        risk_levels = [r["risk_level"] for r in impact_results]
        if "critical" in risk_levels:
            overall_risk = "critical"
        elif "high" in risk_levels:
            overall_risk = "high"
        elif "medium" in risk_levels:
            overall_risk = "medium"
        else:
            overall_risk = "low"
        
        # Calculate average confidence
        avg_confidence = sum(r["confidence_score"] for r in impact_results) / len(impact_results) if impact_results else 1.0
        
        return {
            "success": True,
            "results": impact_results,
            "summary": {
                "total_changed_symbols": len(changed_symbols),
                "total_callers": total_callers,
                "total_files": total_files,
                "overall_risk": overall_risk,
                "average_confidence": avg_confidence,
                "changed_symbols": [s.to_dict() for s in changed_symbols]
            },
            "repository_stats": call_graph.get_statistics()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repository-overview")
async def get_repository_overview(request: RepositoryOverviewRequest) -> Dict[str, Any]:
    """
    Get an overview of a repository's structure and complexity.
    
    Returns:
    - Language breakdown
    - Function/class counts
    - Call graph statistics
    - Critical services identification
    """
    try:
        # Parse the repository
        parser = RepositoryParser()
        repository_data = parser.parse_repository(request.repository_path)
        
        # Build graphs
        call_graph_builder = CallGraphBuilder()
        call_graph = call_graph_builder.build_from_repository(repository_data["repository"])
        
        import_graph_builder = ImportGraphBuilder()
        import_graph = import_graph_builder.build_from_repository(repository_data["repository"])
        
        # Extract statistics
        repo = repository_data["repository"]
        files = repo.get("files", [])
        
        # Language breakdown
        language_counts: Dict[str, int] = {}
        for file_data in files:
            lang = file_data["language"]
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        # Function/class counts
        total_functions = sum(len(f.get("functions", [])) for f in files)
        total_classes = sum(len(f.get("classes", [])) for f in files)
        total_imports = sum(len(f.get("imports", [])) for f in files)
        total_exports = sum(len(f.get("exports", [])) for f in files)
        
        # Identify critical services (files with high fan-in)
        critical_services = []
        for node in import_graph.nodes.values():
            if node.in_degree > 5:  # High fan-in
                critical_services.append({
                    "file": node.file_path,
                    "name": node.name,
                    "in_degree": node.in_degree,
                    "out_degree": node.out_degree,
                    "centrality": node.centrality
                })
        
        # Sort by centrality
        critical_services.sort(key=lambda x: x["centrality"], reverse=True)
        
        return {
            "success": True,
            "repository": repo["repository"],
            "total_files": repo["total_files"],
            "language_breakdown": language_counts,
            "symbol_counts": {
                "functions": total_functions,
                "classes": total_classes,
                "imports": total_imports,
                "exports": total_exports
            },
            "call_graph_stats": call_graph.get_statistics(),
            "import_graph_stats": import_graph.get_statistics(),
            "critical_services": critical_services[:10]  # Top 10
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-pr-comment")
async def generate_pr_comment(request: DiffAnalysisRequest) -> Dict[str, Any]:
    """
    Generate a ready-to-paste GitHub PR review comment.
    
    This formats the impact analysis into a clean, readable
    comment that can be pasted directly into a GitHub PR review.
    """
    try:
        # First, get the diff analysis
        diff_result = await analyze_diff_impact(request)
        
        if not diff_result["success"]:
            return {"success": False, "error": "Failed to analyze diff"}
        
        summary = diff_result["summary"]
        results = diff_result["results"]
        
        # Generate PR comment
        comment_lines = []
        
        # Header
        comment_lines.append("## 🚨 Blast Radius Analysis")
        comment_lines.append("")
        
        # Overall risk
        risk_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        risk_emoji_str = risk_emoji.get(summary["overall_risk"], "⚪")
        
        comment_lines.append(f"**Risk: {risk_emoji_str} {summary['overall_risk'].upper()}**  ")
        comment_lines.append(f"**Confidence: {int(summary['average_confidence'] * 100)}%**")
        comment_lines.append("")
        
        # Summary statistics
        comment_lines.append(f"- **{summary['total_changed_symbols']} symbols changed**  ")
        comment_lines.append(f"- **{summary['total_callers']} callers affected**  ")
        comment_lines.append(f"- **{summary['total_files']} files impacted**")
        comment_lines.append("")
        
        # Changed symbols
        if summary["changed_symbols"]:
            comment_lines.append("### Changed Symbols:")
            for symbol in summary["changed_symbols"][:5]:  # Limit to first 5
                change_type_emoji = {
                    "added": "✅",
                    "modified": "🔄",
                    "deleted": "❌"
                }
                emoji = change_type_emoji.get(symbol["change_type"], "📝")
                comment_lines.append(f"- {emoji} `{symbol['name']}` ({symbol['type']}) in `{symbol['file']}`")
            comment_lines.append("")
        
        # Individual analyses
        if results:
            comment_lines.append("### Impact Details:")
            for i, result in enumerate(results[:3]):  # Limit to first 3
                risk_emoji_str = risk_emoji.get(result["risk_level"], "⚪")
                comment_lines.append(f"")
                comment_lines.append(f"**{i+1}. `{result['changed_symbol']}`** {risk_emoji_str}")
                comment_lines.append(f"   - Direct callers: {result['direct_callers']}")
                comment_lines.append(f"   - Transitive callers: {result['transitive_callers']}")
                comment_lines.append(f"   - Risk score: {result['risk_score']:.1f}")
            comment_lines.append("")
        
        # Suggested actions
        comment_lines.append("### Suggested Actions:")
        if summary["overall_risk"] in ["critical", "high"]:
            comment_lines.append("- 🛑 **DO NOT MERGE** without addressing the high-risk changes")
            comment_lines.append("- Add comprehensive tests for affected functionality")
            comment_lines.append("- Consider breaking this into smaller, safer PRs")
        elif summary["overall_risk"] == "medium":
            comment_lines.append("- 👀 Please review the affected files carefully")
            comment_lines.append("- Ensure all callers are updated appropriately")
        else:
            comment_lines.append("- ✅ Low risk change, but please verify the changes work as expected")
        
        comment_lines.append("")
        comment_lines.append("---")
        comment_lines.append("*Generated by [Blast Radius](https://github.com/CodeManBist/Arka)*")
        
        return {
            "success": True,
            "comment": "\n".join(comment_lines)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
