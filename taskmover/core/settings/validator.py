"""
Settings Validation Implementation

Provides comprehensive validation for setting values including type checking,
range validation, pattern matching, and custom validation functions.
"""

import logging
import re
from pathlib import Path
from typing import Any, List, Union

from . import (
    SettingDefinition,
    SettingValidationResult,
    SettingType,
    ISettingValidator,
)


class SettingValidator(ISettingValidator):
    """
    Comprehensive setting validator with support for all setting types
    and validation rules.
    """
    
    def __init__(self):
        self._logger = logging.getLogger(f"{__name__}.SettingValidator")
    
    def validate(self, definition: SettingDefinition, value: Any) -> SettingValidationResult:
        """
        Validate a setting value against its definition.
        
        Args:
            definition: The setting definition with validation rules
            value: The value to validate
            
        Returns:
            SettingValidationResult with validation status and normalized value
        """
        errors = []
        warnings = []
        normalized_value = value
        
        try:
            # Check if required
            if definition.required and (value is None or value == ""):
                errors.append(f"Setting '{definition.key}' is required")
                return SettingValidationResult(False, errors, warnings)
            
            # Allow None for non-required settings
            if value is None and not definition.required:
                return SettingValidationResult(True, errors, warnings, definition.default_value)
            
            # Type validation and normalization
            type_result = self._validate_type(definition, value)
            if not type_result.is_valid:
                errors.extend(type_result.errors)
            else:
                normalized_value = type_result.normalized_value
            
            # Range validation (for numeric types)
            if definition.type in [SettingType.INTEGER, SettingType.FLOAT]:
                range_errors = self._validate_range(definition, normalized_value)
                errors.extend(range_errors)
            
            # Allowed values validation
            if definition.allowed_values:
                if normalized_value not in definition.allowed_values:
                    errors.append(f"Value '{normalized_value}' not in allowed values: {definition.allowed_values}")
            
            # Pattern validation (for string types)
            if definition.pattern and definition.type == SettingType.STRING:
                pattern_errors = self._validate_pattern(definition, normalized_value)
                errors.extend(pattern_errors)
            
            # Custom validator
            if definition.validator:
                try:
                    if not definition.validator(normalized_value):
                        errors.append(f"Custom validation failed for '{definition.key}'")
                except Exception as e:
                    errors.append(f"Custom validator error: {str(e)}")
            
            # Dependency validation
            dependency_warnings = self._validate_dependencies(definition, normalized_value)
            warnings.extend(dependency_warnings)
            
            # Deprecation warning
            if definition.deprecated:
                message = definition.deprecated_message or f"Setting '{definition.key}' is deprecated"
                warnings.append(message)
            
            is_valid = len(errors) == 0
            
            if is_valid:
                self._logger.debug(f"Validation passed for setting '{definition.key}' with value: {normalized_value}")
            else:
                self._logger.warning(f"Validation failed for setting '{definition.key}': {errors}")
            
            return SettingValidationResult(is_valid, errors, warnings, normalized_value)
            
        except Exception as e:
            error_msg = f"Validation error for setting '{definition.key}': {str(e)}"
            self._logger.error(error_msg)
            return SettingValidationResult(False, [error_msg], warnings)
    
    def _validate_type(self, definition: SettingDefinition, value: Any) -> SettingValidationResult:
        """Validate and normalize the type of a setting value."""
        errors = []
        normalized_value = value
        
        try:
            if definition.type == SettingType.STRING:
                if not isinstance(value, str):
                    # Try to convert to string
                    normalized_value = str(value)
                    if normalized_value != str(value):  # Conversion changed the value
                        errors.append(f"Value '{value}' converted to string: '{normalized_value}'")
            
            elif definition.type == SettingType.INTEGER:
                if isinstance(value, bool):  # bool is subclass of int, but we want to catch this
                    errors.append(f"Boolean value '{value}' not allowed for integer setting")
                elif not isinstance(value, int):
                    try:
                        if isinstance(value, str):
                            normalized_value = int(value)
                        elif isinstance(value, float):
                            if value.is_integer():
                                normalized_value = int(value)
                            else:
                                errors.append(f"Float value '{value}' cannot be converted to integer without loss")
                        else:
                            normalized_value = int(value)
                    except (ValueError, TypeError):
                        errors.append(f"Cannot convert '{value}' to integer")
            
            elif definition.type == SettingType.FLOAT:
                if not isinstance(value, (int, float)):
                    try:
                        normalized_value = float(value)
                    except (ValueError, TypeError):
                        errors.append(f"Cannot convert '{value}' to float")
                else:
                    normalized_value = float(value)
            
            elif definition.type == SettingType.BOOLEAN:
                if not isinstance(value, bool):
                    # Try to convert common boolean representations
                    if isinstance(value, str):
                        lower_value = value.lower()
                        if lower_value in ['true', '1', 'yes', 'on', 'enabled']:
                            normalized_value = True
                        elif lower_value in ['false', '0', 'no', 'off', 'disabled']:
                            normalized_value = False
                        else:
                            errors.append(f"Cannot convert string '{value}' to boolean")
                    elif isinstance(value, (int, float)):
                        normalized_value = bool(value)
                    else:
                        errors.append(f"Cannot convert '{value}' to boolean")
            
            elif definition.type == SettingType.LIST:
                if not isinstance(value, list):
                    if isinstance(value, str):
                        # Try to parse as comma-separated values
                        normalized_value = [item.strip() for item in value.split(',') if item.strip()]
                    else:
                        errors.append(f"Value '{value}' is not a list")
            
            elif definition.type == SettingType.DICT:
                if not isinstance(value, dict):
                    errors.append(f"Value '{value}' is not a dictionary")
            
            elif definition.type == SettingType.PATH:
                if not isinstance(value, (str, Path)):
                    errors.append(f"Path value must be string or Path object, got {type(value)}")
                else:
                    # Normalize to Path object
                    normalized_value = Path(value)
                    # Validate path format
                    try:
                        # Check if path is valid (doesn't need to exist)
                        str(normalized_value.resolve())
                    except (OSError, ValueError) as e:
                        errors.append(f"Invalid path format: {str(e)}")
            
            elif definition.type == SettingType.COLOR:
                color_errors = self._validate_color(value)
                errors.extend(color_errors)
                if not color_errors:
                    normalized_value = self._normalize_color(value)
            
            elif definition.type == SettingType.ENUM:
                # For enum types, validation should be done via allowed_values
                pass
            
            else:
                errors.append(f"Unknown setting type: {definition.type}")
        
        except Exception as e:
            errors.append(f"Type validation error: {str(e)}")
        
        return SettingValidationResult(len(errors) == 0, errors, [], normalized_value)
    
    def _validate_range(self, definition: SettingDefinition, value: Union[int, float]) -> List[str]:
        """Validate numeric range constraints."""
        errors = []
        
        if definition.min_value is not None and value < definition.min_value:
            errors.append(f"Value {value} is below minimum {definition.min_value}")
        
        if definition.max_value is not None and value > definition.max_value:
            errors.append(f"Value {value} is above maximum {definition.max_value}")
        
        return errors
    
    def _validate_pattern(self, definition: SettingDefinition, value: str) -> List[str]:
        """Validate string pattern constraints."""
        errors = []
        
        try:
            if not re.match(definition.pattern, value):
                errors.append(f"Value '{value}' does not match required pattern: {definition.pattern}")
        except re.error as e:
            errors.append(f"Invalid regex pattern '{definition.pattern}': {str(e)}")
        
        return errors
    
    def _validate_dependencies(self, definition: SettingDefinition, value: Any) -> List[str]:
        """Validate setting dependencies (returns warnings)."""
        warnings = []
        
        # This is a placeholder for dependency validation
        # In a full implementation, this would check if dependent settings
        # are compatible with the current value
        for dependency in definition.dependencies:
            warnings.append(f"Setting '{definition.key}' depends on '{dependency}' - ensure compatibility")
        
        return warnings
    
    def _validate_color(self, value: Any) -> List[str]:
        """Validate color values (hex, rgb, rgba, named colors)."""
        errors = []
        
        if not isinstance(value, str):
            errors.append("Color value must be a string")
            return errors
        
        value = value.strip()
        
        # Hex color validation
        if value.startswith('#'):
            hex_pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3}|[A-Fa-f0-9]{8})$'
            if not re.match(hex_pattern, value):
                errors.append(f"Invalid hex color format: '{value}'")
        
        # RGB/RGBA validation
        elif value.startswith(('rgb(', 'rgba(')):
            rgb_pattern = r'^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(0?\.\d+|1(?:\.0)?|\d+))?\s*\)$'
            match = re.match(rgb_pattern, value)
            if not match:
                errors.append(f"Invalid RGB/RGBA color format: '{value}'")
            else:
                # Validate RGB values are 0-255
                r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
                if not all(0 <= val <= 255 for val in [r, g, b]):
                    errors.append(f"RGB values must be between 0 and 255: '{value}'")
                
                # Validate alpha value if present
                if match.group(4):
                    alpha = float(match.group(4))
                    if not 0 <= alpha <= 1:
                        errors.append(f"Alpha value must be between 0 and 1: '{value}'")
        
        # HSL/HSLA validation
        elif value.startswith(('hsl(', 'hsla(')):
            hsl_pattern = r'^hsla?\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*(?:,\s*(0?\.\d+|1(?:\.0)?|\d+))?\s*\)$'
            match = re.match(hsl_pattern, value)
            if not match:
                errors.append(f"Invalid HSL/HSLA color format: '{value}'")
            else:
                h, s, l = int(match.group(1)), int(match.group(2)), int(match.group(3))
                if not (0 <= h <= 360):
                    errors.append(f"Hue value must be between 0 and 360: '{value}'")
                if not all(0 <= val <= 100 for val in [s, l]):
                    errors.append(f"Saturation and lightness must be between 0 and 100: '{value}'")
        
        # Named color validation (basic list)
        else:
            named_colors = {
                'red', 'green', 'blue', 'white', 'black', 'yellow', 'cyan', 'magenta',
                'orange', 'purple', 'pink', 'brown', 'gray', 'grey', 'transparent'
            }
            if value.lower() not in named_colors:
                errors.append(f"Unknown named color: '{value}'")
        
        return errors
    
    def _normalize_color(self, value: str) -> str:
        """Normalize color values to a consistent format."""
        value = value.strip().lower()
        
        # Convert 3-digit hex to 6-digit
        if value.startswith('#') and len(value) == 4:
            return f"#{value[1]*2}{value[2]*2}{value[3]*2}"
        
        # Normalize spacing in rgb/rgba/hsl/hsla
        for prefix in ['rgb(', 'rgba(', 'hsl(', 'hsla(']:
            if value.startswith(prefix):
                # Remove extra spaces around commas
                value = re.sub(r'\s*,\s*', ', ', value)
                break
        
        return value


class BasicSettingValidator(ISettingValidator):
    """
    A simplified validator for basic use cases that only validates
    required fields and basic type checking.
    """
    
    def __init__(self):
        self._logger = logging.getLogger(f"{__name__}.BasicSettingValidator")
    
    def validate(self, definition: SettingDefinition, value: Any) -> SettingValidationResult:
        """Basic validation that only checks required fields and basic types."""
        errors = []
        
        # Check if required
        if definition.required and (value is None or value == ""):
            errors.append(f"Setting '{definition.key}' is required")
            return SettingValidationResult(False, errors)
        
        # Allow None for non-required settings
        if value is None and not definition.required:
            return SettingValidationResult(True, [], [], definition.default_value)
        
        # Basic type validation
        expected_types = {
            SettingType.STRING: str,
            SettingType.INTEGER: int,
            SettingType.FLOAT: (int, float),
            SettingType.BOOLEAN: bool,
            SettingType.LIST: list,
            SettingType.DICT: dict,
        }
        
        expected_type = expected_types.get(definition.type)
        if expected_type and not isinstance(value, expected_type):
            errors.append(f"Expected {expected_type}, got {type(value)}")
        
        is_valid = len(errors) == 0
        return SettingValidationResult(is_valid, errors, [], value)
