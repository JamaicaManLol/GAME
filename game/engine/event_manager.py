"""
Event Management System for Chronicles of Aethermoor
Implements observer pattern for game event handling
"""

from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict
import weakref
import time


class EventType(Enum):
    """Enumeration of all possible game events"""
    # Player events
    PLAYER_LEVEL_UP = "player_level_up"
    PLAYER_DIED = "player_died"
    PLAYER_MOVED = "player_moved"
    PLAYER_HEALTH_CHANGED = "player_health_changed"
    PLAYER_MANA_CHANGED = "player_mana_changed"
    
    # Combat events
    COMBAT_STARTED = "combat_started"
    COMBAT_ENDED = "combat_ended"
    ATTACK_PERFORMED = "attack_performed"
    DAMAGE_DEALT = "damage_dealt"
    SKILL_USED = "skill_used"
    STATUS_EFFECT_APPLIED = "status_effect_applied"
    STATUS_EFFECT_REMOVED = "status_effect_removed"
    
    # Quest events
    QUEST_STARTED = "quest_started"
    QUEST_COMPLETED = "quest_completed"
    QUEST_FAILED = "quest_failed"
    QUEST_OBJECTIVE_UPDATED = "quest_objective_updated"
    
    # World events
    DAY_NIGHT_CHANGED = "day_night_changed"
    WEATHER_CHANGED = "weather_changed"
    LOCATION_ENTERED = "location_entered"
    LOCATION_EXITED = "location_exited"
    NPC_INTERACTION = "npc_interaction"
    
    # Inventory events
    ITEM_ACQUIRED = "item_acquired"
    ITEM_USED = "item_used"
    ITEM_EQUIPPED = "item_equipped"
    ITEM_UNEQUIPPED = "item_unequipped"
    ITEM_SOLD = "item_sold"
    ITEM_CRAFTED = "item_crafted"
    
    # UI events
    MENU_OPENED = "menu_opened"
    MENU_CLOSED = "menu_closed"
    DIALOGUE_STARTED = "dialogue_started"
    DIALOGUE_ENDED = "dialogue_ended"
    
    # System events
    GAME_PAUSED = "game_paused"
    GAME_RESUMED = "game_resumed"
    SAVE_GAME = "save_game"
    LOAD_GAME = "load_game"
    SETTINGS_CHANGED = "settings_changed"


@dataclass
class GameEvent:
    """Represents a game event with associated data"""
    event_type: EventType
    data: Dict[str, Any]
    timestamp: float
    source: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()


class EventListener:
    """Base class for event listeners"""
    
    def __init__(self, priority: int = 0):
        self.priority = priority
        self.enabled = True
    
    def handle_event(self, event: GameEvent) -> bool:
        """
        Handle an event. Return True if event should be consumed (not passed to other listeners)
        """
        return False
    
    def get_listened_events(self) -> List[EventType]:
        """Return list of events this listener cares about"""
        return []


class EventManager:
    """Central event management system"""
    
    _instance: Optional['EventManager'] = None
    
    def __new__(cls) -> 'EventManager':
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._listeners: Dict[EventType, List[weakref.ref]] = defaultdict(list)
        self._global_listeners: List[weakref.ref] = []
        self._event_queue: List[GameEvent] = []
        self._processing = False
        self._event_history: List[GameEvent] = []
        self._max_history = 1000  # Keep last 1000 events
        self._initialized = True
    
    def subscribe(self, event_type: EventType, listener: EventListener) -> None:
        """Subscribe a listener to a specific event type"""
        listener_ref = weakref.ref(listener, self._cleanup_listener)
        self._listeners[event_type].append(listener_ref)
        
        # Sort by priority (higher priority first)
        self._listeners[event_type].sort(
            key=lambda ref: ref().priority if ref() else -999, 
            reverse=True
        )
    
    def subscribe_global(self, listener: EventListener) -> None:
        """Subscribe a listener to all events"""
        listener_ref = weakref.ref(listener, self._cleanup_global_listener)
        self._global_listeners.append(listener_ref)
        
        # Sort by priority
        self._global_listeners.sort(
            key=lambda ref: ref().priority if ref() else -999,
            reverse=True
        )
    
    def unsubscribe(self, event_type: EventType, listener: EventListener) -> None:
        """Unsubscribe a listener from a specific event type"""
        self._listeners[event_type] = [
            ref for ref in self._listeners[event_type] 
            if ref() is not None and ref() is not listener
        ]
    
    def unsubscribe_global(self, listener: EventListener) -> None:
        """Unsubscribe a listener from all events"""
        self._global_listeners = [
            ref for ref in self._global_listeners
            if ref() is not None and ref() is not listener
        ]
    
    def emit(self, event_type: EventType, data: Dict[str, Any] = None, 
             source: str = None, immediate: bool = False) -> None:
        """Emit an event"""
        if data is None:
            data = {}
            
        event = GameEvent(
            event_type=event_type,
            data=data,
            timestamp=time.time(),
            source=source
        )
        
        if immediate:
            self._process_event(event)
        else:
            self._event_queue.append(event)
    
    def emit_immediate(self, event_type: EventType, data: Dict[str, Any] = None,
                      source: str = None) -> None:
        """Emit an event and process it immediately"""
        self.emit(event_type, data, source, immediate=True)
    
    def process_events(self) -> None:
        """Process all queued events"""
        if self._processing:
            return  # Prevent recursive processing
        
        self._processing = True
        
        try:
            while self._event_queue:
                event = self._event_queue.pop(0)
                self._process_event(event)
        finally:
            self._processing = False
    
    def _process_event(self, event: GameEvent) -> None:
        """Process a single event"""
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        consumed = False
        
        # Process global listeners first
        for listener_ref in self._global_listeners[:]:  # Copy to avoid modification during iteration
            listener = listener_ref()
            if listener is None:
                continue
                
            if listener.enabled:
                try:
                    if listener.handle_event(event):
                        consumed = True
                        break
                except Exception as e:
                    print(f"Error in global event listener: {e}")
        
        # Process specific event listeners if not consumed
        if not consumed and event.event_type in self._listeners:
            for listener_ref in self._listeners[event.event_type][:]:
                listener = listener_ref()
                if listener is None:
                    continue
                    
                if listener.enabled:
                    try:
                        if listener.handle_event(event):
                            consumed = True
                            break
                    except Exception as e:
                        print(f"Error in event listener for {event.event_type}: {e}")
    
    def _cleanup_listener(self, ref) -> None:
        """Clean up dead listener references"""
        for event_type, listeners in self._listeners.items():
            self._listeners[event_type] = [l for l in listeners if l is not ref]
    
    def _cleanup_global_listener(self, ref) -> None:
        """Clean up dead global listener references"""
        self._global_listeners = [l for l in self._global_listeners if l is not ref]
    
    def clear_queue(self) -> None:
        """Clear all queued events"""
        self._event_queue.clear()
    
    def get_event_history(self, event_type: Optional[EventType] = None, 
                         limit: int = 100) -> List[GameEvent]:
        """Get recent event history"""
        if event_type is None:
            return self._event_history[-limit:]
        else:
            filtered = [e for e in self._event_history if e.event_type == event_type]
            return filtered[-limit:]
    
    def get_listener_count(self, event_type: EventType) -> int:
        """Get number of listeners for an event type"""
        return len([ref for ref in self._listeners[event_type] if ref() is not None])
    
    def get_global_listener_count(self) -> int:
        """Get number of global listeners"""
        return len([ref for ref in self._global_listeners if ref() is not None])


# Convenience functions
def get_event_manager() -> EventManager:
    """Get the singleton event manager instance"""
    return EventManager()


def emit_event(event_type: EventType, data: Dict[str, Any] = None, 
               source: str = None) -> None:
    """Convenience function to emit an event"""
    get_event_manager().emit(event_type, data, source)


def subscribe_to_event(event_type: EventType, callback: Callable[[GameEvent], bool],
                      priority: int = 0) -> EventListener:
    """Convenience function to subscribe to an event with a callback"""
    class CallbackListener(EventListener):
        def __init__(self, cb, prio):
            super().__init__(prio)
            self.callback = cb
        
        def handle_event(self, event: GameEvent) -> bool:
            return self.callback(event)
    
    listener = CallbackListener(callback, priority)
    get_event_manager().subscribe(event_type, listener)
    return listener