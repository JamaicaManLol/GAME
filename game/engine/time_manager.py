"""
Time Management System for Chronicles of Aethermoor
Manages game time, day/night cycles, and temporal events
"""

import time
from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass
from .event_manager import EventManager, EventType, emit_event
from .logger import get_logger


class TimeOfDay(Enum):
    """Time of day enumeration"""
    DAWN = "dawn"
    MORNING = "morning"
    MIDDAY = "midday"
    AFTERNOON = "afternoon"
    DUSK = "dusk"
    EVENING = "evening"
    NIGHT = "night"
    MIDNIGHT = "midnight"


class Season(Enum):
    """Season enumeration"""
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


class WeatherType(Enum):
    """Weather types"""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    STORM = "storm"
    FOG = "fog"
    SNOW = "snow"
    CRYSTAL_STORM = "crystal_storm"  # Magical weather specific to Aethermoor


@dataclass
class GameTime:
    """Represents a point in game time"""
    year: int = 1
    month: int = 1  # 1-12
    day: int = 1    # 1-30
    hour: int = 6   # 0-23 (start at dawn)
    minute: int = 0 # 0-59
    
    def total_minutes(self) -> int:
        """Get total minutes since game start"""
        return (
            (self.year - 1) * 365 * 24 * 60 +
            (self.month - 1) * 30 * 24 * 60 +
            (self.day - 1) * 24 * 60 +
            self.hour * 60 +
            self.minute
        )
    
    def get_time_of_day(self) -> TimeOfDay:
        """Get the current time of day"""
        if 5 <= self.hour < 7:
            return TimeOfDay.DAWN
        elif 7 <= self.hour < 10:
            return TimeOfDay.MORNING
        elif 10 <= self.hour < 14:
            return TimeOfDay.MIDDAY
        elif 14 <= self.hour < 17:
            return TimeOfDay.AFTERNOON
        elif 17 <= self.hour < 19:
            return TimeOfDay.DUSK
        elif 19 <= self.hour < 22:
            return TimeOfDay.EVENING
        elif 22 <= self.hour < 24 or 0 <= self.hour < 2:
            return TimeOfDay.NIGHT
        else:  # 2 <= hour < 5
            return TimeOfDay.MIDNIGHT
    
    def get_season(self) -> Season:
        """Get the current season"""
        if 3 <= self.month <= 5:
            return Season.SPRING
        elif 6 <= self.month <= 8:
            return Season.SUMMER
        elif 9 <= self.month <= 11:
            return Season.AUTUMN
        else:  # 12, 1, 2
            return Season.WINTER
    
    def is_daytime(self) -> bool:
        """Check if it's daytime"""
        return self.get_time_of_day() in [
            TimeOfDay.DAWN, TimeOfDay.MORNING, 
            TimeOfDay.MIDDAY, TimeOfDay.AFTERNOON
        ]
    
    def is_nighttime(self) -> bool:
        """Check if it's nighttime"""
        return not self.is_daytime()
    
    def copy(self) -> 'GameTime':
        """Create a copy of this time"""
        return GameTime(self.year, self.month, self.day, self.hour, self.minute)
    
    def __str__(self) -> str:
        """String representation of time"""
        time_str = f"{self.hour:02d}:{self.minute:02d}"
        date_str = f"Day {self.day}, Month {self.month}, Year {self.year}"
        return f"{time_str} - {date_str}"


@dataclass
class WeatherCondition:
    """Current weather conditions"""
    weather_type: WeatherType = WeatherType.CLEAR
    intensity: float = 0.0  # 0.0 to 1.0
    visibility: float = 1.0  # 0.0 to 1.0
    temperature: float = 20.0  # Celsius
    wind_speed: float = 0.0  # 0.0 to 100.0 km/h
    duration_remaining: int = 0  # minutes


class TemporalEvent:
    """An event that occurs at a specific time"""
    
    def __init__(self, event_time: GameTime, callback: Callable[[], None],
                 name: str = "Unnamed Event", repeating: bool = False,
                 repeat_interval: int = 0):
        self.event_time = event_time
        self.callback = callback
        self.name = name
        self.repeating = repeating
        self.repeat_interval = repeat_interval  # minutes
        self.next_execution = event_time.total_minutes()
    
    def should_execute(self, current_time: GameTime) -> bool:
        """Check if this event should execute"""
        current_minutes = current_time.total_minutes()
        return current_minutes >= self.next_execution
    
    def execute(self, current_time: GameTime) -> None:
        """Execute the event"""
        try:
            self.callback()
            if self.repeating and self.repeat_interval > 0:
                self.next_execution = current_time.total_minutes() + self.repeat_interval
            else:
                self.next_execution = float('inf')  # Don't execute again
        except Exception as e:
            print(f"Error executing temporal event '{self.name}': {e}")


class TimeManager:
    """Manages game time, day/night cycles, and temporal events"""
    
    def __init__(self, time_scale: float = 60.0):
        """
        Initialize time manager
        
        Args:
            time_scale: How many game minutes pass per real second (default: 60 = 1 hour per minute)
        """
        self.logger = get_logger()
        self.event_manager = EventManager()
        
        # Time settings
        self.time_scale = time_scale  # Game minutes per real second
        self.paused = False
        self.last_real_time = time.time()
        
        # Game time
        self.current_time = GameTime()
        self.last_time_of_day = self.current_time.get_time_of_day()
        self.last_season = self.current_time.get_season()
        
        # Weather system
        self.current_weather = WeatherCondition()
        self.weather_change_probability = 0.001  # Per minute
        self.weather_patterns: Dict[Season, List[WeatherType]] = {
            Season.SPRING: [WeatherType.CLEAR, WeatherType.RAIN, WeatherType.CLOUDY],
            Season.SUMMER: [WeatherType.CLEAR, WeatherType.STORM, WeatherType.CLOUDY],
            Season.AUTUMN: [WeatherType.CLOUDY, WeatherType.RAIN, WeatherType.FOG],
            Season.WINTER: [WeatherType.SNOW, WeatherType.CLOUDY, WeatherType.CLEAR]
        }
        
        # Temporal events
        self.temporal_events: List[TemporalEvent] = []
        self.completed_events: List[TemporalEvent] = []
        
        # Performance tracking
        self.accumulated_time = 0.0
        
        self.logger.info("Time Manager initialized")
    
    def update(self, delta_time: float) -> None:
        """Update the time system"""
        if self.paused:
            return
        
        # Calculate time progression
        game_minutes = delta_time * self.time_scale
        self.accumulated_time += game_minutes
        
        # Only advance time in discrete minute steps
        minutes_to_advance = int(self.accumulated_time)
        if minutes_to_advance > 0:
            self.accumulated_time -= minutes_to_advance
            self._advance_time(minutes_to_advance)
    
    def _advance_time(self, minutes: int) -> None:
        """Advance game time by the specified number of minutes"""
        old_time = self.current_time.copy()
        
        # Advance minutes
        self.current_time.minute += minutes
        
        # Handle minute overflow
        while self.current_time.minute >= 60:
            self.current_time.minute -= 60
            self.current_time.hour += 1
            
            # Handle hour overflow
            if self.current_time.hour >= 24:
                self.current_time.hour = 0
                self.current_time.day += 1
                
                # Handle day overflow
                if self.current_time.day > 30:
                    self.current_time.day = 1
                    self.current_time.month += 1
                    
                    # Handle month overflow
                    if self.current_time.month > 12:
                        self.current_time.month = 1
                        self.current_time.year += 1
        
        # Check for time of day changes
        current_time_of_day = self.current_time.get_time_of_day()
        if current_time_of_day != self.last_time_of_day:
            self._on_time_of_day_changed(self.last_time_of_day, current_time_of_day)
            self.last_time_of_day = current_time_of_day
        
        # Check for season changes
        current_season = self.current_time.get_season()
        if current_season != self.last_season:
            self._on_season_changed(self.last_season, current_season)
            self.last_season = current_season
        
        # Update weather
        self._update_weather(minutes)
        
        # Process temporal events
        self._process_temporal_events()
        
        # Emit time advancement event
        emit_event(EventType.DAY_NIGHT_CHANGED, {
            'old_time': old_time,
            'new_time': self.current_time.copy(),
            'time_of_day': current_time_of_day.value,
            'season': current_season.value
        })
    
    def _on_time_of_day_changed(self, old_time: TimeOfDay, new_time: TimeOfDay) -> None:
        """Handle time of day transitions"""
        self.logger.log_world_event(
            "TIME_CHANGE", 
            "Global", 
            f"Time changed from {old_time.value} to {new_time.value}"
        )
        
        # Emit specific events for important transitions
        if new_time == TimeOfDay.DAWN:
            emit_event(EventType.DAY_NIGHT_CHANGED, {'transition': 'sunrise'})
        elif new_time == TimeOfDay.DUSK:
            emit_event(EventType.DAY_NIGHT_CHANGED, {'transition': 'sunset'})
        elif new_time == TimeOfDay.MIDNIGHT:
            emit_event(EventType.DAY_NIGHT_CHANGED, {'transition': 'midnight'})
    
    def _on_season_changed(self, old_season: Season, new_season: Season) -> None:
        """Handle season transitions"""
        self.logger.log_world_event(
            "SEASON_CHANGE",
            "Global",
            f"Season changed from {old_season.value} to {new_season.value}"
        )
        
        emit_event(EventType.WEATHER_CHANGED, {
            'type': 'season_change',
            'old_season': old_season.value,
            'new_season': new_season.value
        })
    
    def _update_weather(self, minutes_passed: int) -> None:
        """Update weather conditions"""
        # Reduce remaining duration
        if self.current_weather.duration_remaining > 0:
            self.current_weather.duration_remaining -= minutes_passed
        
        # Check for weather change
        change_chance = self.weather_change_probability * minutes_passed
        if (self.current_weather.duration_remaining <= 0 or 
            change_chance > 0.01):  # Force change after duration or random chance
            
            self._change_weather()
    
    def _change_weather(self) -> None:
        """Change to new weather conditions"""
        import random
        
        old_weather = self.current_weather.weather_type
        current_season = self.current_time.get_season()
        
        # Get possible weather for current season
        possible_weather = self.weather_patterns.get(current_season, [WeatherType.CLEAR])
        
        # Choose new weather (avoid staying the same unless only option)
        if len(possible_weather) > 1:
            possible_weather = [w for w in possible_weather if w != old_weather]
        
        new_weather = random.choice(possible_weather)
        
        # Set new weather properties
        self.current_weather.weather_type = new_weather
        self.current_weather.intensity = random.uniform(0.3, 1.0)
        self.current_weather.duration_remaining = random.randint(30, 240)  # 30 minutes to 4 hours
        
        # Adjust properties based on weather type
        if new_weather == WeatherType.CLEAR:
            self.current_weather.visibility = 1.0
            self.current_weather.wind_speed = random.uniform(0, 10)
        elif new_weather == WeatherType.RAIN:
            self.current_weather.visibility = random.uniform(0.6, 0.9)
            self.current_weather.wind_speed = random.uniform(10, 30)
        elif new_weather == WeatherType.STORM:
            self.current_weather.visibility = random.uniform(0.3, 0.6)
            self.current_weather.wind_speed = random.uniform(40, 80)
        elif new_weather == WeatherType.FOG:
            self.current_weather.visibility = random.uniform(0.2, 0.5)
            self.current_weather.wind_speed = random.uniform(0, 5)
        elif new_weather == WeatherType.CRYSTAL_STORM:
            self.current_weather.visibility = random.uniform(0.4, 0.7)
            self.current_weather.wind_speed = random.uniform(20, 60)
            self.current_weather.intensity = random.uniform(0.7, 1.0)
        
        self.logger.log_world_event(
            "WEATHER_CHANGE",
            "Global",
            f"Weather changed from {old_weather.value} to {new_weather.value}"
        )
        
        emit_event(EventType.WEATHER_CHANGED, {
            'old_weather': old_weather.value,
            'new_weather': new_weather.value,
            'intensity': self.current_weather.intensity,
            'visibility': self.current_weather.visibility
        })
    
    def _process_temporal_events(self) -> None:
        """Process scheduled temporal events"""
        events_to_remove = []
        
        for event in self.temporal_events:
            if event.should_execute(self.current_time):
                event.execute(self.current_time)
                
                # Remove non-repeating events or completed repeating events
                if not event.repeating or event.next_execution == float('inf'):
                    events_to_remove.append(event)
                    self.completed_events.append(event)
        
        # Remove completed events
        for event in events_to_remove:
            self.temporal_events.remove(event)
    
    def schedule_event(self, event_time: GameTime, callback: Callable[[], None],
                      name: str = "Unnamed Event", repeating: bool = False,
                      repeat_interval: int = 0) -> TemporalEvent:
        """Schedule a new temporal event"""
        event = TemporalEvent(event_time, callback, name, repeating, repeat_interval)
        self.temporal_events.append(event)
        
        self.logger.debug(f"Scheduled temporal event: {name} at {event_time}")
        return event
    
    def schedule_relative_event(self, minutes_from_now: int, callback: Callable[[], None],
                               name: str = "Unnamed Event", repeating: bool = False,
                               repeat_interval: int = 0) -> TemporalEvent:
        """Schedule an event relative to current time"""
        target_time = self.current_time.copy()
        target_time.minute += minutes_from_now
        
        # Handle overflow
        while target_time.minute >= 60:
            target_time.minute -= 60
            target_time.hour += 1
            if target_time.hour >= 24:
                target_time.hour = 0
                target_time.day += 1
                if target_time.day > 30:
                    target_time.day = 1
                    target_time.month += 1
                    if target_time.month > 12:
                        target_time.month = 1
                        target_time.year += 1
        
        return self.schedule_event(target_time, callback, name, repeating, repeat_interval)
    
    def cancel_event(self, event: TemporalEvent) -> bool:
        """Cancel a scheduled event"""
        if event in self.temporal_events:
            self.temporal_events.remove(event)
            self.logger.debug(f"Cancelled temporal event: {event.name}")
            return True
        return False
    
    def pause(self) -> None:
        """Pause time progression"""
        self.paused = True
        self.logger.info("Time paused")
    
    def resume(self) -> None:
        """Resume time progression"""
        self.paused = False
        self.last_real_time = time.time()
        self.logger.info("Time resumed")
    
    def set_time_scale(self, scale: float) -> None:
        """Set the time scale (game minutes per real second)"""
        self.time_scale = max(0.1, min(3600.0, scale))  # Clamp between 0.1 and 3600
        self.logger.info(f"Time scale set to {self.time_scale}")
    
    def set_time(self, game_time: GameTime) -> None:
        """Set the current game time"""
        old_time = self.current_time.copy()
        self.current_time = game_time.copy()
        
        self.logger.info(f"Time set to {self.current_time}")
        emit_event(EventType.DAY_NIGHT_CHANGED, {
            'old_time': old_time,
            'new_time': self.current_time.copy(),
            'time_of_day': self.current_time.get_time_of_day().value,
            'season': self.current_time.get_season().value
        })
    
    def get_time(self) -> GameTime:
        """Get the current game time"""
        return self.current_time.copy()
    
    def get_weather(self) -> WeatherCondition:
        """Get current weather conditions"""
        return self.current_weather
    
    def force_weather_change(self, weather_type: WeatherType, 
                            duration: int = 60, intensity: float = 0.5) -> None:
        """Force a specific weather condition"""
        old_weather = self.current_weather.weather_type
        self.current_weather.weather_type = weather_type
        self.current_weather.intensity = intensity
        self.current_weather.duration_remaining = duration
        
        self.logger.info(f"Weather forced to {weather_type.value}")
        emit_event(EventType.WEATHER_CHANGED, {
            'old_weather': old_weather.value,
            'new_weather': weather_type.value,
            'intensity': intensity,
            'forced': True
        })
    
    def get_light_level(self) -> float:
        """Get current light level (0.0 = pitch black, 1.0 = full daylight)"""
        time_of_day = self.current_time.get_time_of_day()
        
        # Base light levels by time of day
        base_light = {
            TimeOfDay.MIDNIGHT: 0.1,
            TimeOfDay.DAWN: 0.4,
            TimeOfDay.MORNING: 0.8,
            TimeOfDay.MIDDAY: 1.0,
            TimeOfDay.AFTERNOON: 0.9,
            TimeOfDay.DUSK: 0.5,
            TimeOfDay.EVENING: 0.3,
            TimeOfDay.NIGHT: 0.2
        }.get(time_of_day, 0.5)
        
        # Weather modifications
        weather_modifier = {
            WeatherType.CLEAR: 1.0,
            WeatherType.CLOUDY: 0.8,
            WeatherType.RAIN: 0.7,
            WeatherType.STORM: 0.4,
            WeatherType.FOG: 0.5,
            WeatherType.SNOW: 0.6,
            WeatherType.CRYSTAL_STORM: 0.6
        }.get(self.current_weather.weather_type, 1.0)
        
        return max(0.05, base_light * weather_modifier)  # Minimum light level
    
    def get_ambient_color(self) -> tuple[int, int, int]:
        """Get ambient color based on time and weather"""
        time_of_day = self.current_time.get_time_of_day()
        
        # Base colors by time of day
        colors = {
            TimeOfDay.MIDNIGHT: (20, 20, 40),
            TimeOfDay.DAWN: (255, 180, 100),
            TimeOfDay.MORNING: (255, 255, 200),
            TimeOfDay.MIDDAY: (255, 255, 255),
            TimeOfDay.AFTERNOON: (255, 240, 200),
            TimeOfDay.DUSK: (255, 150, 80),
            TimeOfDay.EVENING: (100, 100, 150),
            TimeOfDay.NIGHT: (40, 40, 80)
        }
        
        base_color = colors.get(time_of_day, (255, 255, 255))
        
        # Weather modifications
        if self.current_weather.weather_type == WeatherType.STORM:
            # Darker, more blue
            return (
                int(base_color[0] * 0.7),
                int(base_color[1] * 0.7),
                int(base_color[2] * 0.9)
            )
        elif self.current_weather.weather_type == WeatherType.CRYSTAL_STORM:
            # Purple tint
            return (
                int(base_color[0] * 0.8 + 50),
                int(base_color[1] * 0.7),
                int(base_color[2] * 0.9 + 50)
            )
        
        return base_color