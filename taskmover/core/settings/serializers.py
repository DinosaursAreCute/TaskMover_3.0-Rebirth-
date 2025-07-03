"""
Settings Serialization Implementation

Provides serializers for different settings formats including YAML, JSON, and INI.
"""

import configparser
import json
import logging
import xml.etree.ElementTree as ET
from io import StringIO
from typing import Any, Dict

import yaml

from . import SettingFormat, ISettingSerializer


class YamlSettingSerializer(ISettingSerializer):
    """YAML serializer for settings."""
    
    def __init__(self):
        self._logger = logging.getLogger(f"{__name__}.YamlSettingSerializer")
    
    def serialize(self, settings: Dict[str, Any]) -> str:
        """Serialize settings to YAML format."""
        try:
            return yaml.dump(settings, default_flow_style=False, allow_unicode=True, 
                           sort_keys=True, indent=2)
        except Exception as e:
            self._logger.error(f"Error serializing settings to YAML: {e}")
            raise
    
    def deserialize(self, data: str) -> Dict[str, Any]:
        """Deserialize settings from YAML format."""
        try:
            result = yaml.safe_load(data)
            return result if isinstance(result, dict) else {}
        except Exception as e:
            self._logger.error(f"Error deserializing settings from YAML: {e}")
            raise
    
    def get_file_extension(self) -> str:
        """Get the file extension for YAML format."""
        return ".yaml"


class JsonSettingSerializer(ISettingSerializer):
    """JSON serializer for settings."""
    
    def __init__(self, indent: int = 2):
        """
        Initialize JSON serializer.
        
        Args:
            indent: Number of spaces for indentation
        """
        self._indent = indent
        self._logger = logging.getLogger(f"{__name__}.JsonSettingSerializer")
    
    def serialize(self, settings: Dict[str, Any]) -> str:
        """Serialize settings to JSON format."""
        try:
            return json.dumps(settings, indent=self._indent, ensure_ascii=False, sort_keys=True)
        except Exception as e:
            self._logger.error(f"Error serializing settings to JSON: {e}")
            raise
    
    def deserialize(self, data: str) -> Dict[str, Any]:
        """Deserialize settings from JSON format."""
        try:
            result = json.loads(data)
            return result if isinstance(result, dict) else {}
        except Exception as e:
            self._logger.error(f"Error deserializing settings from JSON: {e}")
            raise
    
    def get_file_extension(self) -> str:
        """Get the file extension for JSON format."""
        return ".json"


class IniSettingSerializer(ISettingSerializer):
    """INI serializer for settings."""
    
    def __init__(self, default_section: str = "DEFAULT"):
        """
        Initialize INI serializer.
        
        Args:
            default_section: Default section name for ungrouped settings
        """
        self._default_section = default_section
        self._logger = logging.getLogger(f"{__name__}.IniSettingSerializer")
    
    def serialize(self, settings: Dict[str, Any]) -> str:
        """Serialize settings to INI format."""
        try:
            config = configparser.ConfigParser()
            
            # Convert nested dictionaries to sections
            for key, value in settings.items():
                if isinstance(value, dict):
                    # Create section for nested dict
                    config[key] = {}
                    for subkey, subvalue in value.items():
                        config[key][subkey] = str(subvalue)
                else:
                    # Add to default section
                    if self._default_section not in config:
                        config[self._default_section] = {}
                    config[self._default_section][key] = str(value)
            
            output = StringIO()
            config.write(output)
            return output.getvalue()
            
        except Exception as e:
            self._logger.error(f"Error serializing settings to INI: {e}")
            raise
    
    def deserialize(self, data: str) -> Dict[str, Any]:
        """Deserialize settings from INI format."""
        try:
            config = configparser.ConfigParser()
            config.read_string(data)
            
            result = {}
            
            for section_name in config.sections():
                if section_name == self._default_section:
                    # Add default section items to root level
                    for key, value in config[section_name].items():
                        result[key] = self._convert_ini_value(value)
                else:
                    # Add section as nested dict
                    result[section_name] = {}
                    for key, value in config[section_name].items():
                        result[section_name][key] = self._convert_ini_value(value)
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error deserializing settings from INI: {e}")
            raise
    
    def get_file_extension(self) -> str:
        """Get the file extension for INI format."""
        return ".ini"
    
    def _convert_ini_value(self, value: str) -> Any:
        """Convert INI string value to appropriate Python type."""
        # Try to convert to appropriate type
        if value.lower() in ('true', 'yes', '1'):
            return True
        elif value.lower() in ('false', 'no', '0'):
            return False
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value


class XmlSettingSerializer(ISettingSerializer):
    """XML serializer for settings."""
    
    def __init__(self, root_element: str = "settings"):
        """
        Initialize XML serializer.
        
        Args:
            root_element: Name of the root XML element
        """
        self._root_element = root_element
        self._logger = logging.getLogger(f"{__name__}.XmlSettingSerializer")
    
    def serialize(self, settings: Dict[str, Any]) -> str:
        """Serialize settings to XML format."""
        try:
            root = ET.Element(self._root_element)
            self._dict_to_xml(settings, root)
            
            # Format with indentation
            self._indent_xml(root)
            
            return ET.tostring(root, encoding='unicode')
            
        except Exception as e:
            self._logger.error(f"Error serializing settings to XML: {e}")
            raise
    
    def deserialize(self, data: str) -> Dict[str, Any]:
        """Deserialize settings from XML format."""
        try:
            root = ET.fromstring(data)
            return self._xml_to_dict(root)
            
        except Exception as e:
            self._logger.error(f"Error deserializing settings from XML: {e}")
            raise
    
    def get_file_extension(self) -> str:
        """Get the file extension for XML format."""
        return ".xml"
    
    def _dict_to_xml(self, data: Any, parent: ET.Element) -> None:
        """Convert dictionary to XML elements."""
        if isinstance(data, dict):
            for key, value in data.items():
                # Create element with safe key name
                safe_key = self._make_safe_xml_name(key)
                element = ET.SubElement(parent, safe_key)
                
                if isinstance(value, (dict, list)):
                    self._dict_to_xml(value, element)
                else:
                    element.text = str(value)
                    # Store original key as attribute if it was modified
                    if safe_key != key:
                        element.set('original_key', key)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                element = ET.SubElement(parent, 'item')
                element.set('index', str(i))
                if isinstance(item, (dict, list)):
                    self._dict_to_xml(item, element)
                else:
                    element.text = str(item)
    
    def _xml_to_dict(self, element: ET.Element) -> Any:
        """Convert XML element to dictionary."""
        result = {}
        
        # Handle child elements
        for child in element:
            key = child.get('original_key', child.tag)
            
            if child.tag == 'item':
                # Handle list items
                if 'list' not in result:
                    result['list'] = []
                
                if len(child) > 0:
                    result['list'].append(self._xml_to_dict(child))
                else:
                    result['list'].append(self._convert_xml_value(child.text))
            else:
                if len(child) > 0:
                    result[key] = self._xml_to_dict(child)
                else:
                    result[key] = self._convert_xml_value(child.text)
        
        # If no children and has text, return the text value
        if not result and element.text:
            return self._convert_xml_value(element.text)
        
        return result
    
    def _convert_xml_value(self, value: str) -> Any:
        """Convert XML text value to appropriate Python type."""
        if value is None:
            return None
        
        # Try boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _make_safe_xml_name(self, name: str) -> str:
        """Make a string safe for use as an XML element name."""
        # Replace invalid characters with underscores
        safe_name = ""
        for char in name:
            if char.isalnum() or char in ('-', '_', '.'):
                safe_name += char
            else:
                safe_name += '_'
        
        # Ensure it starts with a letter or underscore
        if safe_name and not (safe_name[0].isalpha() or safe_name[0] == '_'):
            safe_name = '_' + safe_name
        
        return safe_name or '_'
    
    def _indent_xml(self, elem: ET.Element, level: int = 0) -> None:
        """Add indentation to XML for pretty printing."""
        indent = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for elem in elem:
                self._indent_xml(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent


class SettingSerializerFactory:
    """Factory for creating setting serializers."""
    
    _serializers = {
        SettingFormat.YAML: YamlSettingSerializer,
        SettingFormat.JSON: JsonSettingSerializer,
        SettingFormat.INI: IniSettingSerializer,
        SettingFormat.XML: XmlSettingSerializer,
    }
    
    @classmethod
    def create(cls, format: SettingFormat, **kwargs) -> ISettingSerializer:
        """
        Create a serializer for the specified format.
        
        Args:
            format: The serialization format
            **kwargs: Additional arguments for the serializer
            
        Returns:
            ISettingSerializer instance
            
        Raises:
            ValueError: If format is not supported
        """
        if format not in cls._serializers:
            raise ValueError(f"Unsupported serialization format: {format}")
        
        return cls._serializers[format](**kwargs)
    
    @classmethod
    def get_supported_formats(cls) -> list[SettingFormat]:
        """Get list of supported serialization formats."""
        return list(cls._serializers.keys())
