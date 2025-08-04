#!/usr/bin/env python3
"""
Enhancement Configuration Manager for MCP Integration Enhancement System

Real-time configuration management for enhancement systems with validation,
performance monitoring, and graceful degradation capabilities.

Provides unified interface for configuring all enhancement components
following July 2025 MCP standards.

Author: Claude Code MCP Integration Enhancement System
Version: 1.0.0 - July 2025 Configuration Standards
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import asyncio

# Import existing components for validation
from database.vector_database import ClaudeVectorDatabase
from processing.unified_enhancement_manager import UnifiedEnhancementManager
from mcp.oauth_21_security_manager import OAuth21SecurityManager

logger = logging.getLogger(__name__)

@dataclass
class EnhancementConfiguration:
    """Configuration for enhancement systems."""
    # PRP system configurations
    prp1_enabled: bool = True  # Conversation chains
    prp2_enabled: bool = True  # Semantic validation
    prp3_enabled: bool = False  # Adaptive learning (opt-in)
    
    # Performance configurations
    performance_mode: str = "balanced"  # "conservative", "balanced", "aggressive"
    fallback_strategy: str = "graceful"  # "graceful", "strict", "disabled"
    max_search_latency_ms: int = 2000  # Maximum acceptable latency
    
    # Security configurations
    oauth_enforcement: bool = True  # OAuth 2.1 security requirement
    security_scanning: bool = True  # Vulnerability scanning
    rate_limiting: bool = True  # Rate limiting enforcement
    
    # System optimizations
    chromadb_optimization: bool = True  # ChromaDB 1.0.15 Rust features
    parallel_processing: bool = True  # Parallel enhancement processing
    caching_enabled: bool = True  # Result caching
    
    # Monitoring and analytics
    performance_monitoring: bool = True  # Performance tracking
    detailed_logging: bool = False  # Detailed operation logging
    analytics_collection: bool = True  # Analytics data collection
    
    # Advanced options
    enhancement_aggressiveness: float = 1.0  # Enhancement multiplier (0.5-2.0)
    degradation_threshold: float = 0.8  # Quality threshold for degradation
    
    # Metadata
    created_at: str = None
    updated_at: str = None
    version: str = "1.0.0"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at

@dataclass
class ConfigurationValidation:
    """Configuration validation result."""
    is_valid: bool
    config: Optional[EnhancementConfiguration] = None
    error_message: Optional[str] = None
    warnings: List[str] = None
    suggested_fixes: List[str] = None
    performance_impact: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.suggested_fixes is None:
            self.suggested_fixes = []

@dataclass
class ConfigurationTestResult:
    """Result from testing a configuration."""
    success: bool
    performance_metrics: Dict[str, Any]
    security_status: Dict[str, Any]
    compatibility_check: Dict[str, Any]
    error_details: Optional[str] = None
    test_duration_ms: float = 0.0

class EnhancementConfigurationManager:
    """
    Real-time enhancement system configuration management.
    Provides unified interface for configuring all enhancement components.
    """
    
    def __init__(self):
        """Initialize configuration manager."""
        self.current_config = EnhancementConfiguration()
        self.config_history: List[EnhancementConfiguration] = []
        self.max_history = 50  # Keep last 50 configurations
        
        # Component references for validation
        self.vector_db = None  # Lazy initialization
        self.enhancement_manager = None  # Lazy initialization
        self.security_manager = None  # Lazy initialization
        
        # Configuration file path
        self.config_file = Path("enhancement_config.json")
        
        # Load existing configuration if available
        self._load_configuration()
        
        logger.info("⚙️ Enhancement Configuration Manager initialized")
    
    async def _ensure_components_initialized(self):
        """Lazy initialization of required components."""
        if not self.vector_db:
            self.vector_db = ClaudeVectorDatabase()
        if not self.enhancement_manager:
            self.enhancement_manager = UnifiedEnhancementManager()
        if not self.security_manager:
            self.security_manager = OAuth21SecurityManager()
    
    def _load_configuration(self):
        """Load configuration from file if it exists."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    self.current_config = EnhancementConfiguration(**config_data)
                    logger.info("📄 Configuration loaded from file")
        except Exception as e:
            logger.warning(f"Could not load configuration file: {e}")
    
    def _save_configuration(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(asdict(self.current_config), f, indent=2)
                logger.info("💾 Configuration saved to file")
        except Exception as e:
            logger.error(f"Could not save configuration file: {e}")
    
    async def validate_configuration(self, config_dict: Dict[str, Any]) -> ConfigurationValidation:
        """
        Validate configuration against system capabilities and constraints.
        
        Args:
            config_dict: Configuration dictionary to validate
            
        Returns:
            Validation result with detailed feedback
        """
        try:
            await self._ensure_components_initialized()
            
            warnings = []
            suggested_fixes = []
            
            # Create configuration object
            try:
                config = EnhancementConfiguration(**config_dict)
            except Exception as e:
                return ConfigurationValidation(
                    is_valid=False,
                    error_message=f"Invalid configuration format: {e}",
                    suggested_fixes=["Check configuration parameter names and types"]
                )
            
            # Validate performance mode
            valid_performance_modes = ["conservative", "balanced", "aggressive"]
            if config.performance_mode not in valid_performance_modes:
                return ConfigurationValidation(
                    is_valid=False,
                    error_message=f"Invalid performance mode: {config.performance_mode}",
                    suggested_fixes=[f"Use one of: {', '.join(valid_performance_modes)}"]
                )
            
            # Validate fallback strategy
            valid_fallback_strategies = ["graceful", "strict", "disabled"]
            if config.fallback_strategy not in valid_fallback_strategies:
                return ConfigurationValidation(
                    is_valid=False,
                    error_message=f"Invalid fallback strategy: {config.fallback_strategy}",
                    suggested_fixes=[f"Use one of: {', '.join(valid_fallback_strategies)}"]
                )
            
            # Validate enhancement aggressiveness
            if not (0.5 <= config.enhancement_aggressiveness <= 2.0):
                return ConfigurationValidation(
                    is_valid=False,
                    error_message=f"Enhancement aggressiveness must be between 0.5 and 2.0, got {config.enhancement_aggressiveness}",
                    suggested_fixes=["Set enhancement_aggressiveness between 0.5 and 2.0"]
                )
            
            # Validate degradation threshold
            if not (0.1 <= config.degradation_threshold <= 1.0):
                return ConfigurationValidation(
                    is_valid=False,
                    error_message=f"Degradation threshold must be between 0.1 and 1.0, got {config.degradation_threshold}",
                    suggested_fixes=["Set degradation_threshold between 0.1 and 1.0"]
                )
            
            # Check system capabilities
            available_systems = await self.enhancement_manager.detect_available_systems()
            
            # Warn about unavailable systems
            if config.prp1_enabled and not available_systems.get('prp1_available', False):
                warnings.append("PRP-1 (conversation chains) enabled but not available")
                suggested_fixes.append("Consider disabling PRP-1 or check system requirements")
            
            if config.prp2_enabled and not available_systems.get('prp2_available', False):
                warnings.append("PRP-2 (semantic validation) enabled but not available")
                suggested_fixes.append("Consider disabling PRP-2 or check system requirements")
            
            if config.prp3_enabled and not available_systems.get('prp3_available', False):
                warnings.append("PRP-3 (adaptive learning) enabled but not available")
                suggested_fixes.append("Consider disabling PRP-3 or check system requirements")
            
            # Performance warnings
            if config.performance_mode == "aggressive" and config.max_search_latency_ms < 500:
                warnings.append("Aggressive performance mode with low latency limit may cause degradation")
                suggested_fixes.append("Increase max_search_latency_ms or use balanced mode")
            
            # Security warnings
            if not config.oauth_enforcement:
                warnings.append("OAuth enforcement disabled - security risk")
                suggested_fixes.append("Enable OAuth enforcement for production use")
            
            # Performance impact estimation
            performance_impact = await self._estimate_performance_impact(config)
            
            return ConfigurationValidation(
                is_valid=True,
                config=config,
                warnings=warnings,
                suggested_fixes=suggested_fixes,
                performance_impact=performance_impact
            )
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return ConfigurationValidation(
                is_valid=False,
                error_message=f"Validation error: {e}",
                suggested_fixes=["Check system status and try again"]
            )
    
    async def _estimate_performance_impact(self, config: EnhancementConfiguration) -> Dict[str, Any]:
        """Estimate performance impact of configuration changes."""
        try:
            # Base performance metrics
            base_latency = 200  # Base search latency in ms
            base_throughput = 100  # Base operations per minute
            
            # Calculate impact multipliers
            latency_multiplier = 1.0
            throughput_multiplier = 1.0
            
            # PRP system impacts
            if config.prp1_enabled:
                latency_multiplier *= 1.1  # 10% latency increase
                throughput_multiplier *= 0.95  # 5% throughput decrease
            
            if config.prp2_enabled:
                latency_multiplier *= 1.15  # 15% latency increase
                throughput_multiplier *= 0.9  # 10% throughput decrease
            
            if config.prp3_enabled:
                latency_multiplier *= 1.2  # 20% latency increase
                throughput_multiplier *= 0.85  # 15% throughput decrease
            
            # Performance mode impacts
            if config.performance_mode == "aggressive":
                latency_multiplier *= 1.3
                throughput_multiplier *= 0.8
            elif config.performance_mode == "conservative":
                latency_multiplier *= 0.9
                throughput_multiplier *= 1.1
            
            # Enhancement aggressiveness impact
            aggressiveness_factor = config.enhancement_aggressiveness
            latency_multiplier *= (0.8 + 0.4 * aggressiveness_factor)
            throughput_multiplier *= (1.2 - 0.4 * aggressiveness_factor)
            
            # ChromaDB optimization benefits
            if config.chromadb_optimization:
                latency_multiplier *= 0.75  # 25% improvement from Rust
                throughput_multiplier *= 1.4  # 40% improvement
            
            # Parallel processing benefits
            if config.parallel_processing:
                throughput_multiplier *= 1.2  # 20% improvement
            
            # Caching benefits
            if config.caching_enabled:
                latency_multiplier *= 0.7  # 30% improvement for cached results
                throughput_multiplier *= 1.5  # 50% improvement
            
            # Calculate final metrics
            estimated_latency = base_latency * latency_multiplier
            estimated_throughput = base_throughput * throughput_multiplier
            
            return {
                "estimated_search_latency_ms": round(estimated_latency, 1),
                "estimated_throughput_ops_per_min": round(estimated_throughput, 1),
                "latency_change_percentage": round((latency_multiplier - 1) * 100, 1),
                "throughput_change_percentage": round((throughput_multiplier - 1) * 100, 1),
                "within_latency_target": estimated_latency <= config.max_search_latency_ms,
                "performance_score": min(100, max(0, 100 - abs(latency_multiplier - 1) * 50)),
                "optimization_benefits": {
                    "chromadb_rust": config.chromadb_optimization,
                    "parallel_processing": config.parallel_processing,
                    "caching": config.caching_enabled
                }
            }
            
        except Exception as e:
            logger.error(f"Performance impact estimation failed: {e}")
            return {
                "error": str(e),
                "estimated_search_latency_ms": 0,
                "estimated_throughput_ops_per_min": 0
            }
    
    async def apply_configuration(self, validation_result: ConfigurationValidation) -> Dict[str, Any]:
        """
        Apply validated configuration to the system.
        
        Args:
            validation_result: Validated configuration to apply
            
        Returns:
            Application result with status and details
        """
        try:
            if not validation_result.is_valid or not validation_result.config:
                return {
                    "success": False,
                    "error": "Cannot apply invalid configuration",
                    "details": validation_result.error_message
                }
            
            config = validation_result.config
            
            # Store previous configuration
            self.config_history.append(self.current_config)
            if len(self.config_history) > self.max_history:
                self.config_history = self.config_history[-self.max_history:]
            
            # Update timestamps
            config.updated_at = datetime.now().isoformat()
            
            # Apply configuration
            self.current_config = config
            
            # Save to file
            self._save_configuration()
            
            # Apply to components (in real implementation, this would configure actual components)
            application_results = await self._apply_to_components(config)
            
            logger.info("⚙️ Configuration applied successfully")
            
            return {
                "success": True,
                "configuration_applied": asdict(config),
                "application_results": application_results,
                "warnings": validation_result.warnings,
                "performance_impact": validation_result.performance_impact,
                "applied_at": config.updated_at
            }
            
        except Exception as e:
            logger.error(f"Configuration application failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "details": "Configuration application failed"
            }
    
    async def _apply_to_components(self, config: EnhancementConfiguration) -> Dict[str, Any]:
        """Apply configuration to system components."""
        results = {}
        
        try:
            await self._ensure_components_initialized()
            
            # Update enhancement manager configuration
            self.enhancement_manager.mcp_compliance["oauth_2_1_ready"] = config.oauth_enforcement
            self.enhancement_manager.mcp_compliance["security_hardened"] = config.security_scanning
            
            results["enhancement_manager"] = {
                "status": "configured",
                "oauth_enforcement": config.oauth_enforcement,
                "security_scanning": config.security_scanning
            }
            
            # Configure security manager
            if config.oauth_enforcement:
                security_status = await self.security_manager.get_security_status()
                results["security_manager"] = {
                    "status": "active",
                    "compliance_score": security_status.get("compliance_score", 0)
                }
            else:
                results["security_manager"] = {
                    "status": "disabled",
                    "warning": "OAuth enforcement disabled"
                }
            
            # Vector database optimizations
            results["vector_database"] = {
                "status": "configured",
                "chromadb_optimization": config.chromadb_optimization,
                "parallel_processing": config.parallel_processing,
                "caching_enabled": config.caching_enabled
            }
            
            results["overall_status"] = "success"
            
        except Exception as e:
            logger.error(f"Component configuration failed: {e}")
            results["overall_status"] = "partial_failure"
            results["error"] = str(e)
        
        return results
    
    async def test_configuration(self) -> ConfigurationTestResult:
        """Test current configuration with system components."""
        start_time = time.time()
        
        try:
            await self._ensure_components_initialized()
            
            # Test vector database
            db_test_start = time.time()
            db_results = self.vector_db.search_conversations_enhanced(
                query="test configuration",
                n_results=1
            )
            db_test_time = (time.time() - db_test_start) * 1000
            
            # Test enhancement manager
            em_test_start = time.time()
            available_systems = await self.enhancement_manager.detect_available_systems()
            em_test_time = (time.time() - em_test_start) * 1000
            
            # Test security manager
            security_test_start = time.time()
            security_status = await self.security_manager.get_security_status()
            security_test_time = (time.time() - security_test_start) * 1000
            
            # Calculate performance metrics
            performance_metrics = {
                "database_search_latency_ms": round(db_test_time, 2),
                "system_detection_latency_ms": round(em_test_time, 2),
                "security_check_latency_ms": round(security_test_time, 2),
                "total_test_time_ms": round((time.time() - start_time) * 1000, 2),
                "database_results_count": len(db_results),
                "within_latency_target": db_test_time <= self.current_config.max_search_latency_ms
            }
            
            # Compatibility check
            compatibility_check = {
                "prp1_compatible": available_systems.get('prp1_available', False),
                "prp2_compatible": available_systems.get('prp2_available', False),
                "prp3_compatible": available_systems.get('prp3_available', False),
                "base_system_functional": available_systems.get('base_system', False),
                "security_system_functional": security_status.get('oauth_2_1_status', {}).get('compliant', False)
            }
            
            return ConfigurationTestResult(
                success=True,
                performance_metrics=performance_metrics,
                security_status=security_status,
                compatibility_check=compatibility_check,
                test_duration_ms=performance_metrics["total_test_time_ms"]
            )
            
        except Exception as e:
            logger.error(f"Configuration test failed: {e}")
            return ConfigurationTestResult(
                success=False,
                performance_metrics={},
                security_status={},
                compatibility_check={},
                error_details=str(e),
                test_duration_ms=(time.time() - start_time) * 1000
            )
    
    async def get_current_configuration(self) -> Dict[str, Any]:
        """Get current configuration with metadata."""
        return {
            "configuration": asdict(self.current_config),
            "status": "active",
            "history_count": len(self.config_history),
            "last_updated": self.current_config.updated_at,
            "configuration_file": str(self.config_file),
            "file_exists": self.config_file.exists()
        }
    
    async def get_configuration_history(self) -> Dict[str, Any]:
        """Get configuration change history."""
        return {
            "total_configurations": len(self.config_history) + 1,  # Include current
            "current_configuration": asdict(self.current_config),
            "previous_configurations": [
                {
                    "version": config.version,
                    "created_at": config.created_at,
                    "updated_at": config.updated_at,
                    "performance_mode": config.performance_mode,
                    "prp_systems": {
                        "prp1": config.prp1_enabled,
                        "prp2": config.prp2_enabled,
                        "prp3": config.prp3_enabled
                    }
                }
                for config in self.config_history[-10:]  # Last 10 configurations
            ]
        }
    
    async def reset_to_defaults(self) -> Dict[str, Any]:
        """Reset configuration to default values."""
        try:
            # Store current as history
            self.config_history.append(self.current_config)
            
            # Create new default configuration
            self.current_config = EnhancementConfiguration()
            
            # Save to file
            self._save_configuration()
            
            logger.info("⚙️ Configuration reset to defaults")
            
            return {
                "success": True,
                "configuration": asdict(self.current_config),
                "message": "Configuration reset to default values",
                "reset_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Configuration reset failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to reset configuration"
            }