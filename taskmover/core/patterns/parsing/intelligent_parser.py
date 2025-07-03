"""
Intelligent Pattern Parser

Main unified parser that automatically detects input type and converts
user patterns into internal query representations.
"""

import re
import time
from typing import Dict, List, Optional, Set
from pathlib import Path

from ..interfaces import BasePatternComponent, IPatternParser, ITokenResolver
from ..models import (
    ParsedPattern, PatternType, PatternComplexity, ValidationResult
)
from ..exceptions import (
    PatternParseError, PatternSyntaxError, TokenResolutionError
)


class IntelligentPatternParser(BasePatternComponent, IPatternParser):
    """
    Main unified parser for the pattern system.
    
    Automatically detects input type and converts user patterns into
    optimized internal query representations.
    """
    
    def __init__(self, token_resolver: Optional[ITokenResolver] = None):
        super().__init__("intelligent_parser")
        self._token_resolver = token_resolver
        
        # Compile regex patterns for efficient pattern detection
        self._compile_detection_patterns()
        
        # Pattern complexity scoring weights
        self._complexity_weights = {
            'basic_glob': 1,
            'wildcards': 2,
            'tokens': 3,
            'conditions': 5,
            'logical_ops': 4,
            'functions': 6,
            'nested_groups': 7
        }
        
        self._logger.info("IntelligentPatternParser initialized")
    
    def _compile_detection_patterns(self) -> None:
        """Compile regex patterns for efficient type detection."""
        try:
            # Group reference patterns
            self._group_ref_pattern = re.compile(r'^@\w+$')
            
            # Token patterns
            self._token_pattern = re.compile(r'\$[A-Z_]+(?:\{[^}]*\})?')
            
            # Advanced query indicators
            self._advanced_indicators = [
                re.compile(r'\b(?:AND|OR|NOT)\b', re.IGNORECASE),
                re.compile(r'\b(?:size|modified|created|type)\s*[<>=]'),
                re.compile(r'\b(?:contains|matches|startswith|endswith)\s*\('),
                re.compile(r'\bdate\s*[<>=]'),
                re.compile(r'\b(?:today|yesterday|week|month|year)\b', re.IGNORECASE)
            ]
            
            # Simple glob patterns
            self._simple_glob_pattern = re.compile(r'^[a-zA-Z0-9_\-.*?[\]{}]+$')
            
            # Enhanced glob with tokens
            self._enhanced_glob_pattern = re.compile(r'^[a-zA-Z0-9_\-.*?[\]{}$]+$')
            
            self._logger.debug("Pattern detection regex compiled successfully")
            
        except Exception as e:
            self._log_error(e, "pattern_compilation")
            raise PatternParseError(f"Failed to compile detection patterns: {e}", "compilation_error")
    
    def parse(self, user_input: str) -> ParsedPattern:
        """
        Parse user input into a structured pattern representation.
        
        Args:
            user_input: The pattern string entered by the user
            
        Returns:
            ParsedPattern with compiled query and metadata
            
        Raises:
            PatternParseError: If parsing fails
        """
        start_time = time.perf_counter()
        
        try:
            self._log_operation("parse", input_pattern=user_input)
            
            # Input validation        if not user_input or not user_input.strip():
            raise PatternSyntaxError("Empty pattern input", user_input)
            
            cleaned_input = user_input.strip()
            
            # Detect pattern type
            pattern_type = self._detect_pattern_type(cleaned_input)
            self._logger.debug(f"Detected pattern type: {pattern_type}")
            
            # Parse based on type
            if pattern_type == PatternType.GROUP_REFERENCE:
                parsed = self._parse_group_reference(cleaned_input)
            elif pattern_type == PatternType.SIMPLE_GLOB:
                parsed = self._parse_simple_glob(cleaned_input)
            elif pattern_type == PatternType.ENHANCED_GLOB:
                parsed = self._parse_enhanced_glob(cleaned_input)
            elif pattern_type == PatternType.ADVANCED_QUERY:
                parsed = self._parse_advanced_query(cleaned_input)
            elif pattern_type == PatternType.SHORTHAND:
                parsed = self._parse_shorthand(cleaned_input)
            else:
                # Fallback to simple glob
                parsed = self._parse_simple_glob(cleaned_input)
            
            # Calculate complexity
            complexity = self._calculate_complexity(parsed)
            parsed.complexity = complexity
            
            # Validate the parsed pattern
            validation = self.validate_syntax(cleaned_input)
            parsed.validation_result = validation
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            self._log_performance("parse", duration_ms, pattern_type=pattern_type.value)
            
            return parsed
            
        except PatternSyntaxError:
            raise
        except Exception as e:
            self._log_error(e, "parse", input_pattern=user_input)
            raise PatternParseError(f"Failed to parse pattern '{user_input}': {e}", user_input)
    
    def validate_syntax(self, user_input: str) -> ValidationResult:
        """
        Validate pattern syntax without full parsing.
        
        Args:
            user_input: The pattern string to validate
            
        Returns:
            ValidationResult with validation details
        """
        try:
            self._log_operation("validate_syntax", input_pattern=user_input)
            
            errors = []
            warnings = []
            suggestions = []
            
            if not user_input or not user_input.strip():
                errors.append("Pattern cannot be empty")
                return ValidationResult(False, errors)
            
            cleaned_input = user_input.strip()
            
            # Check for common syntax errors
            errors.extend(self._check_syntax_errors(cleaned_input))
            
            # Check for potential issues
            warnings.extend(self._check_warnings(cleaned_input))
            
            # Generate suggestions
            suggestions.extend(self._generate_suggestions(cleaned_input))
            
            # Calculate performance score
            performance_score = self._estimate_performance(cleaned_input)
            
            is_valid = len(errors) == 0
            
            result = ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                performance_score=performance_score
            )
            
            self._logger.debug(f"Validation result: valid={is_valid}, errors={len(errors)}, warnings={len(warnings)}")
            
            return result
            
        except Exception as e:
            self._log_error(e, "validate_syntax", input_pattern=user_input)
            return ValidationResult(
                False, 
                [f"Validation error: {e}"]
            )
    
    def _detect_pattern_type(self, pattern: str) -> PatternType:
        """Detect the type of pattern from user input."""
        # Group reference: @media, @documents, etc.
        if self._group_ref_pattern.match(pattern):
            return PatternType.GROUP_REFERENCE
        
        # Check for advanced query indicators
        for indicator in self._advanced_indicators:
            if indicator.search(pattern):
                return PatternType.ADVANCED_QUERY
        
        # Check for tokens
        if self._token_pattern.search(pattern):
            return PatternType.ENHANCED_GLOB
        
        # Check for common shorthand patterns
        if pattern in ['recent', 'large', 'empty', 'duplicates', 'hidden']:
            return PatternType.SHORTHAND
        
        # Default to simple glob
        return PatternType.SIMPLE_GLOB
    
    def _parse_simple_glob(self, pattern: str) -> ParsedPattern:
        """Parse simple glob patterns like *.txt, file*.pdf."""
        # Convert glob to SQL-like query
        compiled_query = self._glob_to_query(pattern)
        
        return ParsedPattern(
            original_input=pattern,
            pattern_type=PatternType.SIMPLE_GLOB,
            complexity=PatternComplexity.SIMPLE,
            compiled_query=compiled_query,
            tokens_used=set(),
            referenced_groups=set(),
            estimated_complexity=1
        )
    
    def _parse_enhanced_glob(self, pattern: str) -> ParsedPattern:
        """Parse enhanced glob patterns with tokens."""
        # Extract tokens
        tokens_used = set(self._token_pattern.findall(pattern))
        
        # Resolve tokens if resolver is available
        resolved_pattern = pattern
        if self._token_resolver:
            try:
                resolved_pattern = self._token_resolver.resolve_tokens(pattern)
            except Exception as e:
                self._logger.warning(f"Token resolution failed: {e}")
                # Continue with unresolved pattern
        
        # Convert to query
        compiled_query = self._glob_to_query(resolved_pattern)
        
        return ParsedPattern(
            original_input=pattern,
            pattern_type=PatternType.ENHANCED_GLOB,
            complexity=PatternComplexity.ENHANCED,
            compiled_query=compiled_query,
            tokens_used=tokens_used,
            referenced_groups=set(),
            estimated_complexity=3
        )
    
    def _parse_advanced_query(self, pattern: str) -> ParsedPattern:
        """Parse advanced query patterns with conditions."""
        # This is a simplified implementation
        # In a full implementation, this would parse the query syntax
        
        # Extract referenced groups
        referenced_groups = set(re.findall(r'@\w+', pattern))
        
        # Extract tokens
        tokens_used = set(self._token_pattern.findall(pattern))
        
        # For now, pass through as-is with some basic transformations
        compiled_query = self._advanced_to_query(pattern)
        
        return ParsedPattern(
            original_input=pattern,
            pattern_type=PatternType.ADVANCED_QUERY,
            complexity=PatternComplexity.ADVANCED,
            compiled_query=compiled_query,
            tokens_used=tokens_used,
            referenced_groups=referenced_groups,
            estimated_complexity=7
        )
    
    def _parse_group_reference(self, pattern: str) -> ParsedPattern:
        """Parse group reference patterns like @media."""
        group_name = pattern[1:]  # Remove @ prefix
        referenced_groups = {group_name}
        
        # Generate query for group patterns
        compiled_query = f"GROUP_REF('{group_name}')"
        
        return ParsedPattern(
            original_input=pattern,
            pattern_type=PatternType.GROUP_REFERENCE,
            complexity=PatternComplexity.SIMPLE,
            compiled_query=compiled_query,
            tokens_used=set(),
            referenced_groups=referenced_groups,
            estimated_complexity=2
        )
    
    def _parse_shorthand(self, pattern: str) -> ParsedPattern:
        """Parse shorthand patterns like 'recent', 'large'."""
        # Map shorthand to queries
        shorthand_mapping = {
            'recent': "modified > DATE_SUB(NOW(), INTERVAL 7 DAY)",
            'large': "size > 100000000",  # 100MB
            'empty': "size = 0",
            'duplicates': "DUPLICATE_CHECK(checksum)",
            'hidden': "is_hidden = true"
        }
        
        compiled_query = shorthand_mapping.get(pattern, f"name LIKE '%{pattern}%'")
        
        return ParsedPattern(
            original_input=pattern,
            pattern_type=PatternType.SHORTHAND,
            complexity=PatternComplexity.ENHANCED,
            compiled_query=compiled_query,
            tokens_used=set(),
            referenced_groups=set(),
            estimated_complexity=4
        )
    
    def _glob_to_query(self, pattern: str) -> str:
        """Convert glob pattern to SQL-like query."""
        # Escape special SQL characters
        escaped = pattern.replace("'", "''")
        
        # Convert glob wildcards to SQL wildcards
        query_pattern = escaped.replace('*', '%').replace('?', '_')
        
        return f"name LIKE '{query_pattern}'"
    
    def _advanced_to_query(self, pattern: str) -> str:
        """Convert advanced pattern to optimized query."""
        # This is a simplified implementation
        # In practice, this would involve proper parsing and AST generation
        
        query = pattern
        
        # Replace date functions
        query = re.sub(r'today-(\d+)', r"DATE_SUB(NOW(), INTERVAL \1 DAY)", query)
        query = re.sub(r'today\+(\d+)', r"DATE_ADD(NOW(), INTERVAL \1 DAY)", query)
        
        # Replace size units
        query = re.sub(r'(\d+)MB', lambda m: str(int(m.group(1)) * 1024 * 1024), query)
        query = re.sub(r'(\d+)KB', lambda m: str(int(m.group(1)) * 1024), query)
        query = re.sub(r'(\d+)GB', lambda m: str(int(m.group(1)) * 1024 * 1024 * 1024), query)
        
        return query
    
    def _calculate_complexity(self, parsed: ParsedPattern) -> PatternComplexity:
        """Calculate pattern complexity based on features used."""
        score = 0
        
        # Base score from pattern type
        if parsed.pattern_type == PatternType.SIMPLE_GLOB:
            score += 1
        elif parsed.pattern_type == PatternType.ENHANCED_GLOB:
            score += 3
        elif parsed.pattern_type == PatternType.ADVANCED_QUERY:
            score += 7
        elif parsed.pattern_type == PatternType.GROUP_REFERENCE:
            score += 2
        elif parsed.pattern_type == PatternType.SHORTHAND:
            score += 4
        
        # Add complexity for tokens
        score += len(parsed.tokens_used) * 2
        
        # Add complexity for group references
        score += len(parsed.referenced_groups) * 2
        
        # Determine complexity level
        if score <= 3:
            return PatternComplexity.SIMPLE
        elif score <= 6:
            return PatternComplexity.ENHANCED
        elif score <= 10:
            return PatternComplexity.ADVANCED
        else:
            return PatternComplexity.COMPOSITE
    
    def _check_syntax_errors(self, pattern: str) -> List[str]:
        """Check for common syntax errors."""
        errors = []
        
        # Check for unmatched parentheses
        if pattern.count('(') != pattern.count(')'):
            errors.append("Unmatched parentheses")
        
        # Check for unmatched brackets
        if pattern.count('[') != pattern.count(']'):
            errors.append("Unmatched square brackets")
        
        # Check for unmatched braces
        if pattern.count('{') != pattern.count('}'):
            errors.append("Unmatched curly braces")
        
        # Check for invalid token syntax
        invalid_tokens = re.findall(r'\$[^A-Z_\s{]', pattern)
        if invalid_tokens:
            errors.append(f"Invalid token syntax: {', '.join(invalid_tokens)}")
        
        return errors
    
    def _check_warnings(self, pattern: str) -> List[str]:
        """Check for potential issues."""
        warnings = []
        
        # Check for overly broad patterns
        if pattern in ['*', '*.*', '**']:
            warnings.append("Pattern may match too many files")
        
        # Check for potentially slow patterns
        if pattern.startswith('*') and not pattern.startswith('*.'):
            warnings.append("Pattern starting with * may be slow")
        
        # Check for redundant wildcards
        if '**' in pattern:
            warnings.append("Double wildcards may be redundant")
        
        return warnings
    
    def _generate_suggestions(self, pattern: str) -> List[str]:
        """Generate helpful suggestions."""
        suggestions = []
        
        # Suggest file extension patterns
        if not '.' in pattern and not any(op in pattern for op in ['AND', 'OR', 'size', 'modified']):
            suggestions.append("Consider adding file extension: '*.txt', '*.pdf'")
        
        # Suggest token usage
        if 'date' in pattern.lower() and '$DATE' not in pattern:
            suggestions.append("Use $DATE token for dynamic dates: '$DATE*'")
        
        # Suggest group references
        common_extensions = {'.jpg', '.png', '.gif', '.mp4', '.pdf', '.txt', '.doc'}
        for ext in common_extensions:
            if ext in pattern:
                group_map = {
                    ('.jpg', '.png', '.gif'): '@media',
                    ('.mp4', '.avi', '.mov'): '@media', 
                    ('.pdf', '.doc', '.txt'): '@documents'
                }
                for exts, group in group_map.items():
                    if any(e in pattern for e in exts):
                        suggestions.append(f"Use group reference: {group}")
                        break
        
        return suggestions
    
    def _estimate_performance(self, pattern: str) -> int:
        """Estimate pattern performance score (1-10)."""
        score = 10
        
        # Penalize broad patterns
        if pattern in ['*', '*.*']:
            score -= 8
        elif pattern.startswith('*') and not pattern.startswith('*.'):
            score -= 5
        
        # Penalize complex operations
        if re.search(r'\b(?:contains|matches)\b', pattern, re.IGNORECASE):
            score -= 3
        
        # Penalize multiple conditions
        condition_count = len(re.findall(r'\b(?:AND|OR)\b', pattern, re.IGNORECASE))
        score -= min(condition_count * 2, 6)
        
        return max(1, score)
