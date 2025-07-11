#!/usr/bin/env python3
"""
Chronicles of Aethermoor - Main Entry Point
A comprehensive fantasy RPG with complex systems and deep gameplay
"""

import sys
import os
import traceback
import pygame

# Add the game directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'game'))

from game.engine.game_engine import GameEngine
from game.engine.config import Config
from game.engine.logger import Logger

def main():
    """Main entry point for Chronicles of Aethermoor"""
    try:
        # Initialize logging
        logger = Logger()
        logger.info("Starting Chronicles of Aethermoor...")
        
        # Initialize Pygame
        pygame.init()
        
        # Load configuration
        config = Config()
        
        # Create and run the game engine
        game_engine = GameEngine(config, logger)
        game_engine.run()
        
    except Exception as e:
        print(f"Fatal error occurred: {e}")
        traceback.print_exc()
        return 1
    
    finally:
        # Cleanup
        pygame.quit()
        
    return 0

if __name__ == "__main__":
    sys.exit(main())