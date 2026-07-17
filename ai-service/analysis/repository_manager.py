"""
Repository Manager - Handles repository cloning, local path resolution, and cleanup.

This module provides a unified interface for accessing repositories, whether they are:
- Local file system paths
- GitHub URLs (https://github.com/owner/repo)
- Git URLs (git@github.com:owner/repo.git)

Features:
- Automatic detection of input type (local path vs URL)
- GitHub repository cloning to temporary directories
- Temporary directory cleanup
- Proper error handling and validation
- Support for both public and private repositories (with token)
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

import git
from git import Repo, GitCommandError, InvalidGitRepositoryError


class RepositoryManagerError(Exception):
    """Base exception for repository manager errors."""
    pass


class InvalidRepositoryError(RepositoryManagerError):
    """Raised when the repository path/URL is invalid."""
    pass


class CloneError(RepositoryManagerError):
    """Raised when repository cloning fails."""
    pass


class RepositoryManager:
    """
    Manages repository access, cloning, and cleanup.
    
    This class provides a unified interface for working with repositories
    regardless of whether they are local paths or remote URLs.
    """
    
    # Temporary directory for cloned repositories
    TEMP_DIR = Path(tempfile.gettempdir()) / "blast_radius_repos"
    
    # GitHub URL patterns
    GITHUB_HTTPS_PATTERN = re.compile(
        r'^https?://(?:www\.)?github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/)?$'
    )
    GITHUB_SSH_PATTERN = re.compile(
        r'^git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$'
    )
    
    # Git URL pattern
    GIT_URL_PATTERN = re.compile(
        r'^(https?|git)://[^/]+/[^/]+?\.git$'
    )
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize the repository manager.
        
        Args:
            github_token: Optional GitHub personal access token for private repos
        """
        self.github_token = github_token
        self._cloned_repos: Dict[str, Path] = {}  # repo_url -> temp_path
        self._active_repos: Dict[str, Path] = {}  # temp_path -> repo_url
        
        # Ensure temp directory exists
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        
        # Clean up any stale temp directories from previous runs
        self._cleanup_stale_temp_dirs()
    
    def _cleanup_stale_temp_dirs(self) -> None:
        """Clean up temporary directories from previous runs."""
        if not self.TEMP_DIR.exists():
            return
        
        for temp_dir in self.TEMP_DIR.iterdir():
            if temp_dir.is_dir():
                try:
                    # Check if directory is a git repo
                    if (temp_dir / ".git").exists():
                        shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception:
                    # Ignore errors during cleanup
                    pass
    
    def detect_input_type(self, input_path: str) -> str:
        """
        Detect whether the input is a local path or a repository URL.
        
        Args:
            input_path: The input string to analyze
            
        Returns:
            One of: 'local', 'github_https', 'github_ssh', 'git_url'
            
        Raises:
            InvalidRepositoryError: If the input cannot be identified
        """
        input_path = input_path.strip()
        
        # Check for GitHub HTTPS URL
        if self.GITHUB_HTTPS_PATTERN.match(input_path):
            return 'github_https'
        
        # Check for GitHub SSH URL
        if self.GITHUB_SSH_PATTERN.match(input_path):
            return 'github_ssh'
        
        # Check for generic Git URL
        if self.GIT_URL_PATTERN.match(input_path):
            return 'git_url'
        
        # Check if it's a valid local path
        if self._is_valid_local_path(input_path):
            return 'local'
        
        # Try to parse as URL
        try:
            parsed = urlparse(input_path)
            if parsed.scheme in ['http', 'https', 'git', 'ssh']:
                return 'git_url'
        except Exception:
            pass
        
        # If it looks like a path (contains / or \), treat as local
        if '/' in input_path or '\\' in input_path:
            return 'local'
        
        raise InvalidRepositoryError(
            f"Cannot determine input type for: {input_path}. "
            f"Expected a local path or a GitHub/Git URL."
        )
    
    def _is_valid_local_path(self, path: str) -> bool:
        """Check if a string is a valid local file system path."""
        try:
            # Try to resolve the path
            resolved = Path(path).resolve()
            
            # Check if it exists and is a directory
            if resolved.exists() and resolved.is_dir():
                return True
            
            # Check if parent exists (path might not exist yet but parent does)
            if resolved.parent.exists():
                return True
            
            # On Unix, check if it starts with /
            if path.startswith('/'):
                return True
            
            # On Windows, check if it has a drive letter
            if len(path) > 1 and path[1] == ':':
                return True
            
            return False
            
        except (OSError, ValueError):
            return False
    
    def resolve_repository(self, input_path: str) -> Tuple[Path, bool, Optional[str]]:
        """
        Resolve a repository input to a local file system path.
        
        For local paths, returns the path as-is.
        For GitHub URLs, clones the repository to a temporary directory.
        
        Args:
            input_path: Local path or GitHub URL
            
        Returns:
            Tuple of (resolved_path, is_temporary, original_url)
            - resolved_path: Path to the repository on disk
            - is_temporary: True if the repo was cloned to temp dir
            - original_url: The original URL if input was a URL, None otherwise
            
        Raises:
            InvalidRepositoryError: If the input is invalid
            CloneError: If cloning fails
        """
        input_type = self.detect_input_type(input_path)
        
        if input_type == 'local':
            # Local path - resolve and validate
            resolved_path = Path(input_path).resolve()
            
            if not resolved_path.exists():
                raise InvalidRepositoryError(
                    f"Local path does not exist: {input_path}"
                )
            
            if not resolved_path.is_dir():
                raise InvalidRepositoryError(
                    f"Local path is not a directory: {input_path}"
                )
            
            return (resolved_path, False, None)
        
        elif input_type in ['github_https', 'github_ssh', 'git_url']:
            # Remote URL - clone to temporary directory
            return self._clone_repository(input_path, input_type)
        
        else:
            raise InvalidRepositoryError(
                f"Unsupported input type: {input_type}"
            )
    
    def _clone_repository(
        self, 
        url: str, 
        input_type: str
    ) -> Tuple[Path, bool, str]:
        """
        Clone a GitHub repository to a temporary directory.
        
        Args:
            url: The GitHub URL to clone
            input_type: The detected input type
            
        Returns:
            Tuple of (temp_path, True, original_url)
        """
        # Normalize the URL
        normalized_url = self._normalize_github_url(url, input_type)
        
        # Check if already cloned
        if normalized_url in self._cloned_repos:
            temp_path = self._cloned_repos[normalized_url]
            if temp_path.exists():
                return (temp_path, True, normalized_url)
        
        # Generate unique temporary directory name
        repo_name = self._extract_repo_name(normalized_url)
        unique_id = str(uuid.uuid4())[:8]
        temp_dir_name = f"{repo_name}_{unique_id}"
        temp_path = self.TEMP_DIR / temp_dir_name
        
        # Ensure temp directory exists
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Clone the repository
            clone_url = self._get_clone_url(normalized_url, input_type)
            
            # Configure git with token if available
            git_config = {}
            if self.github_token:
                # Use token for authentication
                if 'github.com' in clone_url:
                    # For HTTPS URLs, insert token
                    if clone_url.startswith('https://'):
                        clone_url = clone_url.replace(
                            'https://',
                            f'https://oauth2:{self.github_token}@'
                        )
            
            # Perform the clone
            repo = Repo.clone_from(
                clone_url,
                str(temp_path),
                depth=1,  # Shallow clone for speed
                branch='main',  # Default to main branch
                **git_config
            )
            
            # Store the mapping
            self._cloned_repos[normalized_url] = temp_path
            self._active_repos[str(temp_path)] = normalized_url
            
            return (temp_path, True, normalized_url)
            
        except GitCommandError as e:
            # Clean up temp directory if it was created
            if temp_path.exists():
                shutil.rmtree(temp_path, ignore_errors=True)
            
            raise CloneError(
                f"Failed to clone repository {url}: {str(e)}"
            )
        except InvalidGitRepositoryError as e:
            # Clean up temp directory if it was created
            if temp_path.exists():
                shutil.rmtree(temp_path, ignore_errors=True)
            
            raise CloneError(
                f"Invalid Git repository URL: {url}"
            )
        except Exception as e:
            # Clean up temp directory if it was created
            if temp_path.exists():
                shutil.rmtree(temp_path, ignore_errors=True)
            
            raise CloneError(
                f"Unexpected error cloning repository {url}: {str(e)}"
            )
    
    def _normalize_github_url(self, url: str, input_type: str) -> str:
        """Normalize GitHub URL to standard HTTPS format."""
        if input_type == 'github_https':
            # Already HTTPS
            return url.rstrip('/')
        
        elif input_type == 'github_ssh':
            # Convert SSH to HTTPS
            match = self.GITHUB_SSH_PATTERN.match(url)
            if match:
                owner, repo = match.groups()
                return f"https://github.com/{owner}/{repo}"
        
        elif input_type == 'git_url':
            # Try to convert to HTTPS
            if url.startswith('git@'):
                # SSH-style git URL
                match = self.GITHUB_SSH_PATTERN.match(url)
                if match:
                    owner, repo = match.groups()
                    return f"https://github.com/{owner}/{repo}"
            else:
                # HTTPS git URL
                return url.replace('.git', '').rstrip('/')
        
        return url
    
    def _extract_repo_name(self, url: str) -> str:
        """Extract repository name from URL."""
        # Remove .git suffix
        url = url.rstrip('/').replace('.git', '')
        
        # Get last part of URL
        parts = url.split('/')
        if parts:
            return parts[-1]
        
        return "repo"
    
    def _get_clone_url(self, url: str, input_type: str) -> str:
        """Get the appropriate clone URL for git."""
        if input_type == 'github_https':
            return url
        
        elif input_type == 'github_ssh':
            return url
        
        elif input_type == 'git_url':
            if url.startswith('git@'):
                return url
            else:
                return url
        
        return url
    
    def cleanup_repository(self, temp_path: Path) -> bool:
        """
        Clean up a temporary repository directory.
        
        Args:
            temp_path: Path to the temporary directory
            
        Returns:
            True if cleanup was successful, False otherwise
        """
        if not temp_path.exists():
            return True
        
        try:
            # Remove from tracking
            temp_path_str = str(temp_path)
            if temp_path_str in self._active_repos:
                url = self._active_repos.pop(temp_path_str)
                if url in self._cloned_repos:
                    del self._cloned_repos[url]
            
            # Remove the directory
            shutil.rmtree(temp_path, ignore_errors=True)
            return True
            
        except Exception:
            return False
    
    def cleanup_all(self) -> Dict[str, bool]:
        """
        Clean up all temporary repositories.
        
        Returns:
            Dictionary mapping URLs to cleanup success status
        """
        results = {}
        
        for url, temp_path in list(self._cloned_repos.items()):
            results[url] = self.cleanup_repository(temp_path)
        
        self._cloned_repos.clear()
        self._active_repos.clear()
        
        return results
    
    def validate_repository(self, path: Path) -> bool:
        """
        Validate that a path contains a valid repository.
        
        Args:
            path: Path to validate
            
        Returns:
            True if the path is a valid repository
        """
        if not path.exists():
            return False
        
        if not path.is_dir():
            return False
        
        # Check for common repository markers
        markers = [
            ".git",
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
            "README.md",
        ]
        
        for marker in markers:
            if (path / marker).exists():
                return True
        
        # Check if it's a git repository
        try:
            Repo(path)
            return True
        except (InvalidGitRepositoryError, GitCommandError):
            pass
        
        # If it has source files, consider it valid
        source_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx']
        for ext in source_extensions:
            if list(path.rglob(f'*{ext}')):
                return True
        
        return False
    
    def get_repository_info(self, path: Path) -> Dict[str, Any]:
        """
        Get information about a repository.
        
        Args:
            path: Path to the repository
            
        Returns:
            Dictionary with repository information
        """
        info: Dict[str, Any] = {
            "path": str(path),
            "exists": path.exists(),
            "is_dir": path.is_dir(),
            "name": path.name,
            "is_git_repo": False,
            "branches": [],
            "current_branch": None,
            "commit_hash": None,
            "commit_message": None,
        }
        
        if not path.exists():
            return info
        
        # Try to get git information
        try:
            repo = Repo(path)
            info["is_git_repo"] = True
            info["current_branch"] = repo.active_branch.name
            info["commit_hash"] = repo.head.commit.hexsha
            info["commit_message"] = repo.head.commit.message.strip()
            info["branches"] = [ref.name for ref in repo.branches]
            
        except (InvalidGitRepositoryError, GitCommandError):
            pass
        
        return info
    
    def list_files(self, path: Path, extensions: Optional[list[str]] = None) -> list[Path]:
        """
        List all files in a repository with optional extension filtering.
        
        Args:
            path: Path to the repository
            extensions: Optional list of extensions to filter by
            
        Returns:
            List of file paths
        """
        if not path.exists():
            return []
        
        files = []
        for file_path in path.rglob('*'):
            if file_path.is_file():
                if extensions:
                    if file_path.suffix.lower() in extensions:
                        files.append(file_path)
                else:
                    files.append(file_path)
        
        return files


# Global instance for convenience
_repository_manager: Optional[RepositoryManager] = None


def get_repository_manager(github_token: Optional[str] = None) -> RepositoryManager:
    """Get or create the global repository manager instance."""
    global _repository_manager
    
    if _repository_manager is None:
        _repository_manager = RepositoryManager(github_token)
    
    return _repository_manager


def reset_repository_manager() -> None:
    """Reset the global repository manager instance."""
    global _repository_manager
    
    if _repository_manager is not None:
        _repository_manager.cleanup_all()
        _repository_manager = None
