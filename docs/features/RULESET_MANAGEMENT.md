# Multiple Ruleset Management

## Overview

TaskMover is being enhanced with the ability to maintain and quickly switch between multiple rulesets. This feature allows users to create specific rule collections for different contexts (work, personal, specific projects) and switch between them without having to manually recreate rules.

## Current Status: IN DEVELOPMENT

**Completion Status:** 15% (Planning and initial framework)

## Features Being Implemented

### Ruleset Management Infrastructure
- **Ruleset Manager Class**: Core backend for managing multiple rulesets
- **File Structure**: Organization of ruleset files in the configuration directory
- **Loading/Saving Logic**: Efficient serialization and loading of ruleset collections

### Ruleset Switching
- **Quick Switching UI**: Simple interface for changing active ruleset
- **Persistence**: Remembering the last used ruleset
- **Automatic Rule Application**: Applying the new ruleset when switched

### Ruleset Creation and Editing
- **Creating New Rulesets**: From scratch or by duplicating existing ones
- **Importing/Exporting Rulesets**: Sharing rulesets between installations
- **Renaming/Deleting Rulesets**: Managing the ruleset collection

### Shared Pattern Library
- **Single Pattern Repository**: All rulesets access the same pattern library
- **Pattern Usage Tracking**: Seeing which rulesets use specific patterns
- **Smart Pattern Updates**: Updating patterns across all rulesets

### UI Integration
- **Ruleset Manager Tab**: Dedicated tab for managing ruleset collections
- **Status Indicators**: Clear indicators of which ruleset is active
- **Menu Integration**: Convenient ruleset operations from the menu

## Implementation Status

| Component | Status | Description |
|-----------|--------|-------------|
| `RulesetManager` Class | 🚧 Planned | Core class for ruleset operations |
| Pattern Library Simplification | 🚧 Planned | Remove multiple pattern sets, focus on shared library |
| `RulesetManagerTab` | 🚧 Planned | UI tab for managing rulesets |
| Ruleset Switching Dialog | 🚧 Planned | UI for selecting and switching rulesets |
| App Integration | 🚧 Planned | Integrate with main application |
| Documentation | 🚧 In Progress | This document and related help content |
| Testing | 🚧 Planned | Verification of correct functionality |

## Technical Design

### File Structure
```
config_directory/
  ├─ pattern_library.json   # Single shared pattern library
  └─ rulesets/
      ├─ default.json       # Default ruleset
      ├─ work.json          # Example custom ruleset
      └─ personal.json      # Example custom ruleset
```

### Ruleset File Format
```json
{
  "name": "work",
  "description": "Rules for organizing work files",
  "created": "2025-06-21T15:30:00",
  "modified": "2025-06-21T15:30:00",
  "rules": {
    "rule1": {
      "name": "Documents",
      "path": "C:/Documents",
      "active": true,
      "patterns": ["*.docx", "*.pdf"],
      "unzip": false
    },
    "rule2": {
      // Another rule...
    }
  }
}
```

## Use Cases

### Common User Workflows

1. **Creating different rule environments**
   - Work rules that organize files by project
   - Personal rules that organize files by type
   - Temporary rules for one-time organization tasks

2. **Quickly switching contexts**
   - Switch from work to personal organization rules with one click
   - Switch to a special ruleset for a specific task, then back to default

3. **Sharing organization strategies**
   - Export a well-crafted ruleset to share with colleagues
   - Import ruleset templates for common organization strategies

## Next Steps

1. Implement the `RulesetManager` class with core functionality
2. Refactor `PatternLibraryManager` to support shared pattern access
3. Create the UI components for ruleset management
4. Integrate with the main application
5. Test thoroughly with multiple rulesets
6. Complete documentation and help content

## Completion Criteria

The feature will be considered complete when:

1. Users can create, edit, delete, and switch between rulesets
2. All rulesets have access to the shared pattern library
3. The UI clearly indicates the active ruleset
4. Ruleset operations (switch, import, export) work reliably
5. All interactions have appropriate error handling and user feedback
6. Documentation is complete and accurate
