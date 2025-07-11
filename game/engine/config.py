"""
Configuration System for Chronicles of Aethermoor
Manages game settings, display options, and gameplay parameters
"""

import json
import os
from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class DisplayConfig:
    """Display and graphics configuration"""
    width: int = 1280
    height: int = 720
    fullscreen: bool = False
    vsync: bool = True
    fps_limit: int = 60
    ui_scale: float = 1.0


@dataclass
class AudioConfig:
    """Audio configuration"""
    master_volume: float = 1.0
    sfx_volume: float = 0.8
    music_volume: float = 0.6
    voice_volume: float = 0.9


@dataclass
class GameplayConfig:
    """Gameplay configuration"""
    difficulty: str = "normal"  # easy, normal, hard, expert
    auto_save_interval: int = 300  # seconds
    combat_speed: float = 1.0
    dialogue_speed: float = 1.0
    show_damage_numbers: bool = True
    show_tutorial_hints: bool = True


@dataclass
class ControlsConfig:
    """Input controls configuration"""
    move_up: str = "w"
    move_down: str = "s"
    move_left: str = "a"
    move_right: str = "d"
    interact: str = "e"
    inventory: str = "i"
    character: str = "c"
    quest_log: str = "q"
    map: str = "m"
    pause: str = "escape"
    quick_save: str = "f5"
    quick_load: str = "f9"


class Config:
    """Main configuration manager"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.display = DisplayConfig()
        self.audio = AudioConfig()
        self.gameplay = GameplayConfig()
        self.controls = ControlsConfig()
        
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                # Update configurations with loaded data
                if 'display' in data:
                    for key, value in data['display'].items():
                        if hasattr(self.display, key):
                            setattr(self.display, key, value)
                
                if 'audio' in data:
                    for key, value in data['audio'].items():
                        if hasattr(self.audio, key):
                            setattr(self.audio, key, value)
                
                if 'gameplay' in data:
                    for key, value in data['gameplay'].items():
                        if hasattr(self.gameplay, key):
                            setattr(self.gameplay, key, value)
                
                if 'controls' in data:
                    for key, value in data['controls'].items():
                        if hasattr(self.controls, key):
                            setattr(self.controls, key, value)
                            
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using defaults.")
    
    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            config_data = {
                'display': asdict(self.display),
                'audio': asdict(self.audio),
                'gameplay': asdict(self.gameplay),
                'controls': asdict(self.controls)
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
                
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get_resolution(self) -> tuple[int, int]:
        """Get display resolution as tuple"""
        return (self.display.width, self.display.height)
    
    def set_resolution(self, width: int, height: int) -> None:
        """Set display resolution"""
        self.display.width = width
        self.display.height = height
    
    def get_key_binding(self, action: str) -> str:
        """Get key binding for an action"""
        return getattr(self.controls, action, None)
    
    def set_key_binding(self, action: str, key: str) -> None:
        """Set key binding for an action"""
        if hasattr(self.controls, action):
            setattr(self.controls, action, key)