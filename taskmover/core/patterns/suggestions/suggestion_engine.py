"""
Pattern Suggestion Engine

Provides intelligent pattern suggestions based on workspace analysis,
user patterns, and common file organization structures.
"""

import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta

from ..interfaces import BasePatternComponent, ISuggestionEngine, IWorkspaceAnalyzer
from ..models import Pattern, PatternType, SYSTEM_GROUPS
from ..exceptions import SuggestionError


class PatternSuggestionEngine(BasePatternComponent, ISuggestionEngine):
    """
    Intelligent pattern suggestion engine.
    
    Analyzes workspace structure and usage patterns to provide
    contextually relevant pattern suggestions.
    """
    
    def __init__(self, workspace_analyzer: Optional[IWorkspaceAnalyzer] = None):
        super().__init__("suggestion_engine")
        
        self._workspace_analyzer = workspace_analyzer or WorkspaceAnalyzer()
        
        # Common pattern templates
        self._pattern_templates = {
            'extension': '*.{ext}',
            'prefix': '{prefix}*',
            'suffix': '*{suffix}',
            'contains': '*{text}*',
            'date_range': '*$DATE*',
            'versioned': '*v{version}*',
            'backup': '*.{ext}.bak',
            'temporary': '*.tmp',
            'recent': 'modified > today-7',
            'large': 'size > 10MB',
            'images': '@media AND (*.jpg OR *.png OR *.gif)',
            'documents': '@documents',
            'code': '@code'
        }
        
        # Pattern complexity scoring
        self._complexity_scores = {
            'simple_glob': 1,
            'enhanced_glob': 3,
            'advanced_query': 5,
            'group_reference': 2,
            'shorthand': 2
        }
        
        self._logger.info("PatternSuggestionEngine initialized")
    
    def suggest_patterns(self, workspace_path: Path, partial_input: str = "") -> List[Dict]:
        """
        Generate context-aware pattern suggestions.
        
        Args:
            workspace_path: Path to workspace to analyze
            partial_input: Optional partial user input for context
            
        Returns:
            List of pattern suggestions with metadata
        """
        try:
            self._log_operation("suggest_patterns", 
                              workspace_path=str(workspace_path),
                              partial_input=partial_input)
            
            suggestions = []
            
            # Analyze workspace
            workspace_analysis = self._workspace_analyzer.analyze(workspace_path)
            
            # Generate different types of suggestions
            suggestions.extend(self._suggest_based_on_files(workspace_analysis))
            suggestions.extend(self._suggest_based_on_input(partial_input, workspace_analysis))
            suggestions.extend(self._suggest_common_patterns())
            suggestions.extend(self._suggest_system_groups())
            suggestions.extend(self._suggest_date_patterns())
            suggestions.extend(self._suggest_size_patterns(workspace_analysis))
            
            # Filter and rank suggestions
            suggestions = self._filter_suggestions(suggestions, partial_input)
            suggestions = self._rank_suggestions(suggestions, workspace_analysis)
            
            # Limit to reasonable number
            suggestions = suggestions[:20]
            
            self._logger.debug(f"Generated {len(suggestions)} pattern suggestions")
            
            return suggestions
            
        except Exception as e:
            self._log_error(e, "suggest_patterns", workspace_path=str(workspace_path))
            return []
    
    def get_completions(self, partial_input: str) -> List[str]:
        """
        Get auto-completion suggestions for partial input.
        
        Args:
            partial_input: Partial pattern input
            
        Returns:
            List of completion strings
        """
        try:
            self._log_operation("get_completions", partial_input=partial_input)
            
            completions = []
            
            # Token completions
            if '$' in partial_input:
                completions.extend(self._get_token_completions(partial_input))
            
            # Group reference completions
            if '@' in partial_input:
                completions.extend(self._get_group_completions(partial_input))
            
            # Operator completions
            if any(op in partial_input.lower() for op in ['and', 'or', 'not']):
                completions.extend(self._get_operator_completions(partial_input))
            
            # Function completions
            if '(' in partial_input:
                completions.extend(self._get_function_completions(partial_input))
            
            # Remove duplicates and sort
            completions = sorted(set(completions))
            
            self._logger.debug(f"Generated {len(completions)} completions")
            
            return completions
            
        except Exception as e:
            self._log_error(e, "get_completions", partial_input=partial_input)
            return []
    
    def _suggest_based_on_files(self, analysis: Dict) -> List[Dict]:
        """Generate suggestions based on actual files in workspace."""
        suggestions = []
        
        # Extension-based patterns
        common_extensions = analysis.get('common_extensions', [])
        for ext, count in common_extensions[:10]:  # Top 10 extensions
            suggestions.append({
                'pattern': f'*.{ext}',
                'type': PatternType.SIMPLE_GLOB,
                'description': f'All {ext.upper()} files ({count} found)',
                'category': 'files',
                'confidence': min(0.9, count / 100),  # Higher confidence for more files
                'usage_count': count
            })
        
        # Directory-based patterns
        common_dirs = analysis.get('common_directories', [])
        for dir_name, count in common_dirs[:5]:
            suggestions.append({
                'pattern': f'{dir_name}/*',
                'type': PatternType.SIMPLE_GLOB,
                'description': f'All files in {dir_name} directory',
                'category': 'directories',
                'confidence': 0.7,
                'usage_count': count
            })
        
        # Size-based patterns
        if analysis.get('large_files_count', 0) > 0:
            suggestions.append({
                'pattern': 'size > 10MB',
                'type': PatternType.ADVANCED_QUERY,
                'description': f'Large files (>{analysis.get("large_files_count", 0)} found)',
                'category': 'size',
                'confidence': 0.8
            })
        
        return suggestions
    
    def _suggest_based_on_input(self, partial_input: str, analysis: Dict) -> List[Dict]:
        """Generate suggestions based on partial user input."""
        suggestions = []
        
        if not partial_input:
            return suggestions
        
        partial_lower = partial_input.lower()
        
        # Complete file extensions
        if partial_input.startswith('*.'):
            ext_part = partial_input[2:]
            common_extensions = analysis.get('common_extensions', [])
            
            for ext, count in common_extensions:
                if ext.startswith(ext_part):
                    suggestions.append({
                        'pattern': f'*.{ext}',
                        'type': PatternType.SIMPLE_GLOB,
                        'description': f'All {ext.upper()} files',
                        'category': 'completion',
                        'confidence': 0.9
                    })
        
        # Complete group references
        if partial_input.startswith('@'):
            group_part = partial_input[1:].lower()
            for group_name in SYSTEM_GROUPS.keys():
                clean_name = group_name[1:]  # Remove @ prefix
                if clean_name.startswith(group_part):
                    group = SYSTEM_GROUPS[group_name]
                    suggestions.append({
                        'pattern': group_name,
                        'type': PatternType.GROUP_REFERENCE,
                        'description': group.description,
                        'category': 'groups',
                        'confidence': 0.95
                    })
        
        # Suggest enhancements for simple patterns
        if '*' in partial_input and '$' not in partial_input:
            # Suggest adding date tokens
            suggestions.append({
                'pattern': partial_input.replace('*', '*$DATE*'),
                'type': PatternType.ENHANCED_GLOB,
                'description': 'Add date token to pattern',
                'category': 'enhancement',
                'confidence': 0.6
            })
        
        return suggestions
    
    def _suggest_common_patterns(self) -> List[Dict]:
        """Generate suggestions for common pattern types."""
        common_patterns = [
            {
                'pattern': 'recent',
                'type': PatternType.SHORTHAND,
                'description': 'Files modified in the last 7 days',
                'category': 'time',
                'confidence': 0.8
            },
            {
                'pattern': 'large',
                'type': PatternType.SHORTHAND,
                'description': 'Files larger than 100MB',
                'category': 'size',
                'confidence': 0.7
            },
            {
                'pattern': 'empty',
                'type': PatternType.SHORTHAND,
                'description': 'Empty files (0 bytes)',
                'category': 'size',
                'confidence': 0.6
            },
            {
                'pattern': 'hidden',
                'type': PatternType.SHORTHAND,
                'description': 'Hidden files and directories',
                'category': 'attributes',
                'confidence': 0.5
            },
            {
                'pattern': '*$DATE*',
                'type': PatternType.ENHANCED_GLOB,
                'description': 'Files with today\'s date in filename',
                'category': 'dynamic',
                'confidence': 0.7
            },
            {
                'pattern': 'report_$DATE*.pdf',
                'type': PatternType.ENHANCED_GLOB,
                'description': 'Daily report PDFs',
                'category': 'dynamic',
                'confidence': 0.6
            }
        ]
        
        return common_patterns
    
    def _suggest_system_groups(self) -> List[Dict]:
        """Generate suggestions for system-defined groups."""
        suggestions = []
        
        for group_name, group in SYSTEM_GROUPS.items():
            suggestions.append({
                'pattern': group_name,
                'type': PatternType.GROUP_REFERENCE,
                'description': group.description,
                'category': 'groups',
                'confidence': 0.8,
                'icon': group.icon,
                'color': group.color
            })
        
        return suggestions
    
    def _suggest_date_patterns(self) -> List[Dict]:
        """Generate date-related pattern suggestions."""
        suggestions = [
            {
                'pattern': 'modified > today-7',
                'type': PatternType.ADVANCED_QUERY,
                'description': 'Files modified in the last week',
                'category': 'time',
                'confidence': 0.8
            },
            {
                'pattern': 'modified > today-30',
                'type': PatternType.ADVANCED_QUERY,
                'description': 'Files modified in the last month',
                'category': 'time',
                'confidence': 0.7
            },
            {
                'pattern': 'created > $DATE{%Y-%m-01}',
                'type': PatternType.ENHANCED_GLOB,
                'description': 'Files created this month',
                'category': 'time',
                'confidence': 0.6
            }
        ]
        
        return suggestions
    
    def _suggest_size_patterns(self, analysis: Dict) -> List[Dict]:
        """Generate size-based pattern suggestions."""
        suggestions = []
        
        avg_size = analysis.get('average_file_size', 0)
        
        if avg_size > 0:
            # Suggest patterns based on file size distribution
            if avg_size > 10 * 1024 * 1024:  # > 10MB average
                suggestions.append({
                    'pattern': 'size < 1MB',
                    'type': PatternType.ADVANCED_QUERY,
                    'description': 'Small files (less than 1MB)',
                    'category': 'size',
                    'confidence': 0.7
                })
            
            suggestions.append({
                'pattern': f'size > {int(avg_size * 2)}',
                'type': PatternType.ADVANCED_QUERY,
                'description': 'Files larger than average',
                'category': 'size',
                'confidence': 0.6
            })
        
        return suggestions
    
    def _get_token_completions(self, partial_input: str) -> List[str]:
        """Get token completion suggestions."""
        completions = []
        
        # Find the token being typed
        token_match = re.search(r'\$([A-Z_]*)$', partial_input)
        if token_match:
            token_prefix = token_match.group(1)
            
            available_tokens = [
                'DATE', 'TIME', 'DATETIME', 'USER', 'YEAR', 'MONTH', 'DAY',
                'HOUR', 'MINUTE', 'HOSTNAME', 'PROJECT', 'RANDOM', 'UUID'
            ]
            
            for token in available_tokens:
                if token.startswith(token_prefix):
                    completion = partial_input.replace(f'${token_prefix}', f'${token}')
                    completions.append(completion)
        
        return completions
    
    def _get_group_completions(self, partial_input: str) -> List[str]:
        """Get group reference completion suggestions."""
        completions = []
        
        # Find the group being typed
        group_match = re.search(r'@([a-z_]*)$', partial_input, re.IGNORECASE)
        if group_match:
            group_prefix = group_match.group(1).lower()
            
            for group_name in SYSTEM_GROUPS.keys():
                clean_name = group_name[1:]  # Remove @ prefix
                if clean_name.startswith(group_prefix):
                    completion = partial_input.replace(f'@{group_prefix}', group_name)
                    completions.append(completion)
        
        return completions
    
    def _get_operator_completions(self, partial_input: str) -> List[str]:
        """Get operator completion suggestions."""
        completions = []
        
        operators = ['AND', 'OR', 'NOT']
        conditions = ['size >', 'size <', 'modified >', 'created >', 'name LIKE']
        
        # Add space before operators if needed
        for op in operators:
            if partial_input.endswith(' '):
                completions.append(partial_input + op + ' ')
        
        # Add common conditions
        for condition in conditions:
            if partial_input.endswith(' '):
                completions.append(partial_input + condition + ' ')
        
        return completions
    
    def _get_function_completions(self, partial_input: str) -> List[str]:
        """Get function completion suggestions."""
        completions = []
        
        functions = [
            'contains(',
            'startswith(',
            'endswith(',
            'matches(',
            'DATE_SUB(',
            'DATE_ADD('
        ]
        
        for func in functions:
            if '(' in partial_input and not partial_input.endswith(')'):
                # Inside function call
                if 'contains(' in partial_input and not partial_input.endswith('"'):
                    completions.append(partial_input + '"')
        
        return completions
    
    def _filter_suggestions(self, suggestions: List[Dict], partial_input: str) -> List[Dict]:
        """Filter suggestions based on relevance and partial input."""
        if not partial_input:
            return suggestions
        
        filtered = []
        partial_lower = partial_input.lower()
        
        for suggestion in suggestions:
            pattern = suggestion['pattern'].lower()
            
            # Check if suggestion is relevant to partial input
            if (partial_lower in pattern or
                pattern.startswith(partial_lower) or
                any(word in pattern for word in partial_lower.split())):
                filtered.append(suggestion)
        
        return filtered
    
    def _rank_suggestions(self, suggestions: List[Dict], analysis: Dict) -> List[Dict]:
        """Rank suggestions by relevance and confidence."""
        def suggestion_score(suggestion):
            score = suggestion.get('confidence', 0.5)
            
            # Boost based on category
            category_boosts = {
                'files': 1.2,
                'groups': 1.1,
                'completion': 1.3,
                'time': 1.0,
                'size': 0.9
            }
            
            category = suggestion.get('category', 'general')
            score *= category_boosts.get(category, 1.0)
            
            # Boost based on usage count
            usage_count = suggestion.get('usage_count', 0)
            if usage_count > 0:
                score *= min(1.5, 1.0 + usage_count / 100)
            
            return score
        
        # Sort by score in descending order
        suggestions.sort(key=suggestion_score, reverse=True)
        
        return suggestions


class WorkspaceAnalyzer(BasePatternComponent, IWorkspaceAnalyzer):
    """
    Analyzes workspace structure to understand file patterns.
    
    Provides insights into file types, sizes, dates, and organization
    to help generate better pattern suggestions.
    """
    
    def __init__(self):
        super().__init__("workspace_analyzer")
        
        self._ignore_patterns = {
            '.git', '.svn', '.hg', '__pycache__', 'node_modules',
            '.vscode', '.idea', '.vs', 'target', 'build', 'dist'
        }
        
        self._logger.info("WorkspaceAnalyzer initialized")
    
    def analyze(self, workspace_path: Path) -> Dict:
        """
        Analyze workspace and return file pattern insights.
        
        Args:
            workspace_path: Path to workspace to analyze
            
        Returns:
            Dictionary with analysis results
        """
        try:
            self._log_operation("analyze_workspace", workspace_path=str(workspace_path))
            
            if not workspace_path.exists() or not workspace_path.is_dir():
                return {}
            
            analysis = {
                'total_files': 0,
                'total_size': 0,
                'common_extensions': [],
                'common_directories': [],
                'size_distribution': {},
                'date_distribution': {},
                'large_files_count': 0,
                'empty_files_count': 0,
                'hidden_files_count': 0,
                'average_file_size': 0,
                'newest_file_date': None,
                'oldest_file_date': None
            }
            
            # Collect file information
            file_info = self._collect_file_info(workspace_path)
            
            # Analyze extensions
            analysis['common_extensions'] = self._analyze_extensions(file_info)
            
            # Analyze directories
            analysis['common_directories'] = self._analyze_directories(file_info)
            
            # Analyze sizes
            analysis.update(self._analyze_sizes(file_info))
            
            # Analyze dates
            analysis.update(self._analyze_dates(file_info))
            
            # Calculate totals
            analysis['total_files'] = len(file_info)
            analysis['total_size'] = sum(info['size'] for info in file_info)
            analysis['average_file_size'] = (
                analysis['total_size'] / analysis['total_files']
                if analysis['total_files'] > 0 else 0
            )
            
            self._logger.debug(f"Analyzed {analysis['total_files']} files in workspace")
            
            return analysis
            
        except Exception as e:
            self._log_error(e, "analyze_workspace", workspace_path=str(workspace_path))
            return {}
    
    def get_common_extensions(self, workspace_path: Path) -> List[str]:
        """Get most common file extensions in workspace."""
        try:
            analysis = self.analyze(workspace_path)
            return [ext for ext, _ in analysis.get('common_extensions', [])]
        except Exception as e:
            self._log_error(e, "get_common_extensions")
            return []
    
    def _collect_file_info(self, workspace_path: Path) -> List[Dict]:
        """Collect information about all files in workspace."""
        file_info = []
        
        try:
            for root, dirs, files in os.walk(workspace_path):
                # Skip ignored directories
                dirs[:] = [d for d in dirs if d not in self._ignore_patterns]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    try:
                        stat = file_path.stat()
                        
                        info = {
                            'path': file_path,
                            'name': file,
                            'extension': file_path.suffix.lower().lstrip('.'),
                            'directory': Path(root).name,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime),
                            'created': datetime.fromtimestamp(stat.st_ctime),
                            'is_hidden': file.startswith('.'),
                            'is_empty': stat.st_size == 0
                        }
                        
                        file_info.append(info)
                        
                    except (OSError, PermissionError):
                        # Skip files we can't access
                        continue
                        
        except Exception as e:
            self._logger.debug(f"Error collecting file info: {e}")
        
        return file_info
    
    def _analyze_extensions(self, file_info: List[Dict]) -> List[Tuple[str, int]]:
        """Analyze file extensions and return most common ones."""
        extension_counts = Counter()
        
        for info in file_info:
            ext = info['extension']
            if ext:  # Skip files without extensions
                extension_counts[ext] += 1
        
        return extension_counts.most_common(20)
    
    def _analyze_directories(self, file_info: List[Dict]) -> List[Tuple[str, int]]:
        """Analyze directory names and return most common ones."""
        directory_counts = Counter()
        
        for info in file_info:
            directory = info['directory']
            if directory and directory not in self._ignore_patterns:
                directory_counts[directory] += 1
        
        return directory_counts.most_common(10)
    
    def _analyze_sizes(self, file_info: List[Dict]) -> Dict:
        """Analyze file size distribution."""
        sizes = [info['size'] for info in file_info]
        
        large_files = sum(1 for size in sizes if size > 100 * 1024 * 1024)  # > 100MB
        empty_files = sum(1 for size in sizes if size == 0)
        
        size_ranges = {
            'tiny': sum(1 for size in sizes if 0 < size <= 1024),  # 0-1KB
            'small': sum(1 for size in sizes if 1024 < size <= 1024 * 1024),  # 1KB-1MB
            'medium': sum(1 for size in sizes if 1024 * 1024 < size <= 100 * 1024 * 1024),  # 1MB-100MB
            'large': large_files  # > 100MB
        }
        
        return {
            'large_files_count': large_files,
            'empty_files_count': empty_files,
            'size_distribution': size_ranges
        }
    
    def _analyze_dates(self, file_info: List[Dict]) -> Dict:
        """Analyze file date distribution."""
        if not file_info:
            return {}
        
        modified_dates = [info['modified'] for info in file_info]
        created_dates = [info['created'] for info in file_info]
        
        now = datetime.now()
        recent_cutoff = now - timedelta(days=7)
        
        recent_files = sum(1 for date in modified_dates if date > recent_cutoff)
        
        return {
            'newest_file_date': max(modified_dates).isoformat(),
            'oldest_file_date': min(modified_dates).isoformat(),
            'recent_files_count': recent_files,
            'date_distribution': {
                'last_week': recent_files,
                'last_month': sum(1 for date in modified_dates if date > now - timedelta(days=30)),
                'last_year': sum(1 for date in modified_dates if date > now - timedelta(days=365))
            }
        }
