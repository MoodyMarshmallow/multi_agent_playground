# Documentation Module - CLAUDE.md

This file provides guidance to Claude Code when working with the docs module of the multi-agent simulation framework.

## Module Overview

The docs module contains project documentation, legacy code references, and development guides. This directory serves as a knowledge base and historical reference for the project evolution.

## Directory Structure

### Architecture Documentation
- **Object-Centric-Architecture-Guide.md**: Core architectural patterns and design principles

### Legacy Backend Code (`old backend/`)
Contains previous backend implementation for reference:
- **character_agent/**: Previous agent implementations (clin.py, kani_agent.py)
- **memory/**: Legacy memory management system
- **server/**: Previous server controller implementation
- **objects/**: Legacy object system

### Text Game Implementations
Multiple iterations of the text adventure game engine:

#### Current Reference (`text_game/`)
- **README.md**: Text game implementation guide
- **canonical_world.py**: World state definitions
- **house_actions/**: Action implementations with legend system
- **demo_test.py**: Demonstration and testing scripts

#### Legacy Implementation (`text_game_old/`)
- **canonical_demo.py**: Previous demo implementation
- **game_entry.py**: Legacy game initialization
- **house_actions/**: Previous action system with detailed implementations
- **minimal_demo.py**: Simplified demonstration

## Development Guidelines

### Using Documentation
- **Architecture Guide**: Consult for design patterns and system architecture decisions
- **Legacy Code**: Reference for understanding evolution and alternative approaches
- **Text Game Docs**: Implementation details for game engine features

### Adding Documentation
1. Follow existing markdown structure and formatting
2. Include code examples where relevant
3. Document design decisions and rationale
4. Cross-reference related components

### Legacy Code Usage
- **Do not copy** legacy code directly into current implementation
- Use as reference for understanding previous approaches
- Legacy house_actions/ shows detailed action implementations
- Memory system examples for persistence patterns

### Text Game Development
- Review `text_game/README.md` for current implementation patterns
- Study `canonical_world.py` for world building examples
- Check `house_actions/legend.py` for action categorization

## Key Documentation Areas

### Architecture Patterns
- Object-centric design principles
- Component separation and modularity
- Data flow and state management

### Game Engine Evolution
- Action system development history
- World state management approaches
- Agent integration patterns

### Implementation Examples
- House action implementations across versions
- World building and location setup
- Character and item management

## Common Use Cases

### Understanding System Design
1. Read Object-Centric-Architecture-Guide.md for overall patterns
2. Compare current vs legacy implementations
3. Study evolution of action systems

### Implementing New Features
1. Check existing documentation for similar patterns
2. Review legacy implementations for alternative approaches
3. Document new features following established patterns

### Troubleshooting
1. Compare current implementation with legacy versions
2. Check demo files for expected behavior
3. Review action implementations for debugging patterns

## Maintenance Notes

### Documentation Updates
- Keep architecture guide current with system changes
- Add new implementation patterns as they emerge
- Document major refactoring decisions

### Legacy Code Management
- Preserve legacy code for reference but avoid direct usage
- Document lessons learned from previous implementations
- Maintain clear separation between current and legacy approaches

### Cross-References
- Link documentation to current backend implementation
- Reference specific files and line numbers where helpful
- Maintain bidirectional references between docs and code