# SmartEdu Frontend Documentation

## Overview

SmartEdu is an educational content management system built with Angular. This frontend application provides a comprehensive platform for managing educational content, user accounts, and corporate resources.

## Project Structure

```
src_frontend/
├── src/                    # Source code
│   ├── app/               # Application code
│   │   ├── admin/         # Admin section
│   │   ├── accounts/      # User accounts
│   │   ├── corporate/     # Corporate features
│   │   ├── home/          # Home page
│   │   ├── my-lessons/    # Lesson management
│   │   └── common/        # Shared components
│   ├── assets/            # Static assets
│   ├── environments/      # Environment configurations
│   └── libs/              # Library files
├── e2e/                   # End-to-end tests
├── node_modules/          # Dependencies
└── configuration files    # Various config files
```

## Main Sections

### [Admin Section](src/app/admin/README.md)

The admin section provides administrative functionality for managing global settings, translations, languages, and website configurations.

### [Accounts Section](src/app/accounts/README.md)

Handles user authentication, registration, and account management functionality.

### [Corporate Section](src/app/corporate/README.md)

Provides functionality for managing corporate-level content, projects, and resources.

### [Home Section](src/app/home/README.md)

Serves as the main landing page and entry point of the application.

### [My Lessons Section](src/app/my-lessons/README.md)

A comprehensive module for managing educational content, including lesson creation, editing, and organization.

### [Common Section](src/app/common/README.md)

Contains shared components, services, and utilities used throughout the application.

## Configuration Files

### Angular Configuration

-   **angular.json**: Main Angular configuration file
    -   Defines build configurations
    -   Specifies project settings
    -   Configures assets and styles

### TypeScript Configuration

-   **tsconfig.json**: TypeScript compiler configuration
    -   Defines compilation options
    -   Specifies type checking rules
    -   Sets module resolution

### Testing Configuration

-   **karma.conf.js**: Karma test runner configuration
    -   Configures unit testing
    -   Sets up test environment
-   **protractor.conf.js**: Protractor configuration
    -   Configures end-to-end testing
    -   Sets up browser testing

### Build Tools

-   **gulpfile.js**: Gulp build configuration
    -   Defines build tasks
    -   Configures build pipeline
-   **gulpfile2.js**: Additional Gulp configuration
    -   Extended build tasks
    -   Additional build features

### Proxy Configuration

-   **proxy.config.json**: Development proxy configuration
    -   Configures API proxying
    -   Sets up development server
-   **proxy.conf.json**: Alternative proxy configuration
    -   Additional proxy settings
    -   Environment-specific configuration

### Package Management

-   **package.json**: NPM package configuration
    -   Lists project dependencies
    -   Defines scripts and commands
-   **yarn.lock**: Yarn dependency lock file
    -   Ensures consistent installations
    -   Locks dependency versions

### Code Quality

-   **tslint.json**: TypeScript linting configuration
    -   Defines code style rules
    -   Configures linting options
-   **.editorconfig**: Editor configuration
    -   Ensures consistent coding style
    -   Configures editor settings

### Version Control

-   **.gitignore**: Git ignore configuration
    -   Specifies ignored files
    -   Excludes build artifacts

## Getting Started

### Prerequisites

-   Node.js (LTS version)
-   npm or yarn
-   Angular CLI

### Installation

1. Clone the repository
2. Install dependencies:
    ```bash
    npm install
    # or
    yarn install
    ```

### Development

1. Start the development server:
    ```bash
    npm start
    # or
    yarn start
    ```
2. Navigate to `http://localhost:4200`

### Building

```bash
npm run build
# or
yarn build
```

### Testing

```bash
# Unit tests
npm run test
# or
yarn test

# End-to-end tests
npm run e2e
# or
yarn e2e
```

## Dependencies

-   Angular Core
-   Angular Router
-   Angular Forms
-   Angular Material
-   Various third-party libraries (see package.json)

## Contributing

1. Follow the coding style guidelines
2. Write tests for new features
3. Update documentation as needed
4. Submit pull requests with clear descriptions

## License

[Specify your license here]
