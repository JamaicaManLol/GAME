"""
State Management System for Chronicles of Aethermoor
Manages game states and transitions between them
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Any
from enum import Enum
import pygame
from .event_manager import EventManager, EventType, emit_event
from .logger import get_logger


class StateType(Enum):
    """Enumeration of all possible game states"""
    SPLASH_SCREEN = "splash_screen"
    MAIN_MENU = "main_menu"
    CHARACTER_CREATION = "character_creation"
    LOADING = "loading"
    GAMEPLAY = "gameplay"
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    INVENTORY = "inventory"
    CHARACTER_SHEET = "character_sheet"
    QUEST_LOG = "quest_log"
    WORLD_MAP = "world_map"
    SHOP = "shop"
    CRAFTING = "crafting"
    SETTINGS = "settings"
    PAUSE_MENU = "pause_menu"
    SAVE_LOAD = "save_load"
    GAME_OVER = "game_over"
    CREDITS = "credits"


class GameState(ABC):
    """Abstract base class for all game states"""
    
    def __init__(self, state_type: StateType, state_manager: 'StateManager'):
        self.state_type = state_type
        self.state_manager = state_manager
        self.logger = get_logger()
        self.event_manager = EventManager()
        self.active = False
        self.initialized = False
        
        # State-specific data
        self.data: Dict[str, Any] = {}
        
        # Transition flags
        self.can_pause = True
        self.blocks_input = False
        self.overlay = False  # If True, state is rendered over previous state
    
    @abstractmethod
    def enter(self, previous_state: Optional['GameState'] = None, 
              data: Dict[str, Any] = None) -> None:
        """Called when entering this state"""
        self.active = True
        if data:
            self.data.update(data)
        self.logger.info(f"Entered state: {self.state_type.value}")
    
    @abstractmethod
    def exit(self, next_state: Optional['GameState'] = None) -> None:
        """Called when exiting this state"""
        self.active = False
        self.logger.info(f"Exited state: {self.state_type.value}")
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update state logic"""
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """Render state to screen"""
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events. Return True if event was consumed.
        """
        return False
    
    def initialize(self) -> None:
        """Initialize state (called once)"""
        if not self.initialized:
            self.on_initialize()
            self.initialized = True
    
    def on_initialize(self) -> None:
        """Override this for state-specific initialization"""
        pass
    
    def cleanup(self) -> None:
        """Cleanup state resources"""
        pass
    
    def pause(self) -> None:
        """Pause the state"""
        pass
    
    def resume(self) -> None:
        """Resume the state"""
        pass


class StateManager:
    """Manages game states and transitions"""
    
    def __init__(self):
        self.logger = get_logger()
        self.event_manager = EventManager()
        
        # State management
        self.states: Dict[StateType, GameState] = {}
        self.state_stack: List[GameState] = []
        self.current_state: Optional[GameState] = None
        
        # Transition management
        self._pending_transition: Optional[Dict[str, Any]] = None
        self._transition_data: Dict[str, Any] = {}
        
        # State history for navigation
        self.state_history: List[StateType] = []
        self.max_history = 50
    
    def register_state(self, state: GameState) -> None:
        """Register a new state"""
        self.states[state.state_type] = state
        state.initialize()
        self.logger.debug(f"Registered state: {state.state_type.value}")
    
    def unregister_state(self, state_type: StateType) -> None:
        """Unregister a state"""
        if state_type in self.states:
            state = self.states[state_type]
            if state.active:
                self.logger.warning(f"Unregistering active state: {state_type.value}")
            
            state.cleanup()
            del self.states[state_type]
            self.logger.debug(f"Unregistered state: {state_type.value}")
    
    def change_state(self, state_type: StateType, data: Dict[str, Any] = None,
                    immediate: bool = False) -> bool:
        """Change to a new state"""
        if state_type not in self.states:
            self.logger.error(f"State not found: {state_type.value}")
            return False
        
        if immediate:
            self._perform_state_change(state_type, data)
        else:
            self._pending_transition = {
                'type': 'change',
                'target': state_type,
                'data': data or {}
            }
        
        return True
    
    def push_state(self, state_type: StateType, data: Dict[str, Any] = None,
                  immediate: bool = False) -> bool:
        """Push a new state onto the stack"""
        if state_type not in self.states:
            self.logger.error(f"State not found: {state_type.value}")
            return False
        
        if immediate:
            self._perform_state_push(state_type, data)
        else:
            self._pending_transition = {
                'type': 'push',
                'target': state_type,
                'data': data or {}
            }
        
        return True
    
    def pop_state(self, immediate: bool = False) -> bool:
        """Pop the current state from the stack"""
        if len(self.state_stack) <= 1:
            self.logger.warning("Cannot pop state - only one state on stack")
            return False
        
        if immediate:
            self._perform_state_pop()
        else:
            self._pending_transition = {
                'type': 'pop',
                'target': None,
                'data': {}
            }
        
        return True
    
    def back_to_state(self, state_type: StateType, data: Dict[str, Any] = None) -> bool:
        """Go back to a specific state in the stack"""
        # Find the state in the stack
        target_index = -1
        for i, state in enumerate(self.state_stack):
            if state.state_type == state_type:
                target_index = i
                break
        
        if target_index == -1:
            self.logger.warning(f"State {state_type.value} not found in stack")
            return False
        
        # Pop states until we reach the target
        while len(self.state_stack) > target_index + 1:
            self.pop_state(immediate=True)
        
        # Update the target state with new data if provided
        if data and self.current_state:
            self.current_state.data.update(data)
        
        return True
    
    def clear_stack(self, new_state: StateType, data: Dict[str, Any] = None) -> bool:
        """Clear the entire stack and set a new base state"""
        if new_state not in self.states:
            self.logger.error(f"State not found: {new_state.value}")
            return False
        
        # Exit all current states
        while self.state_stack:
            state = self.state_stack.pop()
            state.exit()
        
        # Set new base state
        return self.change_state(new_state, data, immediate=True)
    
    def update(self, delta_time: float) -> None:
        """Update the current state"""
        # Process pending transitions
        if self._pending_transition:
            transition = self._pending_transition
            self._pending_transition = None
            
            if transition['type'] == 'change':
                self._perform_state_change(transition['target'], transition['data'])
            elif transition['type'] == 'push':
                self._perform_state_push(transition['target'], transition['data'])
            elif transition['type'] == 'pop':
                self._perform_state_pop()
        
        # Update current state
        if self.current_state and self.current_state.active:
            self.current_state.update(delta_time)
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the current state(s)"""
        if not self.state_stack:
            return
        
        # Find the bottom-most non-overlay state
        start_index = len(self.state_stack) - 1
        for i in range(len(self.state_stack) - 1, -1, -1):
            if not self.state_stack[i].overlay:
                start_index = i
                break
        
        # Render states from bottom to top
        for i in range(start_index, len(self.state_stack)):
            state = self.state_stack[i]
            if state.active:
                state.render(screen)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events"""
        # Process events from top of stack downward
        for state in reversed(self.state_stack):
            if state.active and not state.blocks_input:
                if state.handle_event(event):
                    return True  # Event was consumed
        return False
    
    def _perform_state_change(self, state_type: StateType, data: Dict[str, Any]) -> None:
        """Perform an immediate state change"""
        new_state = self.states[state_type]
        
        # Exit current state
        if self.current_state:
            self.current_state.exit(new_state)
        
        # Clear stack and set new state
        self.state_stack.clear()
        self.state_stack.append(new_state)
        self.current_state = new_state
        
        # Enter new state
        new_state.enter(data=data)
        
        # Update history
        self._add_to_history(state_type)
        
        self.logger.info(f"Changed to state: {state_type.value}")
    
    def _perform_state_push(self, state_type: StateType, data: Dict[str, Any]) -> None:
        """Perform an immediate state push"""
        new_state = self.states[state_type]
        previous_state = self.current_state
        
        # Pause current state if it can be paused
        if self.current_state and self.current_state.can_pause:
            self.current_state.pause()
        
        # Push new state
        self.state_stack.append(new_state)
        self.current_state = new_state
        
        # Enter new state
        new_state.enter(previous_state, data)
        
        # Update history
        self._add_to_history(state_type)
        
        self.logger.info(f"Pushed state: {state_type.value}")
    
    def _perform_state_pop(self) -> None:
        """Perform an immediate state pop"""
        if len(self.state_stack) <= 1:
            return
        
        # Exit current state
        current_state = self.state_stack.pop()
        current_state.exit()
        
        # Resume previous state
        self.current_state = self.state_stack[-1] if self.state_stack else None
        if self.current_state:
            self.current_state.resume()
        
        self.logger.info(f"Popped state: {current_state.state_type.value}")
    
    def _add_to_history(self, state_type: StateType) -> None:
        """Add state to history"""
        self.state_history.append(state_type)
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)
    
    def get_current_state(self) -> Optional[GameState]:
        """Get the current active state"""
        return self.current_state
    
    def get_state_stack(self) -> List[GameState]:
        """Get the current state stack"""
        return self.state_stack.copy()
    
    def is_state_active(self, state_type: StateType) -> bool:
        """Check if a specific state is currently active"""
        return any(state.state_type == state_type and state.active 
                  for state in self.state_stack)
    
    def get_state_history(self) -> List[StateType]:
        """Get the state transition history"""
        return self.state_history.copy()
    
    def cleanup(self) -> None:
        """Cleanup all states"""
        for state in self.states.values():
            state.cleanup()
        self.states.clear()
        self.state_stack.clear()
        self.current_state = None