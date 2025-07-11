# Chronicles of Aethermoor - RPG Game Design Document

## Overview
A complex fantasy RPG set in the world of Aethermoor, featuring deep character progression, branching narratives, and intricate world systems.

## World & Lore
**Setting**: The floating continent of Aethermoor, suspended by ancient magical crystals
**Timeline**: Post-apocalyptic fantasy where old magic and new technology coexist
**Main Conflict**: The Aether Crystals are failing, threatening to plunge the world into the void

### Regions
1. **Crystalpeak Mountains** - Mining settlements, crystal caves, harsh weather
2. **Verdant Lowlands** - Agricultural towns, peaceful villages, trade routes
3. **The Shadowmere** - Dark swamplands, corrupted by failed magic experiments
4. **Skyport Metropolis** - Main city, airship docks, political center
5. **The Fractured Wastes** - Dangerous badlands where reality breaks down

### Factions
1. **Crystal Wardens** - Protectors of the Aether Crystals (Lawful Good)
2. **The Techno-Mages** - Blend magic with technology (Neutral)
3. **Void Cultists** - Embrace the coming apocalypse (Chaotic Evil)
4. **Free Traders** - Independent merchants and smugglers (Chaotic Neutral)
5. **The Ancien Guard** - Remnants of the old empire (Lawful Neutral)

## Character System

### Classes
1. **Aether Knight** - Tank/Paladin hybrid with crystal-powered abilities
2. **Void Walker** - Rogue/Assassin with shadow magic and teleportation
3. **Crystal Sage** - Mage with elemental mastery and crystal manipulation
4. **Sky Pirate** - Ranged fighter with firearms and gadgets
5. **Beast Whisperer** - Druid/Summoner with animal companions and nature magic

### Core Stats
- **Vitality** (Health, Constitution)
- **Aether** (Magic Power, Mana)
- **Might** (Physical Damage, Carrying Capacity)
- **Agility** (Speed, Dodge, Critical Chance)
- **Intellect** (Magic Damage, Learning Speed)
- **Charisma** (Social Skills, Leadership, Shop Prices)

### Skill Trees
Each class has 3 skill trees with 10 levels each:
- Combat Tree (damage, survivability)
- Utility Tree (exploration, crafting, social)
- Mastery Tree (ultimate abilities, class specialization)

## Combat System
**Type**: Hybrid Turn-Based/Real-Time
- **Real-time movement** and positioning
- **Turn-based actions** for abilities and attacks
- **Initiative system** determines action order
- **Elemental weaknesses** and resistances
- **Positioning matters** (flanking, backstab, cover)

### Damage Types
- **Physical** (slash, pierce, blunt)
- **Elemental** (fire, ice, lightning, earth)
- **Arcane** (pure magic, void, crystal)
- **Corrupted** (poison, disease, curse)

### Status Effects
- **Buffs**: Haste, Shield, Regeneration, Blessing
- **Debuffs**: Slow, Weakness, Bleeding, Curse
- **Crowd Control**: Stun, Sleep, Charm, Fear
- **Elemental**: Burning, Frozen, Shocked, Poisoned

## Quest System

### Quest Types
1. **Main Story** - Linear progression with major choices
2. **Faction Quests** - Reputation-based, mutually exclusive paths
3. **Side Quests** - Optional stories with moral choices
4. **Dynamic Events** - Randomly generated based on world state
5. **Procedural Dungeons** - Endless exploration content

### Choice Consequences
- **Immediate** - Direct quest resolution changes
- **Regional** - Affects local NPCs and availability
- **Global** - Changes world state and faction relations
- **Ending** - Determines final game outcome

## World Systems

### Day/Night Cycle
- **Dawn** (6-9 AM): Shops open, NPCs start daily routines
- **Day** (9 AM-6 PM): Full activity, optimal travel time
- **Dusk** (6-9 PM): Shops close, some NPCs change behavior
- **Night** (9 PM-6 AM): Danger increases, special events possible

### Weather System
- **Clear**: Normal visibility and movement
- **Rain**: Reduced fire magic, increased lightning damage
- **Storm**: Poor visibility, dangerous travel
- **Fog**: Limited sight, stealth advantages
- **Crystal Storm**: Magic fluctuations, random teleportation

### Economy
- **Supply/Demand** affects prices
- **Trade routes** influence availability
- **Faction control** impacts access
- **Player actions** affect market conditions

## Technical Architecture

### Core Modules
- `engine/` - Core game engine and systems
- `entities/` - Game objects (Player, NPCs, Items)
- `world/` - Map, regions, locations
- `combat/` - Battle system and mechanics
- `ui/` - Interface and menus
- `data/` - Game content and configuration
- `save/` - Save/load system
- `ai/` - NPC and enemy behavior

### Key Design Patterns
- **Entity Component System** for flexible game objects
- **State Machine** for game states and AI
- **Observer Pattern** for event handling
- **Factory Pattern** for object creation
- **Command Pattern** for player actions

### Performance Considerations
- **Spatial partitioning** for collision detection
- **Level-of-detail** for distant objects
- **Object pooling** for frequently created/destroyed objects
- **Lazy loading** for content not immediately needed

## Progression Systems

### Character Advancement
- **Experience Points** from combat, quests, exploration
- **Skill Points** for ability upgrades
- **Attribute Points** for stat increases
- **Talent Points** for special abilities

### Equipment Progression
- **Common** (white) - Basic gear
- **Uncommon** (green) - Minor bonuses
- **Rare** (blue) - Significant improvements
- **Epic** (purple) - Powerful abilities
- **Legendary** (orange) - Game-changing effects
- **Artifact** (red) - Unique story items

### Crafting System
- **Materials** gathered from exploration and combat
- **Recipes** learned from NPCs or found as loot
- **Quality levels** based on skill and materials
- **Enchanting** to add magical properties
- **Upgrading** to improve existing items

## Save System
- **Multiple save slots** (10 available)
- **Autosave** at key points
- **Quick save/load** for convenience
- **Checkpoint system** in dungeons
- **Character sheets** export for sharing builds