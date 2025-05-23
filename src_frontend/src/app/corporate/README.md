# Corporate Section Documentation

## Overview

The corporate section provides functionality for managing corporate-level content, projects, and resources. It serves as a hub for corporate users to access and manage their organization's educational content and projects.

## Directory Structure

```
corporate/
├── component/         # UI components
├── model/            # Data models/interfaces
├── corporate.module.ts # Module definition
└── corporate.routes.ts # Routing configuration
```

## Components

### Core Components

1. **corporate/**

    - Main container component for the corporate section
    - Provides the base layout and navigation

2. **corporate-tiles/**

    - Displays corporate dashboard tiles
    - Shows key metrics and quick access points

3. **corporate-projects-list/**

    - Manages corporate projects
    - Displays and organizes project information

4. **corporate-lessons-list/**

    - Manages corporate lessons
    - Displays and organizes lesson content

5. **corporate-news/**

    - Displays corporate news and updates
    - Manages news content and announcements

6. **quick-tour/**
    - Provides guided tour functionality
    - Helps new users navigate the corporate section

## Module Configuration

-   **corporate.module.ts**: Defines the corporate module, including component declarations, imports, and providers
-   **corporate.routes.ts**: Configures routing for the corporate section, defining navigation paths and component associations

## Features

The corporate section provides:

-   Corporate dashboard
-   Project management
-   Lesson management
-   News and announcements
-   Quick tour functionality
-   Corporate resource organization
-   Team collaboration tools

## Dependencies

-   Angular Core
-   Angular Router
-   Angular Material (if used)
-   Corporate services
-   Project management services
-   Content management services
-   News feed services
