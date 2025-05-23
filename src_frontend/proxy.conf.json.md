# Proxy Configuration Documentation

## Overview

The `proxy.conf.json` file configures the development server's proxy settings for the SmartEdu frontend application. It routes API requests to the backend server during development, handling various endpoints and their specific configurations.

## Configuration Details

### Media and File Handling

```json
{
    "/media": {
        "target": "http://localhost:8000",
        "secure": false
    },
    "/file/serve": {
        "target": "http://localhost:8000",
        "secure": false
    }
}
```

-   **Purpose**: Routes media and file requests to the backend
-   **Target**: Backend server at `http://localhost:8000`
-   **Security**: Non-secure connection (HTTP)
-   **Use Cases**:
    -   Serving media files (images, videos)
    -   File downloads and uploads
    -   Static file serving

### API Endpoints

```json
{
    "/api": {
        "target": "http://localhost:8000",
        "secure": false,
        "changeOrigin": true,
        "logLevel": "debug"
    }
}
```

-   **Purpose**: General API request handling
-   **Features**:
    -   Origin header modification
    -   Debug logging enabled
    -   Handles all `/api` routes

### JWT Authentication

```json
{
    "/api/v2/jwt": {
        "target": "http://localhost:8000",
        "secure": false,
        "changeOrigin": true,
        "logLevel": "debug",
        "pathRewrite": {
            "^/api/v2/jwt": "/api/v2/jwt"
        }
    }
}
```

-   **Purpose**: JWT token authentication endpoints
-   **Features**:
    -   Path rewriting
    -   Debug logging
    -   Origin modification
-   **Use Cases**:
    -   Token generation
    -   Token validation
    -   Authentication requests

### User Session Management

```json
{
    "/accounts/login/session": {
        "target": "http://localhost:8000",
        "secure": false
    }
}
```

-   **Purpose**: User session handling
-   **Use Cases**:
    -   Session creation
    -   Session validation
    -   Login state management

### API Version 2

```json
{
    "/api/v2": {
        "target": "http://localhost:8000",
        "secure": false
    }
}
```

-   **Purpose**: Version 2 API endpoints
-   **Use Cases**:
    -   Modern API features
    -   Updated endpoints
    -   New functionality

### User Management

```json
{
    "/user": {
        "target": "http://localhost:8000",
        "secure": false
    },
    "/user/logout": {
        "target": "http://localhost:8000",
        "secure": false
    }
}
```

-   **Purpose**: User-related operations
-   **Features**:
    -   User profile management
    -   Logout functionality
-   **Use Cases**:
    -   User profile updates
    -   Session termination
    -   User preferences

### Corporate Features

```json
{
    "/corporate/no_space_info": {
        "target": "http://localhost:8000",
        "secure": false
    }
}
```

-   **Purpose**: Corporate-specific endpoints
-   **Use Cases**:
    -   Corporate space management
    -   Organization settings
    -   Corporate user features

### Content Management

```json
{
    "/mycontent": {
        "target": "http://localhost:8000",
        "secure": false,
        "changeOrigin": true
    }
}
```

-   **Purpose**: User content management
-   **Features**:
    -   Origin modification
    -   Content handling
-   **Use Cases**:
    -   User content access
    -   Content management
    -   Personal content storage

## Configuration Options

### Common Properties

-   **target**: Backend server URL
-   **secure**: SSL/TLS configuration
-   **changeOrigin**: Header modification
-   **logLevel**: Logging detail level
-   **pathRewrite**: URL path modification

### Security Considerations

-   All endpoints use non-secure connections (`"secure": false`)
-   Development-only configuration
-   Not suitable for production use

## Usage

### Development Setup

1. Ensure backend server is running on `http://localhost:8000`
2. Start Angular development server:
    ```bash
    ng serve --proxy-config proxy.conf.json
    ```

### Testing

1. Verify all endpoints are accessible
2. Check proxy logs for debugging
3. Test file uploads and downloads
4. Validate authentication flows

### Troubleshooting

1. Check backend server availability
2. Verify endpoint configurations
3. Review proxy logs
4. Test individual endpoints

## Best Practices

1. Keep proxy configuration organized
2. Document new endpoints
3. Use appropriate security settings
4. Maintain clear endpoint naming
5. Regular configuration review

## Related Files

-   `proxy.config.json`: Alternative proxy configuration
-   `angular.json`: Angular project configuration
-   Environment files: Environment-specific settings

## Notes

-   This configuration is for development only
-   Production should use proper security settings
-   Regular updates may be needed for new endpoints
-   Monitor proxy performance and logs
