"""
Conflict Resolver

Core resolver that executes conflict resolution strategies.
"""

from typing import Dict, Any, Optional
from uuid import UUID

from ..logging import get_logger
from .models import Conflict, ResolutionResult
from .enums import ResolutionStrategy
from .strategies import BaseResolutionStrategy


class ConflictResolver:
    """
    Core resolver that manages and executes conflict resolution strategies.
    """
    
    def __init__(self):
        self._logger = get_logger("conflict_resolver")
        self._strategies: Dict[ResolutionStrategy, BaseResolutionStrategy] = {}
        
        self._logger.info("ConflictResolver initialized")
    
    def register_strategy(self, strategy: BaseResolutionStrategy) -> None:
        """Register a resolution strategy."""
        strategy_enum = ResolutionStrategy(strategy.name.lower())
        self._strategies[strategy_enum] = strategy
        self._logger.debug(f"Registered strategy: {strategy.name}")
    
    def unregister_strategy(self, strategy_type: ResolutionStrategy) -> bool:
        """Unregister a resolution strategy."""
        if strategy_type in self._strategies:
            del self._strategies[strategy_type]
            self._logger.debug(f"Unregistered strategy: {strategy_type.value}")
            return True
        return False
    
    def get_available_strategies(self, conflict: Conflict) -> Dict[ResolutionStrategy, BaseResolutionStrategy]:
        """Get all strategies that can handle the given conflict."""
        available = {}
        
        for strategy_type, strategy in self._strategies.items():
            if strategy.can_resolve(conflict):
                available[strategy_type] = strategy
        
        return available
    
    def resolve(self, 
                conflict: Conflict, 
                strategy_type: ResolutionStrategy,
                config: Optional[Dict[str, Any]] = None) -> ResolutionResult:
        """
        Resolve a conflict using the specified strategy.
        
        Args:
            conflict: The conflict to resolve
            strategy_type: The resolution strategy to use
            config: Optional configuration for the strategy
            
        Returns:
            ResolutionResult indicating success/failure and details
        """
        try:
            if strategy_type not in self._strategies:
                return ResolutionResult(
                    conflict_id=conflict.id,
                    success=False,
                    strategy_used=strategy_type,
                    error_message=f"Strategy {strategy_type.value} not registered"
                )
            
            strategy = self._strategies[strategy_type]
            
            if not strategy.can_resolve(conflict):
                return ResolutionResult(
                    conflict_id=conflict.id,
                    success=False,
                    strategy_used=strategy_type,
                    error_message=f"Strategy {strategy_type.value} cannot resolve this conflict type"
                )
            
            self._logger.info(f"Resolving conflict {conflict.id} with {strategy_type.value}")
            
            # Execute the strategy
            result = strategy.resolve(conflict, config or {})
            
            if result.success:
                self._logger.info(f"Successfully resolved conflict {conflict.id}")
            else:
                self._logger.warning(f"Failed to resolve conflict {conflict.id}: {result.error_message}")
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error resolving conflict {conflict.id}: {e}")
            return ResolutionResult(
                conflict_id=conflict.id,
                success=False,
                strategy_used=strategy_type,
                error_message=f"Unexpected error during resolution: {e}"
            )
    
    def estimate_resolution_impact(self, 
                                 conflict: Conflict,
                                 strategy_type: ResolutionStrategy) -> Optional[Dict[str, Any]]:
        """
        Estimate the impact of resolving a conflict with a specific strategy.
        
        Args:
            conflict: The conflict to analyze
            strategy_type: The strategy to estimate impact for
            
        Returns:
            Dictionary with impact estimation or None if strategy not available
        """
        if strategy_type not in self._strategies:
            return None
        
        strategy = self._strategies[strategy_type]
        
        if not strategy.can_resolve(conflict):
            return None
        
        try:
            return strategy.estimate_impact(conflict)
        except Exception as e:
            self._logger.error(f"Error estimating impact for {strategy_type.value}: {e}")
            return None
    
    def get_strategy_recommendations(self, conflict: Conflict) -> Dict[ResolutionStrategy, Dict[str, Any]]:
        """
        Get recommendations for strategies that can resolve the conflict.
        
        Args:
            conflict: The conflict to get recommendations for
            
        Returns:
            Dictionary mapping strategies to their impact estimations
        """
        recommendations = {}
        available_strategies = self.get_available_strategies(conflict)
        
        for strategy_type, strategy in available_strategies.items():
            try:
                impact = strategy.estimate_impact(conflict)
                recommendations[strategy_type] = {
                    "can_resolve": True,
                    "impact": impact,
                    "strategy_name": strategy.name
                }
            except Exception as e:
                self._logger.warning(f"Could not estimate impact for {strategy_type.value}: {e}")
                recommendations[strategy_type] = {
                    "can_resolve": True,
                    "impact": {"error": str(e)},
                    "strategy_name": strategy.name
                }
        
        return recommendations
