#!/usr/bin/env python3
"""
Test script to debug the CollectAI repository parsing.
This will help identify why edges are not being created.
"""

import sys
import logging
from pathlib import Path

# Configure logging to see debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Add the ai-service to the path
sys.path.insert(0, str(Path(__file__).parent / "ai-service"))

from analysis.repository_parser import RepositoryParser
from graph.call_graph_builder import CallGraphBuilder
from graph.import_graph_builder import ImportGraphBuilder

def test_repository(repo_path):
    """Test parsing a repository and building graphs."""
    print(f"\n{'='*80}")
    print(f"Testing repository: {repo_path}")
    print(f"{'='*80}\n")
    
    # Step 1: Parse the repository
    print("Step 1: Parsing repository...")
    parser = RepositoryParser()
    
    try:
        result = parser.parse_repository_no_cleanup(repo_path)
        repository_data = result["repository"]
        
        print(f"  Repository: {repository_data['repository']}")
        print(f"  Total files: {repository_data['total_files']}")
        print(f"  Files parsed: {len(repository_data['files'])}")
        
        # Show first few files
        print("\n  First 5 files:")
        for file_data in repository_data['files'][:5]:
            print(f"    - {file_data['path']} ({file_data['language']})")
            print(f"      Functions: {len(file_data.get('functions', []))}")
            print(f"      Imports: {len(file_data.get('imports', []))}")
            
            # Check if functions have bodies
            for func in file_data.get('functions', [])[:2]:
                has_body = bool(func.get('body', ''))
                body_len = len(func.get('body', ''))
                print(f"      Function '{func['name']}': has_body={has_body}, body_len={body_len}")
                if body_len < 100:
                    print(f"        Body: '{func.get('body', '')[:80]}...'")
        
    except Exception as e:
        print(f"  ERROR parsing repository: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: Build call graph
    print("\nStep 2: Building call graph...")
    call_graph_builder = CallGraphBuilder()
    
    try:
        call_graph = call_graph_builder.build_from_repository(repository_data)
        
        print(f"  Call graph nodes: {len(call_graph.nodes)}")
        print(f"  Call graph edges: {len(call_graph.edges)}")
        
        if len(call_graph.edges) == 0:
            print("  WARNING: No call edges created!")
            print("  Checking function bodies...")
            for file_data in repository_data['files'][:3]:
                for func in file_data.get('functions', [])[:2]:
                    body = func.get('body', '')
                    print(f"    Function '{func['name']}': body='{body[:50]}...'")
        
    except Exception as e:
        print(f"  ERROR building call graph: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 3: Build import graph
    print("\nStep 3: Building import graph...")
    import_graph_builder = ImportGraphBuilder()
    
    try:
        import_graph = import_graph_builder.build_from_repository(repository_data)
        
        print(f"  Import graph nodes: {len(import_graph.nodes)}")
        print(f"  Import graph edges: {len(import_graph.edges)}")
        
        if len(import_graph.edges) == 0:
            print("  WARNING: No import edges created!")
            print("  Checking imports...")
            for file_data in repository_data['files'][:3]:
                for imp in file_data.get('imports', [])[:3]:
                    print(f"    Import: path='{imp.get('path', '')}', name='{imp.get('name', '')}'")
        
    except Exception as e:
        print(f"  ERROR building import graph: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 4: Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Files parsed: {len(repository_data['files'])}")
    print(f"Total functions: {sum(len(f.get('functions', [])) for f in repository_data['files'])}")
    print(f"Total imports: {sum(len(f.get('imports', [])) for f in repository_data['files'])}")
    print(f"Call graph edges: {len(call_graph.edges)}")
    print(f"Import graph edges: {len(import_graph.edges)}")
    print("="*80)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_collectai.py <repository_path>")
        print("Example: python test_collectai.py C:/Users/sagar/OneDrive/Desktop/CollectAI")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    test_repository(repo_path)
