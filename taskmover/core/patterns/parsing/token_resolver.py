"""
Dynamic Token Resolver

Handles resolution of dynamic tokens like $DATE, $TIME, $USER, etc.
in pattern expressions.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Pattern as RegexPattern
import re
import getpass
from pathlib import Path

from ..interfaces import BasePatternComponent, ITokenResolver
from ..exceptions import TokenResolutionError


class TokenResolver(BasePatternComponent, ITokenResolver):
    """
    Resolves dynamic tokens in pattern expressions.
    
    Supports date/time tokens, user context, and custom token definitions.
    """
    
    def __init__(self, custom_tokens: Optional[Dict[str, str]] = None):
        super().__init__("token_resolver")
        
        # Custom token definitions
        self._custom_tokens = custom_tokens or {}
        
        # Compile token pattern for efficient matching
        self._token_pattern = re.compile(r'\$([A-Z_]+)(?:\{([^}]*)\})?')
        
        # Initialize built-in token providers
        self._token_providers = {
            'DATE': self._resolve_date,
            'TIME': self._resolve_time,
            'DATETIME': self._resolve_datetime,
            'TIMESTAMP': self._resolve_timestamp,
            'USER': self._resolve_user,
            'HOSTNAME': self._resolve_hostname,
            'WORKDIR': self._resolve_workdir,
            'YEAR': self._resolve_year,
            'MONTH': self._resolve_month,
            'DAY': self._resolve_day,
            'HOUR': self._resolve_hour,
            'MINUTE': self._resolve_minute,
            'SECOND': self._resolve_second,
            'WEEKDAY': self._resolve_weekday,
            'WEEK': self._resolve_week,
            'QUARTER': self._resolve_quarter,
            'SEASON': self._resolve_season,
            'PROJECT': self._resolve_project,
            'GIT_BRANCH': self._resolve_git_branch,
            'GIT_COMMIT': self._resolve_git_commit,
            'ENV': self._resolve_environment,
            'RANDOM': self._resolve_random,
            'COUNTER': self._resolve_counter,
            'UUID': self._resolve_uuid
        }
        
        # Counter for sequential numbering
        self._counter = 0
        
        self._logger.info(f"TokenResolver initialized with {len(self._token_providers)} built-in tokens")
    
    def resolve_tokens(self, pattern: str) -> str:
        """
        Resolve all dynamic tokens in a pattern.
        
        Args:
            pattern: Pattern string containing tokens like $DATE, $USER{format}
            
        Returns:
            Pattern with all tokens resolved to their current values
            
        Raises:
            TokenResolutionError: If token resolution fails
        """
        try:
            self._log_operation("resolve_tokens", original_pattern=pattern)
            
            if not pattern:
                return pattern
            
            # Find all tokens in the pattern
            tokens = self._token_pattern.findall(pattern)
            if not tokens:
                return pattern
            
            resolved_pattern = pattern
            
            # Resolve each token
            for token_name, token_args in tokens:
                try:
                    # Build full token string for replacement
                    if token_args:
                        full_token = f"${token_name}{{{token_args}}}"
                    else:
                        full_token = f"${token_name}"
                    
                    # Resolve the token value
                    resolved_value = self._resolve_single_token(token_name, token_args)
                    
                    # Replace in pattern
                    resolved_pattern = resolved_pattern.replace(full_token, resolved_value)
                    
                    self._logger.debug(f"Resolved token {full_token} -> {resolved_value}")
                    
                except Exception as e:
                    self._log_error(e, "token_resolution", token=token_name)
                    # Don't fail completely - leave unresolved token
                    self._logger.warning(f"Failed to resolve token ${token_name}: {e}")
            
            self._log_operation("resolve_tokens_complete", 
                              original=pattern, 
                              resolved=resolved_pattern)
            
            return resolved_pattern
            
        except Exception as e:
            self._log_error(e, "resolve_tokens", pattern=pattern)
            raise TokenResolutionError(f"Failed to resolve tokens in pattern '{pattern}': {e}")
    
    def get_available_tokens(self) -> Dict[str, str]:
        """
        Get all available tokens and their descriptions.
        
        Returns:
            Dictionary mapping token names to descriptions
        """
        descriptions = {
            'DATE': 'Current date (YYYY-MM-DD)',
            'TIME': 'Current time (HH-MM-SS)',
            'DATETIME': 'Current date and time (YYYY-MM-DD_HH-MM-SS)',
            'TIMESTAMP': 'Unix timestamp',
            'USER': 'Current username',
            'HOSTNAME': 'Computer hostname',
            'WORKDIR': 'Current working directory name',
            'YEAR': 'Current year (YYYY)',
            'MONTH': 'Current month (MM)',
            'DAY': 'Current day (DD)',
            'HOUR': 'Current hour (HH)',
            'MINUTE': 'Current minute (MM)',
            'SECOND': 'Current second (SS)',
            'WEEKDAY': 'Current weekday name',
            'WEEK': 'Current week number',
            'QUARTER': 'Current quarter (Q1-Q4)',
            'SEASON': 'Current season (Spring/Summer/Fall/Winter)',
            'PROJECT': 'Current project/directory name',
            'GIT_BRANCH': 'Current git branch name',
            'GIT_COMMIT': 'Current git commit hash (short)',
            'ENV': 'Environment variable value',
            'RANDOM': 'Random number',
            'COUNTER': 'Sequential counter',
            'UUID': 'Unique identifier'
        }
        
        # Add custom tokens
        for token_name in self._custom_tokens:
            descriptions[token_name] = f'Custom token: {token_name}'
        
        return descriptions
    
    def add_custom_token(self, name: str, value: str) -> None:
        """Add a custom token definition."""
        self._custom_tokens[name.upper()] = value
        self._logger.info(f"Added custom token: ${name}")
    
    def remove_custom_token(self, name: str) -> bool:
        """Remove a custom token definition."""
        token_name = name.upper()
        if token_name in self._custom_tokens:
            del self._custom_tokens[token_name]
            self._logger.info(f"Removed custom token: ${name}")
            return True
        return False
    
    def _resolve_single_token(self, token_name: str, token_args: str) -> str:
        """Resolve a single token to its value."""
        token_name = token_name.upper()
        
        # Check custom tokens first
        if token_name in self._custom_tokens:
            return self._custom_tokens[token_name]
        
        # Check built-in tokens
        if token_name in self._token_providers:
            provider = self._token_providers[token_name]
            return provider(token_args)
        
        # Unknown token
        raise TokenResolutionError(f"Unknown token: ${token_name}")
    
    # Built-in token resolvers
    
    def _resolve_date(self, args: str) -> str:
        """Resolve $DATE token with optional format."""
        try:
            now = datetime.now()
            if args:
                # Custom format provided
                return now.strftime(args)
            else:
                # Default format: YYYY-MM-DD
                return now.strftime('%Y-%m-%d')
        except Exception as e:
            raise TokenResolutionError(f"Invalid date format: {e}")
    
    def _resolve_time(self, args: str) -> str:
        """Resolve $TIME token with optional format."""
        try:
            now = datetime.now()
            if args:
                return now.strftime(args)
            else:
                # Default format: HH-MM-SS (filename-safe)
                return now.strftime('%H-%M-%S')
        except Exception as e:
            raise TokenResolutionError(f"Invalid time format: {e}")
    
    def _resolve_datetime(self, args: str) -> str:
        """Resolve $DATETIME token."""
        try:
            now = datetime.now()
            if args:
                return now.strftime(args)
            else:
                return now.strftime('%Y-%m-%d_%H-%M-%S')
        except Exception as e:
            raise TokenResolutionError(f"Invalid datetime format: {e}")
    
    def _resolve_timestamp(self, args: str) -> str:
        """Resolve $TIMESTAMP token."""
        return str(int(time.time()))
    
    def _resolve_user(self, args: str) -> str:
        """Resolve $USER token."""
        try:
            return getpass.getuser()
        except Exception:
            return os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
    
    def _resolve_hostname(self, args: str) -> str:
        """Resolve $HOSTNAME token."""
        try:
            import socket
            return socket.gethostname()
        except Exception:
            return 'unknown'
    
    def _resolve_workdir(self, args: str) -> str:
        """Resolve $WORKDIR token."""
        return Path.cwd().name
    
    def _resolve_year(self, args: str) -> str:
        """Resolve $YEAR token."""
        return datetime.now().strftime('%Y')
    
    def _resolve_month(self, args: str) -> str:
        """Resolve $MONTH token."""
        if args and args.lower() == 'name':
            return datetime.now().strftime('%B')
        elif args and args.lower() == 'short':
            return datetime.now().strftime('%b')
        else:
            return datetime.now().strftime('%m')
    
    def _resolve_day(self, args: str) -> str:
        """Resolve $DAY token."""
        return datetime.now().strftime('%d')
    
    def _resolve_hour(self, args: str) -> str:
        """Resolve $HOUR token."""
        return datetime.now().strftime('%H')
    
    def _resolve_minute(self, args: str) -> str:
        """Resolve $MINUTE token."""
        return datetime.now().strftime('%M')
    
    def _resolve_second(self, args: str) -> str:
        """Resolve $SECOND token."""
        return datetime.now().strftime('%S')
    
    def _resolve_weekday(self, args: str) -> str:
        """Resolve $WEEKDAY token."""
        if args and args.lower() == 'short':
            return datetime.now().strftime('%a')
        else:
            return datetime.now().strftime('%A')
    
    def _resolve_week(self, args: str) -> str:
        """Resolve $WEEK token."""
        return str(datetime.now().isocalendar()[1])
    
    def _resolve_quarter(self, args: str) -> str:
        """Resolve $QUARTER token."""
        month = datetime.now().month
        quarter = (month - 1) // 3 + 1
        return f"Q{quarter}"
    
    def _resolve_season(self, args: str) -> str:
        """Resolve $SEASON token."""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'
    
    def _resolve_project(self, args: str) -> str:
        """Resolve $PROJECT token."""
        # Try to find project name from various sources
        cwd = Path.cwd()
        
        # Check for git repository
        git_dir = cwd / '.git'
        if git_dir.exists():
            return cwd.name
        
        # Check parent directories for git
        for parent in cwd.parents:
            if (parent / '.git').exists():
                return parent.name
        
        # Default to current directory name
        return cwd.name
    
    def _resolve_git_branch(self, args: str) -> str:
        """Resolve $GIT_BRANCH token."""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return 'unknown'
        except Exception:
            return 'unknown'
    
    def _resolve_git_commit(self, args: str) -> str:
        """Resolve $GIT_COMMIT token."""
        try:
            import subprocess
            length = 7  # Default short hash length
            if args and args.isdigit():
                length = int(args)
            
            result = subprocess.run(
                ['git', 'rev-parse', f'--short={length}', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return 'unknown'
        except Exception:
            return 'unknown'
    
    def _resolve_environment(self, args: str) -> str:
        """Resolve $ENV{variable_name} token."""
        if not args:
            raise TokenResolutionError("ENV token requires variable name: $ENV{VAR_NAME}")
        
        # Support default values: $ENV{VAR_NAME:default_value}
        if ':' in args:
            var_name, default_value = args.split(':', 1)
            return os.environ.get(var_name.strip(), default_value.strip())
        else:
            var_value = os.environ.get(args.strip())
            if var_value is None:
                raise TokenResolutionError(f"Environment variable not found: {args}")
            return var_value
    
    def _resolve_random(self, args: str) -> str:
        """Resolve $RANDOM token."""
        import random
        
        if args:
            # Support range: $RANDOM{1-100} or length: $RANDOM{6}
            if '-' in args:
                try:
                    start, end = map(int, args.split('-'))
                    return str(random.randint(start, end))
                except ValueError:
                    raise TokenResolutionError(f"Invalid random range: {args}")
            else:
                try:
                    length = int(args)
                    return ''.join(random.choices('0123456789', k=length))
                except ValueError:
                    raise TokenResolutionError(f"Invalid random length: {args}")
        else:
            return str(random.randint(1000, 9999))
    
    def _resolve_counter(self, args: str) -> str:
        """Resolve $COUNTER token."""
        self._counter += 1
        
        if args:
            try:
                width = int(args)
                return str(self._counter).zfill(width)
            except ValueError:
                return str(self._counter)
        else:
            return str(self._counter)
    
    def _resolve_uuid(self, args: str) -> str:
        """Resolve $UUID token."""
        import uuid
        
        if args and args.lower() == 'short':
            # Return first 8 characters of UUID
            return str(uuid.uuid4())[:8]
        else:
            return str(uuid.uuid4())
