# Common Section Documentation

## Overview

The common section contains shared components, services, and utilities used throughout the application. It provides reusable functionality and maintains consistency across different sections of the application.

## Directory Structure

```
common/
├── component/         # Shared UI components
├── service/          # Shared services
├── model/            # Shared data models
├── pipe/             # Custom pipes
├── directive/        # Custom directives
├── guard/            # Route guards
├── templates/        # Shared templates
├── test/            # Test files
└── app.common.module.ts # Module definition
```

## Components

### Layout Components

1. **app-drawer/**

    - Application navigation drawer
    - Provides side menu functionality

2. **app-header/**

    - Application header
    - Contains navigation and user controls

3. **app-footer/**
    - Application footer
    - Contains footer information and links

### UI Components

1. **upload-file/**

    - File upload component
    - Handles file selection and upload

2. **simple-upload-file/**

    - Simplified file upload component
    - Basic file upload functionality

3. **base-upload-file/**

    - Base class for file upload components
    - Common upload functionality

4. **tiny-mce/**
    - Rich text editor integration
    - WYSIWYG editor component

### Popup Components

1. **popup/**

    - Generic popup component
    - Base popup functionality

2. **popup-base/**

    - Base class for popup components
    - Common popup functionality

3. **popup-with-checkbox/**

    - Popup with checkbox selection
    - Handles checkbox-based choices

4. **popup-with-input/**

    - Popup with input field
    - Handles text input in popups

5. **popup-with-radio/**
    - Popup with radio button selection
    - Handles single-choice selection

### Utility Components

1. **paginator/**

    - Pagination component
    - Handles page navigation

2. **paginator-base/**

    - Base pagination component
    - Common pagination functionality

3. **page-title-bar/**

    - Page title display
    - Shows section/page titles

4. **info-messages/**

    - Information message display
    - Shows system messages

5. **loading/**

    - Loading indicator
    - Shows loading states

6. **add-label/**
    - Label addition component
    - Handles label creation

## Services

### Authentication & Authorization

1. **token.service.ts**

    - Manages authentication tokens
    - Handles token storage and validation

2. **auth-user.service.ts**
    - Manages user authentication
    - Handles user session

### Data Management

1. **rest-client.service.ts**

    - HTTP client service
    - Handles API communication

2. **settings.service.ts**

    - Application settings
    - Manages configuration

3. **projects.service.ts**

    - Project management
    - Handles project data

4. **categories.service.ts**
    - Category management
    - Handles categorization

### Content Management

1. **translations.service.ts**

    - Translation management
    - Handles multilingual content

2. **translations-admin.service.ts**

    - Translation administration
    - Manages translation content

3. **news.service.ts**
    - News management
    - Handles news content

### File Management

1. **upload-file.service.ts**
    - File upload handling
    - Manages file operations

### Utility Services

1. **utils.service.ts**

    - Utility functions
    - Common helper methods

2. **referrer.service.ts**

    - Referrer management
    - Handles navigation history

3. **paths.service.ts**

    - Path management
    - Handles routing paths

4. **info-message.service.ts**

    - Message management
    - Handles system messages

5. **logo.service.ts**
    - Logo management
    - Handles application branding

## Module Configuration

-   **app.common.module.ts**: Defines the common module, including component declarations, imports, and providers

## Features

The common section provides:

-   Shared UI components
-   Authentication services
-   Data management
-   Content management
-   File handling
-   Utility functions
-   Navigation components
-   Message handling
-   Translation support

## Dependencies

-   Angular Core
-   Angular Router
-   Angular Material (if used)
-   HTTP Client
-   File handling libraries
-   Rich text editors
-   Authentication libraries
