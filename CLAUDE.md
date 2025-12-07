# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-driven Blender Geometry Nodes pipeline using "glue code" pattern. The system wraps Blender's Geometry Nodes into simple Python APIs for AI agents to call, avoiding direct vertex manipulation while maintaining model integrity.

**Core Philosophy**: Humans define atomic rules (Node Groups), AI performs molecular assembly.

## Commands

### Generate Node Library
```bash
blender --background --python scripts/create_node_library.py
```
Creates `assets/node_library.blend` with 24 predefined node groups.

### Verify Node Library
```bash
blender --background --python scripts/verify_node_library.py
```

### Run Examples
```bash
blender assets/node_library.blend --python examples/demo_test.py
blender assets/node_library.blend --python examples/new_api_demo.py
```

### Run Tests
```bash
blender --background --python tests/test_gnodes_builder.py
blender --background --python tests/test_deformations.py
```

## Architecture

### Core Library (`src/gnodes_builder/`)

- **`builder.py`** - `GNodesBuilder` class: Main API for constructing 3D models via geometry node chains
  - Chain-style API: `add_node_group()` → `finalize()`
  - Semantic spatial APIs: `face_towards()`, `face_away_from()`, `align_tangent_to_circle()`
  - Factory functions: `create_cube()`, `create_cylinder()`, `create_sphere()`

- **`loader.py`** - `NodeLibraryManager`: Loads node groups from external .blend files

- **`templates.py`** - Composite object templates: `create_chair()`, `create_table_with_chairs()`, `create_fence()`, `create_door_frame()`

### Node Group Conventions

All node groups follow the **S.I.O Protocol**:
- **S** (Size/Scale): Accept Vector size inputs
- **I** (Integers/Seed): Expose Seed interface for random effects
- **O** (Origin): Output origin at bottom center

Node group naming: Must start with `G_` prefix (e.g., `G_Base_Cube`, `G_Align_Ground`)

### Two Origin Modes

| Mode | Node Groups | When to Use | G_Align_Ground |
|------|------------|-------------|----------------|
| Bottom-centered | `G_Base_XXX` | Ground placement | Required |
| Geometry-centered | `G_Base_XXX_Centered` | Rotation/floating parts | Do NOT use |

### API Priority (Important for AI usage)

1. **Highest**: Use composite templates (`create_table_with_chairs()`, etc.)
2. **Medium**: Use semantic APIs (`face_towards()`, `face_away_from()`)
3. **Lowest**: Manual rotation with known angles (`set_rotation_degrees()`)
4. **Forbidden**: Manual `atan2()` calculation then `set_rotation()`

## Key Files

- `docs/ai/ai_agent_prompt.md` - System prompt for AI agents (617 lines, comprehensive API reference)
- `docs/ai/api_quick_reference.md` - Quick API reference
- `scripts/create_node_library.py` - Node group definitions (creates all 24 node groups)

## Important Notes

- All dimensions are in **meters**
- All scripts must run inside Blender Python environment
- Always call `finalize()` to complete node chain
- For ground-placed objects using non-Centered versions, always end with `G_Align_Ground`
