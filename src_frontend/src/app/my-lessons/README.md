# My Lessons Section Documentation

## Overview

The my-lessons section is a comprehensive module for managing educational content, including lesson creation, editing, viewing, and organization. It provides a complete interface for content management and lesson delivery.

## Directory Structure

```
my-lessons/
├── component/         # UI components
├── service/          # Business logic services
├── model/            # Data models/interfaces
├── my-lessons.module.ts # Module definition
└── my-lessons.routes.ts # Routing configuration
```

## Components

### Core Components

1. **my-lessons/**

    - Main container component for the lessons section
    - Provides the base layout and navigation

2. **lessons-list/**

    - Displays the list of available lessons
    - Handles lesson filtering and sorting

3. **lesson-card/**
    - Displays individual lesson preview cards
    - Shows lesson metadata and quick actions

### Lesson Management

1. **create-lesson/**

    - Handles new lesson creation
    - Provides lesson setup interface

2. **lesson-details/**

    - Main lesson details view
    - Manages lesson information display

3. **lesson-pages/**

    - Manages lesson page content
    - Handles page organization and navigation

4. **lesson-player/**
    - Provides lesson viewing interface
    - Handles lesson playback and interaction

### Metadata Management

1. **lesson-details-metadata/**

    - Manages lesson metadata
    - Handles metadata editing and display

2. **lesson-details-metadata-properties/**

    - Manages lesson properties
    - Handles property configuration

3. **lesson-details-metadata-title/**

    - Manages lesson titles
    - Handles title editing and validation

4. **lesson-details-metadata-pages-form/**

    - Manages lesson page forms
    - Handles page content editing

5. **lesson-details-metadata-icon/**

    - Manages lesson icons
    - Handles icon selection and display

6. **lesson-details-metadata-custom-field/**
    - Manages custom metadata fields
    - Handles custom field configuration

### Bug Tracking

1. **lesson-details-bug-track/**

    - Manages lesson bug tracking
    - Handles bug reporting and tracking

2. **lesson-details-bug-followers/**

    - Manages bug followers
    - Handles bug notification settings

3. **lesson-details-bug-form/**

    - Provides bug reporting interface
    - Handles bug submission

4. **lesson-details-bug-card/**
    - Displays bug information
    - Shows bug status and details

### Additional Features

1. **lesson-details-history/**

    - Tracks lesson changes
    - Shows revision history

2. **lesson-details-assets/**

    - Manages lesson assets
    - Handles asset upload and organization

3. **categories-list/**

    - Manages lesson categories
    - Handles category organization

4. **project-structure/**

    - Manages project organization
    - Handles project hierarchy

5. **project-structure-select/**

    - Provides project selection interface
    - Handles project navigation

6. **pages-list/**

    - Displays lesson pages
    - Handles page navigation

7. **pages-to-merge/**
    - Manages page merging
    - Handles content combination

## Services

### my-content.service.ts

-   Manages lesson content operations
-   Handles CRUD operations for lessons
-   Manages lesson metadata
-   Handles content organization
-   Provides content search and filtering

### create-lesson.service.ts

-   Manages lesson creation process
-   Handles initial lesson setup
-   Manages lesson templates
-   Provides validation and verification

## Module Configuration

-   **my-lessons.module.ts**: Defines the my-lessons module, including component declarations, imports, and providers
-   **my-lessons.routes.ts**: Configures routing for the my-lessons section, defining navigation paths and component associations

## Features

The my-lessons section provides:

-   Lesson creation and editing
-   Content management
-   Metadata management
-   Bug tracking
-   Asset management
-   Project organization
-   Page management
-   Category management
-   History tracking
-   Content delivery

## Dependencies

-   Angular Core
-   Angular Router
-   Angular Forms
-   Angular Material (if used)
-   Content management services
-   File upload services
-   Rich text editors
-   Media players
