"""
Logging System for Chronicles of Aethermoor
Provides structured logging for debugging and monitoring
"""

import logging
import os
import sys
from datetime import datetime
from enum import Enum
from typing import Optional


class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Logger:
    """Enhanced logging system for the game"""
    
    _instance: Optional['Logger'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'Logger':
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_file: str = "game.log", level: LogLevel = LogLevel.INFO):
        """Initialize the logger (only once due to singleton)"""
        if self._initialized:
            return
            
        self.log_file = log_file
        self.level = level
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else "logs"
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Set up the logger
        self.logger = logging.getLogger("AethermoorRPG")
        self.logger.setLevel(level.value)
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler for detailed logging
        file_handler = logging.FileHandler(
            os.path.join(log_dir, log_file) if log_dir != "logs" else os.path.join("logs", log_file)
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler for important messages
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
        
        self._initialized = True
        self.info("Logger initialized successfully")
    
    def debug(self, message: str, category: str = "GENERAL") -> None:
        """Log debug message"""
        self.logger.debug(f"[{category}] {message}")
    
    def info(self, message: str, category: str = "GENERAL") -> None:
        """Log info message"""
        self.logger.info(f"[{category}] {message}")
    
    def warning(self, message: str, category: str = "GENERAL") -> None:
        """Log warning message"""
        self.logger.warning(f"[{category}] {message}")
    
    def error(self, message: str, category: str = "GENERAL", exception: Optional[Exception] = None) -> None:
        """Log error message"""
        error_msg = f"[{category}] {message}"
        if exception:
            error_msg += f" - Exception: {str(exception)}"
        self.logger.error(error_msg)
    
    def critical(self, message: str, category: str = "GENERAL", exception: Optional[Exception] = None) -> None:
        """Log critical message"""
        critical_msg = f"[{category}] {message}"
        if exception:
            critical_msg += f" - Exception: {str(exception)}"
        self.logger.critical(critical_msg)
    
    def log_game_event(self, event_type: str, details: str) -> None:
        """Log game-specific events"""
        self.info(f"Game Event - {event_type}: {details}", "GAME_EVENT")
    
    def log_combat(self, action: str, attacker: str, target: str = "", damage: int = 0) -> None:
        """Log combat actions"""
        combat_msg = f"{attacker} {action}"
        if target:
            combat_msg += f" -> {target}"
        if damage > 0:
            combat_msg += f" (Damage: {damage})"
        self.debug(combat_msg, "COMBAT")
    
    def log_quest(self, quest_name: str, action: str, details: str = "") -> None:
        """Log quest-related events"""
        quest_msg = f"Quest '{quest_name}' - {action}"
        if details:
            quest_msg += f": {details}"
        self.info(quest_msg, "QUEST")
    
    def log_performance(self, function_name: str, execution_time: float) -> None:
        """Log performance metrics"""
        self.debug(f"Performance - {function_name}: {execution_time:.4f}s", "PERFORMANCE")
    
    def log_save_load(self, action: str, save_name: str, success: bool) -> None:
        """Log save/load operations"""
        status = "SUCCESS" if success else "FAILED"
        self.info(f"Save/Load - {action} '{save_name}': {status}", "SAVE_LOAD")
    
    def log_world_event(self, event_type: str, location: str, details: str) -> None:
        """Log world simulation events"""
        self.debug(f"World Event - {event_type} at {location}: {details}", "WORLD")
    
    def set_level(self, level: LogLevel) -> None:
        """Change the logging level"""
        self.level = level
        self.logger.setLevel(level.value)
        self.info(f"Log level changed to {level.name}")
    
    def flush(self) -> None:
        """Flush all handlers"""
        for handler in self.logger.handlers:
            handler.flush()
    
    def close(self) -> None:
        """Close all handlers"""
        for handler in self.logger.handlers:
            handler.close()
        self.logger.handlers.clear()


# Convenience function for getting the logger instance
def get_logger() -> Logger:
    """Get the singleton logger instance"""
    return Logger()