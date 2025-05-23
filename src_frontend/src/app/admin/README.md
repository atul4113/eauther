# Admin Section Documentation

## Overview

The admin section provides administrative functionality for managing various aspects of the application including global settings, translations, languages, and website configurations.

## Directory Structure

```
admin/
├── component/         # UI components
├── service/          # Business logic services
├── model/            # Data models/interfaces
├── templates/        # Template files
├── test/            # Test files
├── admin.module.ts   # Module definition
└── admin.routes.ts   # Routing configuration
```

## Components

### Admin Panel Components

1. **admin-panel.component.ts**

    - Main container component for the admin section
    - Provides the base layout and navigation for admin features

2. **browse-labels-panel.component.ts**

    - Manages the display and editing of application labels
    - Handles label browsing and searching functionality

3. **global-settings.component.ts**

    - Manages global application settings
    - Provides interface for configuring system-wide parameters

4. **home-websites.component.ts**

    - Manages website configurations
    - Handles website creation, editing, and status management

5. **images-panel.component.ts**

    - Handles image management functionality
    - Provides interface for image upload and management

6. **languages-panel.component.ts**

    - Manages language configurations
    - Handles language addition, editing, and removal

7. **resolve-conflicts-panel.component.ts**

    - Handles conflict resolution between different versions
    - Provides interface for resolving data conflicts

8. **translations-panel.component.ts**
    - Manages translation entries
    - Provides interface for adding and editing translations

## Services

1. **global-settings.service.ts**

    - Handles global settings operations
    - Manages CRUD operations for system settings

2. **home-websites.service.ts**
    - Manages website-related operations
    - Handles website configuration and status updates

## Models

1. **label.ts**

    - Defines the structure for application labels
    - Contains properties for label identification and content

2. **language.ts**

    - Defines language configuration structure
    - Contains properties for language settings and metadata

3. **home-website.ts**

    - Defines website configuration structure
    - Contains properties for website settings and content

4. **home-websites-with-language.ts**

    - Combines website and language configurations
    - Used for multilingual website management

5. **home-website-status.ts**

    - Defines possible website statuses
    - Used for website state management

6. **conflict.ts**

    - Defines conflict data structure
    - Used in conflict resolution process

7. **global-settings.ts**
    - Defines global settings structure
    - Contains system-wide configuration properties

## Module Configuration

-   **admin.module.ts**: Defines the admin module, including component declarations, imports, and providers
-   **admin.routes.ts**: Configures routing for the admin section, defining navigation paths and component associations

## Usage

The admin section provides a comprehensive interface for system administrators to:

-   Manage global application settings
-   Handle multilingual content and translations
-   Configure and manage websites
-   Resolve data conflicts
-   Manage system labels and images

## Dependencies

-   Angular Core
-   Angular Router
-   Angular Forms
-   Angular Material (if used)
-   Custom services and models
