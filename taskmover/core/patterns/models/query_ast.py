"""
Simplified Query AST Models

Fixed version without complex inheritance and dataclass field ordering issues.
"""

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class QueryNodeType(Enum):
    """Types of query AST nodes."""
    LITERAL = "literal"
    FIELD_ACCESS = "field_access"
    BINARY_OP = "binary_op"
    UNARY_OP = "unary_op"
    FUNCTION_CALL = "function_call"
    LIKE_PATTERN = "like_pattern"
    GROUP_REFERENCE = "group_reference"
    TOKEN_REFERENCE = "token_reference"


class BinaryOperator(Enum):
    """Binary operators for query conditions."""
    EQUALS = "="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LIKE = "LIKE"
    REGEXP = "REGEXP"
    AND = "AND"
    OR = "OR"
    IN = "IN"
    NOT_IN = "NOT IN"
    CONTAINS = "CONTAINS"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"


class UnaryOperator(Enum):
    """Unary operators for query conditions."""
    NOT = "NOT"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"


# Simple classes without complex inheritance

@dataclass
class LiteralNode:
    """Literal value node."""
    value: Any
    value_type: str = "string"
    estimated_cost: int = 1
    
    @property
    def node_type(self) -> QueryNodeType:
        return QueryNodeType.LITERAL


@dataclass 
class FieldAccessNode:
    """Field access node (e.g., 'name', 'size', 'modified')."""
    field_name: str
    estimated_cost: int = 1
    
    @property
    def node_type(self) -> QueryNodeType:
        return QueryNodeType.FIELD_ACCESS


@dataclass
class BinaryOpNode:
    """Binary operation node."""
    operator: BinaryOperator
    left: Any  # QueryNode type (avoiding circular reference)
    right: Any  # QueryNode type (avoiding circular reference)
    estimated_cost: int = 1
    
    @property
    def node_type(self) -> QueryNodeType:
        return QueryNodeType.BINARY_OP


@dataclass
class UnaryOpNode:
    """Unary operation node."""
    operator: UnaryOperator
    operand: Any  # QueryNode type (avoiding circular reference)
    estimated_cost: int = 1
    
    @property
    def node_type(self) -> QueryNodeType:
        return QueryNodeType.UNARY_OP


@dataclass
class FunctionCallNode:
    """Function call node."""
    function_name: str
    arguments: List[Any] = field(default_factory=list)  # List[QueryNode]
    estimated_cost: int = 1
    
    @property
    def node_type(self) -> QueryNodeType:
        return QueryNodeType.FUNCTION_CALL


@dataclass
class LikePatternNode:
    """LIKE pattern matching node."""
    field: Any  # QueryNode type
    pattern: str
    case_sensitive: bool = True
    estimated_cost: int = 3  # Pattern matching is expensive
    
    @property
    def node_type(self) -> QueryNodeType:
        return QueryNodeType.LIKE_PATTERN


@dataclass
class GroupReferenceNode:
    """Pattern group reference node."""
    group_name: str
    estimated_cost: int = 1
    
    @property
    def node_type(self) -> QueryNodeType:
        return QueryNodeType.GROUP_REFERENCE


@dataclass
class TokenReferenceNode:
    """Dynamic token reference node."""
    token_name: str
    token_params: Dict[str, Any] = field(default_factory=dict)
    estimated_cost: int = 1
    
    @property
    def node_type(self) -> QueryNodeType:
        return QueryNodeType.TOKEN_REFERENCE


# Union type for all query nodes
QueryNode = Union[
    LiteralNode,
    FieldAccessNode, 
    BinaryOpNode,
    UnaryOpNode,
    FunctionCallNode,
    LikePatternNode,
    GroupReferenceNode,
    TokenReferenceNode
]


@dataclass
class QueryAST:
    """
    Query Abstract Syntax Tree.
    
    Represents a parsed query with optimized internal structure.
    """
    root: Optional[QueryNode] = None
    estimated_cost: int = 1
    optimized: bool = False
    original_input: str = ""
    
    def get_complexity_score(self) -> int:
        """Calculate complexity score for the entire query."""
        if not self.root:
            return 0
        return self._calculate_node_complexity(self.root)
    
    def _calculate_node_complexity(self, node: QueryNode) -> int:
        """Recursively calculate complexity for a node."""
        if hasattr(node, 'estimated_cost'):
            return getattr(node, 'estimated_cost', 1)
        return 1
    
    def get_referenced_fields(self) -> List[str]:
        """Get all field names referenced in the query."""
        fields = []
        self._collect_fields(self.root, fields)
        return list(set(fields))  # Remove duplicates
    
    def _collect_fields(self, node: Optional[QueryNode], fields: List[str]) -> None:
        """Recursively collect field references."""
        if not node:
            return
            
        if isinstance(node, FieldAccessNode):
            fields.append(node.field_name)
        elif isinstance(node, BinaryOpNode):
            self._collect_fields(node.left, fields)
            self._collect_fields(node.right, fields)
        elif isinstance(node, UnaryOpNode):
            self._collect_fields(node.operand, fields)
        elif isinstance(node, FunctionCallNode) and node.arguments:
            for arg in node.arguments:
                self._collect_fields(arg, fields)
        elif isinstance(node, LikePatternNode):
            self._collect_fields(node.field, fields)


# Simple builder functions to avoid constructor parameter issues
def create_binary_op(operator: BinaryOperator, left: QueryNode, right: QueryNode) -> BinaryOpNode:
    """Create a binary operation node."""
    return BinaryOpNode(operator=operator, left=left, right=right)


def create_unary_op(operator: UnaryOperator, operand: QueryNode) -> UnaryOpNode:
    """Create a unary operation node.""" 
    return UnaryOpNode(operator=operator, operand=operand)


def create_function_call(function_name: str, arguments: List[QueryNode] = None) -> FunctionCallNode:
    """Create a function call node."""
    return FunctionCallNode(function_name=function_name, arguments=arguments or [])


def create_like_pattern(field: QueryNode, pattern: str, case_sensitive: bool = True) -> LikePatternNode:
    """Create a LIKE pattern node."""
    return LikePatternNode(field=field, pattern=pattern, case_sensitive=case_sensitive)
