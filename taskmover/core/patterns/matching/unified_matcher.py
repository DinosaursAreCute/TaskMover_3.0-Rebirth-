"""
Unified Pattern Matcher

Main matching engine that executes compiled patterns against file paths
and metadata with performance optimization and caching.
"""

import fnmatch
import re
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Set
from datetime import datetime

from ..interfaces import BasePatternComponent, IPatternMatcher, ICacheManager, IQueryExecutor
from ..models import Pattern, MatchResult, FileMetadata, PatternType, SYSTEM_GROUPS
from ..exceptions import PatternMatchError, QueryExecutionError
from ...conflict_resolution import ConflictManager, ConflictType, ConflictScope, ConflictContext
from ...conflict_resolution.models import ConflictItem
from ...conflict_resolution.enums import ConflictSource


class UnifiedPatternMatcher(BasePatternComponent, IPatternMatcher):
    """
    Unified pattern matching engine.
    
    Executes patterns against file paths and metadata with intelligent
    optimization and caching for performance.
    """
    
    def __init__(self, 
                 cache_manager: Optional[ICacheManager] = None,
                 query_executor: Optional[IQueryExecutor] = None,
                 conflict_manager: Optional[ConflictManager] = None):
        super().__init__("unified_matcher")
        
        self._cache_manager = cache_manager
        self._query_executor = query_executor
        self._conflict_manager = conflict_manager
        
        # Performance optimization settings
        self._max_files_for_content_scan = 10000
        self._cache_ttl_seconds = 300  # 5 minutes default
        
        # Compiled regex patterns for efficiency
        self._compiled_patterns = {}
        
        self._logger.info("UnifiedPatternMatcher initialized")
    
    def match(self, pattern: Pattern, file_paths: List[Path]) -> MatchResult:
        """
        Execute pattern matching against a list of file paths.
        
        Args:
            pattern: The pattern to match against
            file_paths: List of file paths to check
            
        Returns:
            MatchResult with matched files and performance metrics
            
        Raises:
            PatternMatchError: If matching fails
        """
        start_time = time.perf_counter()
        
        try:
            self._log_operation("match", 
                              pattern_id=str(pattern.id),
                              pattern_type=pattern.pattern_type.value,
                              file_count=len(file_paths))
            
            # Check cache first
            cache_key = self._generate_cache_key(pattern, file_paths)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                self._logger.debug("Cache hit for pattern matching")
                cached_result.cache_hit = True
                return cached_result
            
            # Perform matching based on pattern type
            matched_files = []
            
            if pattern.pattern_type == PatternType.GROUP_REFERENCE:
                matched_files = self._match_group_reference(pattern, file_paths)
            elif pattern.pattern_type == PatternType.SIMPLE_GLOB:
                matched_files = self._match_simple_glob(pattern, file_paths)
            elif pattern.pattern_type == PatternType.ENHANCED_GLOB:
                matched_files = self._match_enhanced_glob(pattern, file_paths)
            elif pattern.pattern_type == PatternType.ADVANCED_QUERY:
                matched_files = self._match_advanced_query(pattern, file_paths)
            elif pattern.pattern_type == PatternType.SHORTHAND:
                matched_files = self._match_shorthand(pattern, file_paths)
            else:
                # Fallback to simple glob
                matched_files = self._match_simple_glob(pattern, file_paths)
            
            # Calculate performance metrics
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            
            # Create result
            result = MatchResult(
                matched_files=matched_files,
                total_files_checked=len(file_paths),
                execution_time_ms=execution_time_ms,
                cache_hit=False,
                performance_metrics={
                    'pattern_type': pattern.pattern_type.value,
                    'complexity': pattern.pattern_complexity.value,
                    'match_ratio': len(matched_files) / len(file_paths) if file_paths else 0
                }
            )
            
            # Cache the result
            self._cache_result(cache_key, result)
            
            # Update pattern usage statistics
            pattern.update_usage_stats(execution_time_ms, cache_hit=False)
            
            self._log_performance("match", execution_time_ms,
                                pattern_type=pattern.pattern_type.value,
                                matched_count=len(matched_files),
                                total_count=len(file_paths))
            
            return result
            
        except Exception as e:
            self._log_error(e, "match", pattern_id=str(pattern.id))
            # Update pattern with error
            pattern.update_usage_stats(0, error=True)
            raise PatternMatchError(f"Pattern matching failed: {e}", pattern_id=str(pattern.id))
    
    def match_single(self, pattern: Pattern, file_path: Path) -> bool:
        """
        Check if a single file matches the pattern.
        
        Args:
            pattern: The pattern to check
            file_path: Single file path to check
            
        Returns:
            True if the file matches the pattern
        """
        try:
            result = self.match(pattern, [file_path])
            return len(result.matched_files) > 0
        except Exception as e:
            self._log_error(e, "match_single", 
                          pattern_id=str(pattern.id),
                          file_path=str(file_path))
            return False
    
    def _match_simple_glob(self, pattern: Pattern, file_paths: List[Path]) -> List[Path]:
        """Match simple glob patterns using fnmatch."""
        matched = []
        glob_pattern = pattern.user_expression
        
        for file_path in file_paths:
            if fnmatch.fnmatch(file_path.name, glob_pattern):
                matched.append(file_path)
        
        return matched
    
    def _match_enhanced_glob(self, pattern: Pattern, file_paths: List[Path]) -> List[Path]:
        """Match enhanced glob patterns with resolved tokens."""
        # The compiled_query should already have tokens resolved
        # by the parser, so treat it like a simple glob
        matched = []
        
        # Extract the pattern from the compiled query
        # Format: "name LIKE 'pattern'"
        if "LIKE '" in pattern.compiled_query:
            query_pattern = pattern.compiled_query.split("LIKE '")[1].rstrip("'")
            # Convert SQL LIKE pattern back to glob
            glob_pattern = query_pattern.replace('%', '*').replace('_', '?')
            
            for file_path in file_paths:
                if fnmatch.fnmatch(file_path.name, glob_pattern):
                    matched.append(file_path)
        
        return matched
    
    def _match_group_reference(self, pattern: Pattern, file_paths: List[Path]) -> List[Path]:
        """Match files against system group patterns."""
        matched = []
        
        # Extract group name from pattern
        group_name = None
        for ref_group in pattern.referenced_groups:
            group_name = f"@{ref_group}"
            break
        
        if not group_name or group_name not in SYSTEM_GROUPS:
            return matched
        
        group = SYSTEM_GROUPS[group_name]
        group_patterns = group.system_patterns
        
        for file_path in file_paths:
            # Check if file matches any pattern in the group
            for group_pattern in group_patterns:
                if fnmatch.fnmatch(file_path.name, group_pattern):
                    matched.append(file_path)
                    break  # Don't add the same file multiple times
        
        return matched
    
    def _match_advanced_query(self, pattern: Pattern, file_paths: List[Path]) -> List[Path]:
        """Match advanced query patterns with conditions."""
        if self._query_executor:
            try:
                # Use query executor if available
                from ..models import QueryAST  # This would be implemented
                # For now, fall back to basic implementation
                return self._match_advanced_fallback(pattern, file_paths)
            except Exception as e:
                self._logger.warning(f"Query executor failed, using fallback: {e}")
                return self._match_advanced_fallback(pattern, file_paths)
        else:
            return self._match_advanced_fallback(pattern, file_paths)
    
    def _match_advanced_fallback(self, pattern: Pattern, file_paths: List[Path]) -> List[Path]:
        """Fallback implementation for advanced queries."""
        matched = []
        query = pattern.compiled_query.lower()
        
        for file_path in file_paths:
            try:
                # Get file metadata
                file_metadata = self._get_file_metadata(file_path)
                
                # Simple pattern matching for common conditions
                file_matches = True
                
                # Parse basic conditions from query
                conditions = self._parse_basic_conditions(query)
                
                for condition in conditions:
                    if not self._evaluate_condition(condition, file_metadata):
                        file_matches = False
                        break
                
                if file_matches:
                    matched.append(file_path)
                    
            except Exception as e:
                self._logger.debug(f"Error evaluating {file_path}: {e}")
                continue
        
        return matched
    
    def _match_shorthand(self, pattern: Pattern, file_paths: List[Path]) -> List[Path]:
        """Match shorthand patterns like 'recent', 'large', etc."""
        matched = []
        shorthand = pattern.user_expression.lower()
        
        for file_path in file_paths:
            try:
                if not file_path.exists():
                    continue
                
                stat = file_path.stat()
                
                if shorthand == 'recent':
                    # Files modified in last 7 days
                    age_days = (datetime.now().timestamp() - stat.st_mtime) / 86400
                    if age_days <= 7:
                        matched.append(file_path)
                
                elif shorthand == 'large':
                    # Files larger than 100MB
                    if stat.st_size > 100 * 1024 * 1024:
                        matched.append(file_path)
                
                elif shorthand == 'empty':
                    # Empty files
                    if stat.st_size == 0:
                        matched.append(file_path)
                
                elif shorthand == 'hidden':
                    # Hidden files (start with . on Unix, have hidden attribute on Windows)
                    if file_path.name.startswith('.'):
                        matched.append(file_path)
                    # Could add Windows hidden attribute check here
                
                elif shorthand == 'duplicates':
                    # This would require more sophisticated duplicate detection
                    # For now, skip this complex case
                    pass
                    
            except Exception as e:
                self._logger.debug(f"Error checking {file_path} for shorthand {shorthand}: {e}")
                continue
        
        return matched
    
    def _get_file_metadata(self, file_path: Path) -> FileMetadata:
        """Get comprehensive metadata for a file."""
        try:
            stat = file_path.stat()
            
            return FileMetadata(
                path=file_path,
                name=file_path.name,
                extension=file_path.suffix.lower(),
                size=stat.st_size,
                created=datetime.fromtimestamp(stat.st_ctime),
                modified=datetime.fromtimestamp(stat.st_mtime),
                accessed=datetime.fromtimestamp(stat.st_atime),
                is_hidden=file_path.name.startswith('.'),
                is_readonly=not os.access(file_path, os.W_OK) if hasattr(file_path, 'exists') and file_path.exists() else False
            )
        except Exception as e:
            self._logger.debug(f"Error getting metadata for {file_path}: {e}")
            # Return minimal metadata on error
            return FileMetadata(
                path=file_path,
                name=file_path.name,
                extension=file_path.suffix.lower(),
                size=0,
                created=datetime.now(),
                modified=datetime.now(),
                accessed=datetime.now(),
                is_hidden=False,
                is_readonly=False
            )
    
    def _parse_basic_conditions(self, query: str) -> List[Dict[str, Any]]:
        """Parse basic conditions from a query string."""
        conditions = []
        
        # Simple regex patterns for common conditions
        patterns = [
            (r'name\s+like\s+[\'"]([^\'"]+)[\'"]', 'name_like'),
            (r'size\s*([><=]+)\s*(\d+)', 'size'),
            (r'modified\s*([><=]+)\s*(.+)', 'modified'),
            (r'extension\s*=\s*[\'"]([^\'"]+)[\'"]', 'extension')
        ]
        
        for pattern, condition_type in patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                if condition_type == 'name_like':
                    conditions.append({
                        'type': 'name_like',
                        'pattern': match.group(1)
                    })
                elif condition_type == 'size':
                    conditions.append({
                        'type': 'size',
                        'operator': match.group(1),
                        'value': int(match.group(2))
                    })
                elif condition_type == 'extension':
                    conditions.append({
                        'type': 'extension',
                        'value': match.group(1)
                    })
        
        return conditions
    
    def _evaluate_condition(self, condition: Dict[str, Any], metadata: FileMetadata) -> bool:
        """Evaluate a single condition against file metadata."""
        try:
            condition_type = condition['type']
            
            if condition_type == 'name_like':
                pattern = condition['pattern'].replace('%', '*').replace('_', '?')
                return fnmatch.fnmatch(metadata.name, pattern)
            
            elif condition_type == 'size':
                operator = condition['operator']
                value = condition['value']
                
                if operator == '>':
                    return metadata.size > value
                elif operator == '<':
                    return metadata.size < value
                elif operator == '>=':
                    return metadata.size >= value
                elif operator == '<=':
                    return metadata.size <= value
                elif operator == '=':
                    return metadata.size == value
            
            elif condition_type == 'extension':
                return metadata.extension == condition['value'].lower()
            
            return True
            
        except Exception as e:
            self._logger.debug(f"Error evaluating condition {condition}: {e}")
            return False
    
    def _generate_cache_key(self, pattern: Pattern, file_paths: List[Path]) -> str:
        """Generate a cache key for the pattern and file list."""
        # Create a hash of the pattern and file paths
        import hashlib
        
        pattern_data = f"{pattern.compiled_query}:{pattern.pattern_type.value}"
        files_data = ":".join(str(p) for p in sorted(file_paths))
        
        combined = f"{pattern_data}|{files_data}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[MatchResult]:
        """Get cached result if available and valid."""
        if not self._cache_manager:
            return None
        
        try:
            return self._cache_manager.get(cache_key)
        except Exception as e:
            self._logger.debug(f"Cache retrieval failed: {e}")
            return None
    
    def _cache_result(self, cache_key: str, result: MatchResult) -> None:
        """Cache the matching result."""
        if not self._cache_manager:
            return
        
        try:
            self._cache_manager.set(cache_key, result, self._cache_ttl_seconds)
        except Exception as e:
            self._logger.debug(f"Cache storage failed: {e}")
    
    def handle_pattern_conflicts(self, patterns: List[Pattern], file_paths: List[Path]) -> Dict[str, Any]:
        """
        Detect and handle conflicts between multiple patterns.
        
        Args:
            patterns: List of patterns that might conflict
            file_paths: File paths to check for conflicts
            
        Returns:
            Dictionary with conflict resolution results
        """
        if not self._conflict_manager:
            return {"conflicts_detected": 0, "conflicts_resolved": 0}
        
        conflicts_detected = 0
        conflicts_resolved = 0
        results = []
        
        try:
            # Check for pattern overlaps
            for i, pattern1 in enumerate(patterns):
                for j, pattern2 in enumerate(patterns[i+1:], i+1):
                    overlap_files = self._detect_pattern_overlap(pattern1, pattern2, file_paths)
                    
                    if overlap_files:
                        # Create conflict
                        existing_item = ConflictItem(
                            id=str(pattern1.id),
                            name=pattern1.name,
                            metadata={"pattern_type": pattern1.pattern_type.value}
                        )
                        
                        new_item = ConflictItem(
                            id=str(pattern2.id),
                            name=pattern2.name,
                            metadata={"pattern_type": pattern2.pattern_type.value}
                        )
                        
                        context = ConflictContext(
                            source_component=ConflictSource.PATTERN_SYSTEM,
                            additional_data={
                                "overlapping_files": [str(f) for f in overlap_files],
                                "overlap_count": len(overlap_files)
                            }
                        )
                        
                        conflict = self._conflict_manager.detect_conflict(
                            ConflictType.PATTERN_OVERLAP,
                            existing_item=existing_item,
                            new_item=new_item,
                            context=context,
                            scope=ConflictScope.PATTERN
                        )
                        
                        if conflict:
                            conflicts_detected += 1
                            
                            # Try to resolve if pattern has specific resolution strategy
                            resolution_strategy = None
                            
                            # Check if either pattern has a specific conflict resolution strategy
                            if hasattr(pattern1, 'conflict_resolution_strategy') and pattern1.conflict_resolution_strategy:
                                resolution_strategy = pattern1.conflict_resolution_strategy
                            elif hasattr(pattern2, 'conflict_resolution_strategy') and pattern2.conflict_resolution_strategy:
                                resolution_strategy = pattern2.conflict_resolution_strategy
                            
                            # Resolve the conflict
                            resolution_result = self._conflict_manager.resolve_conflict(
                                conflict, 
                                strategy=resolution_strategy
                            )
                            
                            if resolution_result.success:
                                conflicts_resolved += 1
                            
                            results.append({
                                "conflict_id": str(conflict.id),
                                "pattern1": pattern1.name,
                                "pattern2": pattern2.name,
                                "overlap_count": len(overlap_files),
                                "resolved": resolution_result.success,
                                "resolution_strategy": resolution_result.strategy_used.value if resolution_result.strategy_used else None
                            })
            
            return {
                "conflicts_detected": conflicts_detected,
                "conflicts_resolved": conflicts_resolved,
                "conflict_details": results
            }
            
        except Exception as e:
            self._logger.error(f"Error handling pattern conflicts: {e}")
            return {
                "conflicts_detected": conflicts_detected,
                "conflicts_resolved": conflicts_resolved,
                "error": str(e)
            }
    
    def _detect_pattern_overlap(self, pattern1: Pattern, pattern2: Pattern, file_paths: List[Path]) -> List[Path]:
        """Detect files that match both patterns (indicating overlap)."""
        try:
            # Get matches for both patterns
            matches1 = self._get_pattern_matches(pattern1, file_paths)
            matches2 = self._get_pattern_matches(pattern2, file_paths)
            
            # Find overlapping files
            overlap = []
            for file_path in matches1:
                if file_path in matches2:
                    overlap.append(file_path)
            
            return overlap
            
        except Exception as e:
            self._logger.debug(f"Error detecting pattern overlap: {e}")
            return []
    
    def _get_pattern_matches(self, pattern: Pattern, file_paths: List[Path]) -> List[Path]:
        """Get files that match a specific pattern."""
        try:
            if pattern.pattern_type == PatternType.SIMPLE_GLOB:
                return self._match_simple_glob(pattern, file_paths)
            elif pattern.pattern_type == PatternType.ENHANCED_GLOB:
                return self._match_enhanced_glob(pattern, file_paths)
            elif pattern.pattern_type == PatternType.ADVANCED_QUERY:
                return self._match_advanced_query(pattern, file_paths)
            elif pattern.pattern_type == PatternType.GROUP_REFERENCE:
                return self._match_group_reference(pattern, file_paths)
            elif pattern.pattern_type == PatternType.SHORTHAND:
                return self._match_shorthand(pattern, file_paths)
            else:
                return self._match_simple_glob(pattern, file_paths)
        except Exception:
            return []

    def invalidate_cache(self) -> None:
        """Invalidate all cached results."""
        if self._cache_manager:
            try:
                self._cache_manager.clear()
                self._logger.info("Pattern matcher cache cleared")
            except Exception as e:
                self._log_error(e, "cache_invalidation")


# Import os at module level for file permission checks
import os
