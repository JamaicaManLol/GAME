"""
Main Game Engine for Chronicles of Aethermoor
Coordinates all game systems and manages the main game loop
"""

import pygame
import sys
import time
from typing import Optional, Dict, Any

from .config import Config
from .logger import Logger
from .event_manager import EventManager, EventType
from .state_manager import StateManager, StateType
from .time_manager import TimeManager


class GameEngine:
    """Main game engine that coordinates all systems"""
    
    def __init__(self, config: Config, logger: Logger):
        """Initialize the game engine"""
        self.config = config
        self.logger = logger
        self.running = False
        
        # Core systems
        self.event_manager = EventManager()
        self.state_manager = StateManager()
        self.time_manager = TimeManager()
        
        # Pygame systems
        self.screen: Optional[pygame.Surface] = None
        self.clock = pygame.time.Clock()
        
        # Performance tracking
        self.frame_count = 0
        self.total_time = 0.0
        self.last_fps_update = 0.0
        self.current_fps = 0.0
        
        # Game state
        self.delta_time = 0.0
        self.last_frame_time = 0.0
        
        self.logger.info("Game Engine initialized")
    
    def initialize(self) -> bool:
        """Initialize all game systems"""
        try:
            # Initialize display
            if not self._initialize_display():
                return False
            
            # Initialize game states
            if not self._initialize_states():
                return False
            
            # Initialize input system
            if not self._initialize_input():
                return False
            
            # Set initial game state
            self.state_manager.change_state(StateType.SPLASH_SCREEN)
            
            self.logger.info("Game Engine initialization complete")
            return True
            
        except Exception as e:
            self.logger.error("Failed to initialize game engine", exception=e)
            return False
    
    def _initialize_display(self) -> bool:
        """Initialize the display system"""
        try:
            # Set up display
            display_flags = 0
            if self.config.display.fullscreen:
                display_flags |= pygame.FULLSCREEN
            if self.config.display.vsync:
                display_flags |= pygame.DOUBLEBUF
            
            self.screen = pygame.display.set_mode(
                self.config.get_resolution(),
                display_flags
            )
            
            pygame.display.set_caption("Chronicles of Aethermoor")
            
            # Set up icon (placeholder)
            icon = pygame.Surface((32, 32))
            icon.fill((100, 50, 200))  # Purple color
            pygame.display.set_icon(icon)
            
            self.logger.info(f"Display initialized: {self.config.get_resolution()}")
            return True
            
        except Exception as e:
            self.logger.error("Failed to initialize display", exception=e)
            return False
    
    def _initialize_states(self) -> bool:
        """Initialize all game states"""
        try:
            # Import state classes (we'll implement these next)
            from ..states.splash_state import SplashState
            from ..states.main_menu_state import MainMenuState
            from ..states.gameplay_state import GameplayState
            from ..states.pause_state import PauseState
            
            # Register states
            self.state_manager.register_state(
                SplashState(StateType.SPLASH_SCREEN, self.state_manager)
            )
            self.state_manager.register_state(
                MainMenuState(StateType.MAIN_MENU, self.state_manager)
            )
            self.state_manager.register_state(
                GameplayState(StateType.GAMEPLAY, self.state_manager)
            )
            self.state_manager.register_state(
                PauseState(StateType.PAUSE_MENU, self.state_manager)
            )
            
            self.logger.info("Game states initialized")
            return True
            
        except ImportError as e:
            self.logger.warning(f"Some states not available yet: {e}")
            # For now, create placeholder states
            self._create_placeholder_states()
            return True
        except Exception as e:
            self.logger.error("Failed to initialize states", exception=e)
            return False
    
    def _create_placeholder_states(self) -> None:
        """Create placeholder states for development"""
        from .state_manager import GameState
        
        class PlaceholderState(GameState):
            def __init__(self, state_type, state_manager, color=(100, 100, 100)):
                super().__init__(state_type, state_manager)
                self.color = color
                self.font = None
            
            def enter(self, previous_state=None, data=None):
                super().enter(previous_state, data)
                try:
                    self.font = pygame.font.Font(None, 36)
                except:
                    self.font = None
            
            def exit(self, next_state=None):
                super().exit(next_state)
            
            def update(self, delta_time):
                pass
            
            def render(self, screen):
                screen.fill(self.color)
                if self.font:
                    text = self.font.render(
                        f"{self.state_type.value.replace('_', ' ').title()}", 
                        True, (255, 255, 255)
                    )
                    text_rect = text.get_rect(center=screen.get_rect().center)
                    screen.blit(text, text_rect)
                    
                    # Instructions
                    if self.state_type == StateType.SPLASH_SCREEN:
                        instruction = self.font.render("Press SPACE to continue", True, (200, 200, 200))
                        inst_rect = instruction.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50))
                        screen.blit(instruction, inst_rect)
                    elif self.state_type == StateType.MAIN_MENU:
                        instruction = self.font.render("Press ENTER to start game", True, (200, 200, 200))
                        inst_rect = instruction.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50))
                        screen.blit(instruction, inst_rect)
            
            def handle_event(self, event):
                if event.type == pygame.KEYDOWN:
                    if self.state_type == StateType.SPLASH_SCREEN and event.key == pygame.K_SPACE:
                        self.state_manager.change_state(StateType.MAIN_MENU)
                        return True
                    elif self.state_type == StateType.MAIN_MENU and event.key == pygame.K_RETURN:
                        self.state_manager.change_state(StateType.GAMEPLAY)
                        return True
                    elif self.state_type == StateType.GAMEPLAY and event.key == pygame.K_ESCAPE:
                        self.state_manager.push_state(StateType.PAUSE_MENU)
                        return True
                    elif self.state_type == StateType.PAUSE_MENU and event.key == pygame.K_ESCAPE:
                        self.state_manager.pop_state()
                        return True
                return False
        
        # Create placeholder states with different colors
        self.state_manager.register_state(
            PlaceholderState(StateType.SPLASH_SCREEN, self.state_manager, (50, 50, 100))
        )
        self.state_manager.register_state(
            PlaceholderState(StateType.MAIN_MENU, self.state_manager, (100, 50, 50))
        )
        self.state_manager.register_state(
            PlaceholderState(StateType.GAMEPLAY, self.state_manager, (50, 100, 50))
        )
        self.state_manager.register_state(
            PlaceholderState(StateType.PAUSE_MENU, self.state_manager, (100, 100, 50))
        )
    
    def _initialize_input(self) -> bool:
        """Initialize input handling"""
        try:
            # Set key repeat
            pygame.key.set_repeat(250, 50)  # Initial delay, repeat interval
            
            self.logger.info("Input system initialized")
            return True
            
        except Exception as e:
            self.logger.error("Failed to initialize input", exception=e)
            return False
    
    def run(self) -> None:
        """Main game loop"""
        if not self.initialize():
            self.logger.critical("Failed to initialize game engine")
            return
        
        self.running = True
        self.last_frame_time = time.time()
        self.last_fps_update = self.last_frame_time
        
        self.logger.info("Starting main game loop")
        
        try:
            while self.running:
                current_time = time.time()
                self.delta_time = current_time - self.last_frame_time
                self.last_frame_time = current_time
                
                # Cap delta time to prevent large jumps
                self.delta_time = min(self.delta_time, 1.0 / 20.0)  # Max 20 FPS minimum
                
                # Handle events
                self._handle_events()
                
                # Update systems
                self._update(self.delta_time)
                
                # Render
                self._render()
                
                # Update performance metrics
                self._update_performance_metrics(current_time)
                
                # Control frame rate
                self.clock.tick(self.config.display.fps_limit)
                
        except KeyboardInterrupt:
            self.logger.info("Game interrupted by user")
        except Exception as e:
            self.logger.critical("Critical error in main game loop", exception=e)
            raise
        finally:
            self.shutdown()
    
    def _handle_events(self) -> None:
        """Handle pygame events"""
        for event in pygame.event.get():
            # Check for quit events
            if event.type == pygame.QUIT:
                self.shutdown()
                return
            
            # Handle global key events
            if event.type == pygame.KEYDOWN:
                # Quick save/load
                if event.key == pygame.K_F5:
                    self._handle_quick_save()
                elif event.key == pygame.K_F9:
                    self._handle_quick_load()
                # Debug features
                elif event.key == pygame.K_F12:
                    self._toggle_debug_info()
                # Screenshot
                elif event.key == pygame.K_F10:
                    self._take_screenshot()
            
            # Pass event to state manager
            if not self.state_manager.handle_event(event):
                # Event not consumed by states, handle globally if needed
                pass
    
    def _update(self, delta_time: float) -> None:
        """Update all game systems"""
        # Update core systems
        self.time_manager.update(delta_time)
        self.event_manager.process_events()
        self.state_manager.update(delta_time)
    
    def _render(self) -> None:
        """Render the game"""
        if not self.screen:
            return
        
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render current state(s)
        self.state_manager.render(self.screen)
        
        # Render debug information if enabled
        self._render_debug_info()
        
        # Update display
        pygame.display.flip()
    
    def _render_debug_info(self) -> None:
        """Render debug information overlay"""
        if not hasattr(self, 'show_debug') or not self.show_debug:
            return
        
        try:
            font = pygame.font.Font(None, 24)
            y_offset = 10
            line_height = 25
            
            # FPS
            fps_text = font.render(f"FPS: {self.current_fps:.1f}", True, (255, 255, 0))
            self.screen.blit(fps_text, (10, y_offset))
            y_offset += line_height
            
            # Game time
            game_time = self.time_manager.get_time()
            time_text = font.render(f"Time: {game_time}", True, (255, 255, 0))
            self.screen.blit(time_text, (10, y_offset))
            y_offset += line_height
            
            # Current state
            current_state = self.state_manager.get_current_state()
            state_text = font.render(
                f"State: {current_state.state_type.value if current_state else 'None'}", 
                True, (255, 255, 0)
            )
            self.screen.blit(state_text, (10, y_offset))
            y_offset += line_height
            
            # Weather
            weather = self.time_manager.get_weather()
            weather_text = font.render(
                f"Weather: {weather.weather_type.value} ({weather.intensity:.1f})", 
                True, (255, 255, 0)
            )
            self.screen.blit(weather_text, (10, y_offset))
            
        except Exception as e:
            self.logger.error("Error rendering debug info", exception=e)
    
    def _update_performance_metrics(self, current_time: float) -> None:
        """Update performance tracking"""
        self.frame_count += 1
        self.total_time += self.delta_time
        
        # Update FPS every second
        if current_time - self.last_fps_update >= 1.0:
            self.current_fps = self.frame_count / (current_time - self.last_fps_update)
            self.frame_count = 0
            self.last_fps_update = current_time
    
    def _handle_quick_save(self) -> None:
        """Handle quick save"""
        self.logger.info("Quick save requested")
        # TODO: Implement save system
    
    def _handle_quick_load(self) -> None:
        """Handle quick load"""
        self.logger.info("Quick load requested")
        # TODO: Implement load system
    
    def _toggle_debug_info(self) -> None:
        """Toggle debug information display"""
        if not hasattr(self, 'show_debug'):
            self.show_debug = False
        self.show_debug = not self.show_debug
        self.logger.info(f"Debug info {'enabled' if self.show_debug else 'disabled'}")
    
    def _take_screenshot(self) -> None:
        """Take a screenshot"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            pygame.image.save(self.screen, filename)
            self.logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            self.logger.error("Failed to take screenshot", exception=e)
    
    def pause(self) -> None:
        """Pause the game"""
        self.time_manager.pause()
        self.logger.info("Game paused")
    
    def resume(self) -> None:
        """Resume the game"""
        self.time_manager.resume()
        self.last_frame_time = time.time()
        self.logger.info("Game resumed")
    
    def shutdown(self) -> None:
        """Shutdown the game engine"""
        self.logger.info("Shutting down game engine")
        
        self.running = False
        
        # Cleanup systems
        self.state_manager.cleanup()
        self.event_manager.clear_queue()
        
        # Save configuration
        self.config.save_config()
        
        # Close logger
        self.logger.flush()
        
        self.logger.info("Game engine shutdown complete")
    
    def get_system(self, system_name: str) -> Any:
        """Get a reference to a game system"""
        systems = {
            'event_manager': self.event_manager,
            'state_manager': self.state_manager,
            'time_manager': self.time_manager,
            'config': self.config,
            'logger': self.logger
        }
        return systems.get(system_name)
    
    def get_screen(self) -> pygame.Surface:
        """Get the main screen surface"""
        return self.screen
    
    def get_fps(self) -> float:
        """Get current FPS"""
        return self.current_fps
    
    def get_delta_time(self) -> float:
        """Get current frame delta time"""
        return self.delta_time