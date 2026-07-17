"""Parse git diffs to extract changed symbols."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ChangedSymbol:
    """Represents a symbol that was changed in a diff."""
    
    name: str
    symbol_type: str  # 'function', 'class', 'method', 'variable', 'constant', 'export'
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted'
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    old_signature: Optional[str] = None
    new_signature: Optional[str] = None
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.symbol_type,
            "file": self.file_path,
            "change_type": self.change_type,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "old_signature": self.old_signature,
            "new_signature": self.new_signature,
        }


class DiffParser:
    """
    Parse git diffs to extract information about changed symbols.
    
    This parser can detect:
    - Added, modified, and deleted functions
    - Added, modified, and deleted classes
    - Added, modified, and deleted variables
    - Added, modified, and deleted exports
    - Changed function signatures (parameters, return types)
    - Added/removed imports
    """
    
    def __init__(self):
        """Initialize the diff parser."""
        # Patterns for detecting different types of changes
        self.function_patterns = [
            # Python
            r'(def\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            # JavaScript/TypeScript
            r'(function\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            r'(const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*function\s*\(',
            r'(const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\([^)]*\)\s*=>',
            # Method definitions
            r'(class\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\{[^}]*\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
        ]
        
        self.class_patterns = [
            r'(class\s+)([a-zA-Z_][a-zA-Z0-9_]*)',
        ]
        
        self.variable_patterns = [
            # Python: variable = value
            r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*.+',
            # JavaScript/TypeScript: const/let/var variable = value
            r'(const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[=;]',
            # Export const variable = value
            r'export\s+(const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[=;]',
            # Default export
            r'export\s+default\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        ]
        
        self.import_patterns = [
            r'(import\s+.*?\s+from\s+["\'])',
            r'(import\s+["\'].*?["\'])',
            r'(require\s*\(\s*["\'].*?["\']\s*\))',
        ]
        
        self.export_patterns = [
            r'export\s+(function|class|const|let|var|default)',
            r'export\s+\{.*?\}',
        ]
    
    def parse_diff(self, diff: str) -> List[ChangedSymbol]:
        """
        Parse a git diff and extract changed symbols.
        
        Args:
            diff: The git diff string
            
        Returns:
            List of ChangedSymbol objects
        """
        changed_symbols: List[ChangedSymbol] = []
        lines = diff.split('\n')
        
        current_file: Optional[str] = None
        current_change_type: Optional[str] = None
        
        # Track old and new content for each file
        file_changes: Dict[str, Dict[str, Any]] = {}
        
        for line in lines:
            # Parse file header
            if line.startswith('diff --git'):
                parts = line.split()
                if len(parts) >= 4:
                    old_file = parts[2]
                    new_file = parts[3]
                    current_file = new_file if new_file != '/dev/null' else old_file
                    
                    # Determine change type
                    if old_file == '/dev/null':
                        current_change_type = 'added'
                    elif new_file == '/dev/null':
                        current_change_type = 'deleted'
                    else:
                        current_change_type = 'modified'
                    
                    file_changes[current_file] = {
                        'old_lines': [],
                        'new_lines': [],
                        'change_type': current_change_type
                    }
            
            # Parse old file header
            elif line.startswith('---'):
                if current_file:
                    file_path = line[4:].strip()
                    if file_path and file_path != '/dev/null':
                        current_file = file_path
            
            # Parse new file header
            elif line.startswith('+++'):
                if current_file:
                    file_path = line[4:].strip()
                    if file_path and file_path != '/dev/null':
                        current_file = file_path
            
            # Parse hunks
            elif line.startswith('@@'):
                # Extract line numbers
                match = re.match(r'@@\s+-(\d+)(?:,\d+)?\s+\+(\d+)(?:,\d+)?\s+@@', line)
                if match:
                    old_start = int(match.group(1))
                    new_start = int(match.group(2))
                    
                    if current_file and current_file in file_changes:
                        file_changes[current_file]['old_start'] = old_start
                        file_changes[current_file]['new_start'] = new_start
            
            # Parse removed lines
            elif line.startswith('-') and not line.startswith('---'):
                if current_file and current_file in file_changes:
                    file_changes[current_file]['old_lines'].append(line[1:])
            
            # Parse added lines
            elif line.startswith('+') and not line.startswith('+++'):
                if current_file and current_file in file_changes:
                    file_changes[current_file]['new_lines'].append(line[1:])
        
        # Analyze changes for each file
        for file_path, changes in file_changes.items():
            old_lines = changes.get('old_lines', [])
            new_lines = changes.get('new_lines', [])
            change_type = changes.get('change_type', 'modified')
            
            # Extract changed symbols from this file
            symbols = self._extract_symbols_from_file_changes(
                file_path, old_lines, new_lines, change_type
            )
            changed_symbols.extend(symbols)
        
        return changed_symbols
    
    def _extract_symbols_from_file_changes(
        self,
        file_path: str,
        old_lines: List[str],
        new_lines: List[str],
        change_type: str
    ) -> List[ChangedSymbol]:
        """Extract changed symbols from file changes."""
        symbols: List[ChangedSymbol] = []
        
        # Combine old and new lines for analysis
        all_old = '\n'.join(old_lines)
        all_new = '\n'.join(new_lines)
        
        # Detect function changes
        symbols.extend(self._extract_function_changes(
            file_path, all_old, all_new, change_type
        ))
        
        # Detect class changes
        symbols.extend(self._extract_class_changes(
            file_path, all_old, all_new, change_type
        ))
        
        # Detect variable changes
        symbols.extend(self._extract_variable_changes(
            file_path, all_old, all_new, change_type
        ))
        
        # Detect export changes
        symbols.extend(self._extract_export_changes(
            file_path, all_old, all_new, change_type
        ))
        
        # Detect import changes
        symbols.extend(self._extract_import_changes(
            file_path, all_old, all_new, change_type
        ))
        
        return symbols
    
    def _extract_function_changes(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
        change_type: str
    ) -> List[ChangedSymbol]:
        """Extract function changes from content."""
        symbols: List[ChangedSymbol] = []
        
        # Find all function definitions in old and new content
        old_functions = self._find_functions(old_content)
        new_functions = self._find_functions(new_content)
        
        # Detect added functions
        old_function_names = {f['name'] for f in old_functions}
        new_function_names = {f['name'] for f in new_functions}
        
        added_functions = new_function_names - old_function_names
        deleted_functions = old_function_names - new_function_names
        common_functions = old_function_names & new_function_names
        
        # Added functions
        for func in new_functions:
            if func['name'] in added_functions:
                symbols.append(ChangedSymbol(
                    name=func['name'],
                    symbol_type='function',
                    file_path=file_path,
                    change_type='added',
                    start_line=func.get('start_line'),
                    end_line=func.get('end_line'),
                    new_signature=func.get('signature')
                ))
        
        # Deleted functions
        for func in old_functions:
            if func['name'] in deleted_functions:
                symbols.append(ChangedSymbol(
                    name=func['name'],
                    symbol_type='function',
                    file_path=file_path,
                    change_type='deleted',
                    start_line=func.get('start_line'),
                    end_line=func.get('end_line'),
                    old_signature=func.get('signature')
                ))
        
        # Modified functions (signature changes)
        for func_name in common_functions:
            old_func = next((f for f in old_functions if f['name'] == func_name), None)
            new_func = next((f for f in new_functions if f['name'] == func_name), None)
            
            if old_func and new_func:
                old_sig = old_func.get('signature', '')
                new_sig = new_func.get('signature', '')
                
                if old_sig != new_sig:
                    symbols.append(ChangedSymbol(
                        name=func_name,
                        symbol_type='function',
                        file_path=file_path,
                        change_type='modified',
                        start_line=new_func.get('start_line'),
                        end_line=new_func.get('end_line'),
                        old_signature=old_sig,
                        new_signature=new_sig
                    ))
        
        return symbols
    
    def _find_functions(self, content: str) -> List[Dict[str, Any]]:
        """Find all function definitions in content."""
        functions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            for pattern in self.function_patterns:
                match = re.search(pattern, line)
                if match:
                    func_type = match.group(1).strip()
                    func_name = match.group(2).strip()
                    
                    # Skip anonymous functions
                    if func_name and func_name != '_':
                        # Extract signature (entire line or up to opening brace)
                        signature_match = re.search(r'(def|function|const|let|var)\s+[^\n]*', line)
                        signature = signature_match.group(0) if signature_match else line.strip()
                        
                        functions.append({
                            'name': func_name,
                            'type': func_type,
                            'signature': signature,
                            'start_line': i + 1
                        })
                        break
        
        return functions
    
    def _extract_class_changes(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
        change_type: str
    ) -> List[ChangedSymbol]:
        """Extract class changes from content."""
        symbols: List[ChangedSymbol] = []
        
        # Find all class definitions in old and new content
        old_classes = self._find_classes(old_content)
        new_classes = self._find_classes(new_content)
        
        # Detect added classes
        old_class_names = {c['name'] for c in old_classes}
        new_class_names = {c['name'] for c in new_classes}
        
        added_classes = new_class_names - old_class_names
        deleted_classes = old_class_names - new_class_names
        common_classes = old_class_names & new_class_names
        
        # Added classes
        for cls in new_classes:
            if cls['name'] in added_classes:
                symbols.append(ChangedSymbol(
                    name=cls['name'],
                    symbol_type='class',
                    file_path=file_path,
                    change_type='added',
                    start_line=cls.get('start_line'),
                    end_line=cls.get('end_line'),
                    new_signature=cls.get('signature')
                ))
        
        # Deleted classes
        for cls in old_classes:
            if cls['name'] in deleted_classes:
                symbols.append(ChangedSymbol(
                    name=cls['name'],
                    symbol_type='class',
                    file_path=file_path,
                    change_type='deleted',
                    start_line=cls.get('start_line'),
                    end_line=cls.get('end_line'),
                    old_signature=cls.get('signature')
                ))
        
        # Modified classes
        for class_name in common_classes:
            old_cls = next((c for c in old_classes if c['name'] == class_name), None)
            new_cls = next((c for c in new_classes if c['name'] == class_name), None)
            
            if old_cls and new_cls:
                old_sig = old_cls.get('signature', '')
                new_sig = new_cls.get('signature', '')
                
                if old_sig != new_sig:
                    symbols.append(ChangedSymbol(
                        name=class_name,
                        symbol_type='class',
                        file_path=file_path,
                        change_type='modified',
                        start_line=new_cls.get('start_line'),
                        end_line=new_cls.get('end_line'),
                        old_signature=old_sig,
                        new_signature=new_sig
                    ))
        
        return symbols
    
    def _find_classes(self, content: str) -> List[Dict[str, Any]]:
        """Find all class definitions in content."""
        classes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            for pattern in self.class_patterns:
                match = re.search(pattern, line)
                if match:
                    class_type = match.group(1).strip()
                    class_name = match.group(2).strip()
                    
                    if class_name:
                        signature_match = re.search(r'class\s+[^\n]*', line)
                        signature = signature_match.group(0) if signature_match else line.strip()
                        
                        classes.append({
                            'name': class_name,
                            'type': class_type,
                            'signature': signature,
                            'start_line': i + 1
                        })
                        break
        
        return classes
    
    def _extract_variable_changes(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
        change_type: str
    ) -> List[ChangedSymbol]:
        """Extract variable changes from content."""
        symbols: List[ChangedSymbol] = []
        
        # Find all variables in old and new content
        old_variables = self._find_variables(old_content)
        new_variables = self._find_variables(new_content)
        
        # Detect added variables
        old_var_names = {v['name'] for v in old_variables}
        new_var_names = {v['name'] for v in new_variables}
        
        added_vars = new_var_names - old_var_names
        deleted_vars = old_var_names - new_var_names
        common_vars = old_var_names & new_var_names
        
        # Added variables
        for var in new_variables:
            if var['name'] in added_vars:
                symbols.append(ChangedSymbol(
                    name=var['name'],
                    symbol_type='variable',
                    file_path=file_path,
                    change_type='added',
                    start_line=var.get('start_line'),
                    new_signature=var.get('signature')
                ))
        
        # Deleted variables
        for var in old_variables:
            if var['name'] in deleted_vars:
                symbols.append(ChangedSymbol(
                    name=var['name'],
                    symbol_type='variable',
                    file_path=file_path,
                    change_type='deleted',
                    start_line=var.get('start_line'),
                    old_signature=var.get('signature')
                ))
        
        # Modified variables
        for var_name in common_vars:
            old_var = next((v for v in old_variables if v['name'] == var_name), None)
            new_var = next((v for v in new_variables if v['name'] == var_name), None)
            
            if old_var and new_var:
                old_sig = old_var.get('signature', '')
                new_sig = new_var.get('signature', '')
                
                if old_sig != new_sig:
                    symbols.append(ChangedSymbol(
                        name=var_name,
                        symbol_type='variable',
                        file_path=file_path,
                        change_type='modified',
                        start_line=new_var.get('start_line'),
                        old_signature=old_sig,
                        new_signature=new_sig
                    ))
        
        return symbols
    
    def _find_variables(self, content: str) -> List[Dict[str, Any]]:
        """Find all variable definitions in content."""
        variables = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            for pattern in self.variable_patterns:
                match = re.search(pattern, line)
                if match:
                    # Handle different pattern types
                    groups = match.groups()
                    
                    # Skip if it's a function definition (def, function, etc.)
                    if any(kw in line for kw in ['def ', 'function ', 'class ']):
                        continue
                    
                    # Extract variable name
                    var_name = None
                    for group in groups:
                        if group and group not in ['const', 'let', 'var', 'export', 'default']:
                            var_name = group
                            break
                    
                    if var_name and var_name != '_':
                        # Extract signature
                        signature = line.strip()
                        
                        variables.append({
                            'name': var_name,
                            'signature': signature,
                            'start_line': i + 1
                        })
                        break
        
        return variables
    
    def _extract_export_changes(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
        change_type: str
    ) -> List[ChangedSymbol]:
        """Extract export changes from content."""
        symbols: List[ChangedSymbol] = []
        
        # Find all exports in old and new content
        old_exports = self._find_exports(old_content)
        new_exports = self._find_exports(new_content)
        
        # Detect added exports
        old_export_names = {e['name'] for e in old_exports}
        new_export_names = {e['name'] for e in new_exports}
        
        added_exports = new_export_names - old_export_names
        deleted_exports = old_export_names - new_export_names
        
        # Added exports
        for exp in new_exports:
            if exp['name'] in added_exports:
                symbols.append(ChangedSymbol(
                    name=exp['name'],
                    symbol_type='export',
                    file_path=file_path,
                    change_type='added',
                    start_line=exp.get('start_line'),
                    new_signature=exp.get('signature')
                ))
        
        # Deleted exports
        for exp in old_exports:
            if exp['name'] in deleted_exports:
                symbols.append(ChangedSymbol(
                    name=exp['name'],
                    symbol_type='export',
                    file_path=file_path,
                    change_type='deleted',
                    start_line=exp.get('start_line'),
                    old_signature=exp.get('signature')
                ))
        
        return symbols
    
    def _find_exports(self, content: str) -> List[Dict[str, Any]]:
        """Find all exports in content."""
        exports = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            for pattern in self.export_patterns:
                match = re.search(pattern, line)
                if match:
                    # Extract export name
                    export_name = None
                    
                    # Try to extract from named exports: export { name }
                    named_match = re.search(r'export\s+\{([^}]+)\}', line)
                    if named_match:
                        named_exports = named_match.group(1).split(',')
                        for name in named_exports:
                            name = name.strip()
                            if name:
                                exports.append({
                                    'name': name,
                                    'signature': line.strip(),
                                    'start_line': i + 1
                                })
                        continue
                    
                    # Try to extract from export function/class
                    func_match = re.search(r'export\s+(function|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
                    if func_match:
                        export_name = func_match.group(2)
                    else:
                        # Try default export
                        default_match = re.search(r'export\s+default\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
                        if default_match:
                            export_name = default_match.group(1)
                        else:
                            # Try export const/let/var
                            var_match = re.search(r'export\s+(const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
                            if var_match:
                                export_name = var_match.group(2)
                    
                    if export_name:
                        exports.append({
                            'name': export_name,
                            'signature': line.strip(),
                            'start_line': i + 1
                        })
                    break
        
        return exports
    
    def _extract_import_changes(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
        change_type: str
    ) -> List[ChangedSymbol]:
        """Extract import changes from content."""
        symbols: List[ChangedSymbol] = []
        
        # Find all imports in old and new content
        old_imports = self._find_imports(old_content)
        new_imports = self._find_imports(new_content)
        
        # Detect added imports
        old_import_paths = {imp['path'] for imp in old_imports}
        new_import_paths = {imp['path'] for imp in new_imports}
        
        added_imports = new_import_paths - old_import_paths
        deleted_imports = old_import_paths - new_import_paths
        
        # Added imports
        for imp in new_imports:
            if imp['path'] in added_imports:
                symbols.append(ChangedSymbol(
                    name=imp.get('name', imp['path']),
                    symbol_type='import',
                    file_path=file_path,
                    change_type='added',
                    new_signature=imp.get('statement')
                ))
        
        # Deleted imports
        for imp in old_imports:
            if imp['path'] in deleted_imports:
                symbols.append(ChangedSymbol(
                    name=imp.get('name', imp['path']),
                    symbol_type='import',
                    file_path=file_path,
                    change_type='deleted',
                    old_signature=imp.get('statement')
                ))
        
        return symbols
    
    def _find_imports(self, content: str) -> List[Dict[str, Any]]:
        """Find all import statements in content."""
        imports = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            for pattern in self.import_patterns:
                match = re.search(pattern, line)
                if match:
                    import_statement = match.group(0)
                    
                    # Extract path
                    path_match = re.search(r'["\']([^"\']+)["\']', import_statement)
                    import_path = path_match.group(1) if path_match else ''
                    
                    # Extract name (for named imports)
                    name_match = re.search(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', import_statement)
                    import_name = name_match.group(1) if name_match else ''
                    
                    imports.append({
                        'name': import_name,
                        'path': import_path,
                        'statement': import_statement,
                        'start_line': i + 1
                    })
                    break
        
        return imports
