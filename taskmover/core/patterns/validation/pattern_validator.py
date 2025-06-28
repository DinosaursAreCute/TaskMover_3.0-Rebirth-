"""
Comprehensive Pattern Validator

Validates patterns for syntax, performance, and best practices
with detailed error reporting and suggestions.
"""

import re
import time
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path

from ..interfaces import BasePatternComponent, IPatternValidator, IPatternParser
from ..models import Pattern, ValidationResult, PatternType, SYSTEM_GROUPS
from ..exceptions import ValidationError


class PatternValidator(BasePatternComponent, IPatternValidator):
    """
    Comprehensive pattern validation with syntax checking,
    performance analysis, and best practice recommendations.
    """
    
    def __init__(self, parser: Optional[IPatternParser] = None):
        super().__init__("pattern_validator")
        
        self._parser = parser
        
        # Performance thresholds
        self._max_complexity_score = 10
        self._recommended_complexity_score = 5
        self._performance_warning_threshold = 7
        
        # Known problematic patterns
        self._problematic_patterns = {
            r'^\*$': "Single wildcard matches all files - too broad",
            r'^\*\.\*$': "Double wildcard extension pattern - too broad",
            r'^\*.*\*.*\*.*\*': "Too many wildcards - may be slow",
            r'^\..*\*': "Leading dot with wildcard may not work as expected"
        }
        
        # Best practice rules
        self._best_practices = {
            'use_extensions': "Consider adding file extensions for better performance",
            'avoid_leading_wildcards': "Patterns starting with * can be slow",
            'use_groups': "Consider using system groups like @media, @documents",
            'use_tokens': "Use tokens like $DATE for dynamic patterns",
            'specific_patterns': "More specific patterns perform better"
        }
        
        # Compile regex patterns for validation
        self._compile_validation_patterns()
        
        self._logger.info("PatternValidator initialized")
    
    def validate(self, pattern: Pattern) -> ValidationResult:
        """
        Validate a complete pattern with all its components.
        
        Args:
            pattern: Pattern object to validate
            
        Returns:
            ValidationResult with comprehensive validation details
        """
        try:
            self._log_operation("validate_pattern", 
                              pattern_id=str(pattern.id),
                              pattern_type=pattern.pattern_type.value)
            
            errors = []
            warnings = []
            suggestions = []
            
            # Validate expression syntax
            expr_result = self.validate_expression(pattern.user_expression)
            errors.extend(expr_result.errors)
            warnings.extend(expr_result.warnings)
            suggestions.extend(expr_result.suggestions)
            
            # Validate pattern metadata
            metadata_errors = self._validate_metadata(pattern)
            errors.extend(metadata_errors)
            
            # Validate compiled query
            if pattern.compiled_query:
                query_errors = self._validate_compiled_query(pattern.compiled_query)
                errors.extend(query_errors)
            
            # Performance analysis
            performance_score = self._analyze_performance(pattern)
            if performance_score < 3:
                warnings.append(f"Low performance score: {performance_score}/10")
            
            # Check for deprecated patterns
            deprecation_warnings = self._check_deprecation(pattern)
            warnings.extend(deprecation_warnings)
            
            # Generate optimization suggestions
            optimization_suggestions = self._suggest_optimizations(pattern)
            suggestions.extend(optimization_suggestions)
            
            is_valid = len(errors) == 0
            
            result = ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                performance_score=performance_score
            )
            
            self._logger.debug(f"Pattern validation: valid={is_valid}, "
                             f"errors={len(errors)}, warnings={len(warnings)}")
            
            return result
            
        except Exception as e:
            self._log_error(e, "validate_pattern", pattern_id=str(pattern.id))
            return ValidationResult(
                False,
                [f"Validation error: {e}"]
            )
    
    def validate_expression(self, expression: str) -> ValidationResult:
        """
        Validate a pattern expression string.
        
        Args:
            expression: Pattern expression to validate
            
        Returns:
            ValidationResult for the expression
        """
        try:
            self._log_operation("validate_expression", expression=expression)
            
            errors = []
            warnings = []
            suggestions = []
            
            if not expression or not expression.strip():
                errors.append("Pattern expression cannot be empty")
                return ValidationResult(False, errors)
            
            expression = expression.strip()
            
            # Basic syntax validation
            syntax_errors = self._validate_syntax(expression)
            errors.extend(syntax_errors)
            
            # Check for problematic patterns
            problematic_warnings = self._check_problematic_patterns(expression)
            warnings.extend(problematic_warnings)
            
            # Validate tokens
            token_errors, token_warnings = self._validate_tokens(expression)
            errors.extend(token_errors)
            warnings.extend(token_warnings)
            
            # Validate group references
            group_errors = self._validate_group_references(expression)
            errors.extend(group_errors)
            
            # Validate advanced query syntax
            if self._is_advanced_query(expression):
                query_errors, query_warnings = self._validate_advanced_syntax(expression)
                errors.extend(query_errors)
                warnings.extend(query_warnings)
            
            # Generate best practice suggestions
            bp_suggestions = self._generate_best_practice_suggestions(expression)
            suggestions.extend(bp_suggestions)
            
            # Calculate basic performance score
            performance_score = self._calculate_expression_performance(expression)
            
            is_valid = len(errors) == 0
            
            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                performance_score=performance_score
            )
            
        except Exception as e:
            self._log_error(e, "validate_expression", expression=expression)
            return ValidationResult(
                False,
                [f"Expression validation error: {e}"]
            )
    
    def validate_batch(self, patterns: List[Pattern]) -> Dict[str, ValidationResult]:
        """Validate multiple patterns efficiently."""
        try:
            self._log_operation("validate_batch", pattern_count=len(patterns))
            
            results = {}
            
            for pattern in patterns:
                results[str(pattern.id)] = self.validate(pattern)
            
            return results
            
        except Exception as e:
            self._log_error(e, "validate_batch")
            return {}
    
    def _compile_validation_patterns(self) -> None:
        """Compile regex patterns for efficient validation."""
        try:
            # Token pattern
            self._token_pattern = re.compile(r'\$([A-Z_]+)(?:\{([^}]*)\})?')
            
            # Group reference pattern
            self._group_pattern = re.compile(r'@([a-zA-Z_][a-zA-Z0-9_]*)')
            
            # Advanced query indicators
            self._advanced_indicators = [
                re.compile(r'\b(?:AND|OR|NOT)\b', re.IGNORECASE),
                re.compile(r'\b(?:size|modified|created|type)\s*[<>=]'),
                re.compile(r'\b(?:contains|matches|startswith|endswith)\s*\('),
                re.compile(r'\bdate\s*[<>=]'),
            ]
            
            # Bracket patterns
            self._bracket_patterns = {
                'parentheses': re.compile(r'[()]'),
                'square': re.compile(r'[\[\]]'),
                'curly': re.compile(r'[{}]')
            }
            
            # Problematic pattern regex
            self._problematic_regex = [
                (re.compile(pattern), message) 
                for pattern, message in self._problematic_patterns.items()
            ]
            
        except Exception as e:
            raise ValidationError(f"Failed to compile validation patterns: {e}", target="validation_patterns")
    
    def _validate_syntax(self, expression: str) -> List[str]:
        """Validate basic syntax of expression."""
        errors = []
        
        # Check for balanced brackets
        bracket_errors = self._check_balanced_brackets(expression)
        errors.extend(bracket_errors)
        
        # Check for invalid characters in simple patterns
        if not self._is_advanced_query(expression):
            invalid_chars = self._find_invalid_characters(expression)
            if invalid_chars:
                errors.append(f"Invalid characters for glob pattern: {', '.join(invalid_chars)}")
        
        # Check for consecutive wildcards
        if '***' in expression:
            errors.append("Triple wildcards (***) are not valid")
        
        # Check for empty parentheses
        if '()' in expression:
            errors.append("Empty parentheses are not allowed")
        
        return errors
    
    def _check_balanced_brackets(self, expression: str) -> List[str]:
        """Check if brackets are properly balanced."""
        errors = []
        
        bracket_pairs = {
            '(': ')',
            '[': ']',
            '{': '}'
        }
        
        for open_bracket, close_bracket in bracket_pairs.items():
            open_count = expression.count(open_bracket)
            close_count = expression.count(close_bracket)
            
            if open_count != close_count:
                bracket_name = {
                    '(': 'parentheses',
                    '[': 'square brackets',
                    '{': 'curly braces'
                }[open_bracket]
                errors.append(f"Unmatched {bracket_name}")
        
        return errors
    
    def _find_invalid_characters(self, expression: str) -> Set[str]:
        """Find invalid characters in glob patterns."""
        # Valid characters for glob patterns
        valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                         '0123456789._-*?[]{}/$@')
        
        invalid_chars = set()
        for char in expression:
            if char not in valid_chars and not char.isspace():
                invalid_chars.add(char)
        
        return invalid_chars
    
    def _check_problematic_patterns(self, expression: str) -> List[str]:
        """Check for known problematic patterns."""
        warnings = []
        
        for pattern_regex, message in self._problematic_regex:
            if pattern_regex.match(expression):
                warnings.append(message)
        
        return warnings
    
    def _validate_tokens(self, expression: str) -> Tuple[List[str], List[str]]:
        """Validate token syntax and usage."""
        errors = []
        warnings = []
        
        # Find all tokens
        tokens = self._token_pattern.findall(expression)
        
        # Valid token names
        valid_tokens = {
            'DATE', 'TIME', 'DATETIME', 'TIMESTAMP', 'USER', 'HOSTNAME',
            'WORKDIR', 'YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND',
            'WEEKDAY', 'WEEK', 'QUARTER', 'SEASON', 'PROJECT', 'GIT_BRANCH',
            'GIT_COMMIT', 'ENV', 'RANDOM', 'COUNTER', 'UUID'
        }
        
        for token_name, token_args in tokens:
            # Check if token is valid
            if token_name not in valid_tokens:
                errors.append(f"Unknown token: ${token_name}")
            
            # Validate token arguments
            if token_args:
                arg_errors = self._validate_token_args(token_name, token_args)
                errors.extend(arg_errors)
            
            # Check for specific token requirements
            if token_name == 'ENV' and not token_args:
                errors.append("ENV token requires variable name: $ENV{VAR_NAME}")
        
        # Check for malformed tokens
        malformed_tokens = re.findall(r'\$[^A-Z_\s{]', expression)
        for malformed in malformed_tokens:
            errors.append(f"Malformed token: {malformed}")
        
        return errors, warnings
    
    def _validate_token_args(self, token_name: str, args: str) -> List[str]:
        """Validate token arguments."""
        errors = []
        
        if token_name == 'DATE' and args:
            # Validate strftime format
            try:
                from datetime import datetime
                datetime.now().strftime(args)
            except ValueError:
                errors.append(f"Invalid date format: {args}")
        
        elif token_name == 'RANDOM' and args:
            # Validate random format
            if '-' in args:
                try:
                    start, end = args.split('-')
                    int(start)
                    int(end)
                except ValueError:
                    errors.append(f"Invalid random range: {args}")
            else:
                try:
                    int(args)
                except ValueError:
                    errors.append(f"Invalid random length: {args}")
        
        elif token_name == 'COUNTER' and args:
            try:
                int(args)
            except ValueError:
                errors.append(f"Invalid counter width: {args}")
        
        return errors
    
    def _validate_group_references(self, expression: str) -> List[str]:
        """Validate group references."""
        errors = []
        
        # Find all group references
        groups = self._group_pattern.findall(expression)
        
        for group_name in groups:
            full_ref = f"@{group_name}"
            
            # Check if it's a valid system group
            if full_ref not in SYSTEM_GROUPS:
                # Could be a user-defined group, so this is just a warning
                # We'll handle this in warnings, not errors
                pass
        
        return errors
    
    def _is_advanced_query(self, expression: str) -> bool:
        """Check if expression is an advanced query."""
        for indicator in self._advanced_indicators:
            if indicator.search(expression):
                return True
        return False
    
    def _validate_advanced_syntax(self, expression: str) -> Tuple[List[str], List[str]]:
        """Validate advanced query syntax."""
        errors = []
        warnings = []
        
        # Check for valid operators
        invalid_operators = re.findall(r'\b(?:and|or|not)\b', expression)
        if invalid_operators:
            errors.append("Use uppercase operators: AND, OR, NOT")
        
        # Check for incomplete conditions
        incomplete_conditions = re.findall(r'\b(?:size|modified|created)\s*[<>=]\s*$', expression)
        if incomplete_conditions:
            errors.append("Incomplete condition - missing value")
        
        # Check for unquoted string literals
        unquoted_strings = re.findall(r'\bname\s*=\s*([^\s\'"][^\s]*)', expression)
        if unquoted_strings:
            warnings.append("String literals should be quoted")
        
        # Validate date expressions
        date_expressions = re.findall(r'(?:modified|created)\s*[<>=]\s*([^)\s]+)', expression)
        for date_expr in date_expressions:
            if not self._is_valid_date_expression(date_expr):
                errors.append(f"Invalid date expression: {date_expr}")
        
        return errors, warnings
    
    def _is_valid_date_expression(self, expr: str) -> bool:
        """Check if date expression is valid."""
        valid_patterns = [
            r'today-\d+',
            r'today\+\d+',
            r'\d{4}-\d{2}-\d{2}',
            r'DATE_SUB\(',
            r'DATE_ADD\(',
            r'NOW\(\)'
        ]
        
        for pattern in valid_patterns:
            if re.match(pattern, expr):
                return True
        
        return False
    
    def _validate_metadata(self, pattern: Pattern) -> List[str]:
        """Validate pattern metadata."""
        errors = []
        
        if not pattern.name.strip():
            errors.append("Pattern name cannot be empty")
        
        if len(pattern.name) > 100:
            errors.append("Pattern name too long (max 100 characters)")
        
        if pattern.estimated_complexity < 1 or pattern.estimated_complexity > 10:
            errors.append("Estimated complexity must be between 1 and 10")
        
        return errors
    
    def _validate_compiled_query(self, query: str) -> List[str]:
        """Validate compiled query syntax."""
        errors = []
        
        # Basic SQL-like syntax validation
        if query and not any(keyword in query.upper() for keyword in ['LIKE', 'GROUP_REF', '=']):
            errors.append("Compiled query has invalid format")
        
        return errors
    
    def _analyze_performance(self, pattern: Pattern) -> int:
        """Analyze pattern performance and return score (1-10)."""
        score = 10
        
        expression = pattern.user_expression
        
        # Penalize overly broad patterns
        if expression in ['*', '*.*', '**']:
            score -= 8
        elif expression.startswith('*') and not expression.startswith('*.'):
            score -= 4
        
        # Penalize multiple wildcards
        wildcard_count = expression.count('*')
        if wildcard_count > 3:
            score -= min(wildcard_count - 3, 3)
        
        # Penalize complex advanced queries
        if pattern.pattern_type == PatternType.ADVANCED_QUERY:
            condition_count = len(re.findall(r'\b(?:AND|OR)\b', expression, re.IGNORECASE))
            score -= min(condition_count * 2, 4)
        
        # Bonus for specific extensions
        if re.match(r'^\*\.[a-zA-Z]{2,4}$', expression):
            score += 1
        
        # Penalty for regex-like patterns in glob
        if any(char in expression for char in ['+', '^', '$', '\\']) and pattern.pattern_type != PatternType.ADVANCED_QUERY:
            score -= 2
        
        return max(1, min(10, score))
    
    def _calculate_expression_performance(self, expression: str) -> int:
        """Calculate performance score for expression only."""
        score = 10
        
        # Simple scoring based on pattern characteristics
        if expression in ['*', '*.*']:
            score = 1
        elif expression.startswith('*'):
            score -= 3
        elif expression.count('*') > 2:
            score -= 2
        
        if any(op in expression.upper() for op in ['AND', 'OR', 'NOT']):
            score -= 1
        
        return max(1, score)
    
    def _check_deprecation(self, pattern: Pattern) -> List[str]:
        """Check for deprecated pattern features."""
        warnings = []
        
        # Currently no deprecated features, but could include:
        # - Old token syntax
        # - Deprecated group names
        # - Legacy operators
        
        return warnings
    
    def _suggest_optimizations(self, pattern: Pattern) -> List[str]:
        """Suggest pattern optimizations."""
        suggestions = []
        
        expression = pattern.user_expression
        
        # Suggest more specific patterns
        if expression == '*':
            suggestions.append("Consider adding file extension: '*.txt', '*.pdf'")
        
        # Suggest group usage
        if any(ext in expression for ext in ['.jpg', '.png', '.gif', '.mp4']):
            suggestions.append("Consider using @media group for media files")
        
        if any(ext in expression for ext in ['.pdf', '.doc', '.txt']):
            suggestions.append("Consider using @documents group for document files")
        
        # Suggest token usage
        if 'date' in expression.lower() and '$DATE' not in expression:
            suggestions.append("Use $DATE token for dynamic date patterns")
        
        # Suggest avoiding leading wildcards
        if expression.startswith('*') and not expression.startswith('*.'):
            suggestions.append("Avoid leading wildcards for better performance")
        
        return suggestions
    
    def _generate_best_practice_suggestions(self, expression: str) -> List[str]:
        """Generate best practice suggestions."""
        suggestions = []
        
        # Suggest extensions for broad patterns
        if expression in ['*', 'file*', '*file*']:
            suggestions.append("Add file extension for better performance: '*.txt'")
        
        # Suggest system groups
        if '*.' in expression:
            ext = expression.split('*.')[-1]
            if ext in ['jpg', 'png', 'gif', 'mp4', 'avi']:
                suggestions.append("Consider using @media group instead")
            elif ext in ['pdf', 'doc', 'txt']:
                suggestions.append("Consider using @documents group instead")
        
        return suggestions
