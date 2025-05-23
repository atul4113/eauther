# Routing Documentation

## Overview

The SmartEdu application uses a hybrid routing approach where most routes are handled by backend templates, while the Angular frontend handles specific feature routes. This architecture allows for better SEO, server-side rendering, and integration with existing backend systems.

## Backend Template Routes

### Main Application Routes

```
/                   # Main landing page (backend template)
/accounts/          # Account management (backend template)
/admin/             # Admin dashboard (backend template)
/corporate/         # Corporate section (backend template)
```

### Authentication Routes

```
/accounts/login/            # Login page
/accounts/register/         # Registration page
/accounts/password-reset/   # Password reset
/accounts/verify-email/     # Email verification
```

### Content Management Routes

```
/my-lessons/               # Lesson management
/my-lessons/create/        # Lesson creation
/my-lessons/:id/          # Lesson details
/my-lessons/:id/edit/     # Lesson editing
```

## Frontend Routes (Angular)

### Admin Module Routes

```typescript
// admin.routes.ts
{
    path: 'admin',
    component: AdminPanelComponent,
    children: [
        { path: 'settings', component: GlobalSettingsComponent },
        { path: 'translations', component: TranslationsPanelComponent },
        { path: 'languages', component: LanguagesPanelComponent }
    ]
}
```

### Accounts Module Routes

```typescript
// accounts.routes.ts
{
    path: 'accounts',
    component: AccountsComponent,
    children: [
        { path: 'profile', component: UserProfileComponent },
        { path: 'settings', component: UserSettingsComponent }
    ]
}
```

### My Lessons Module Routes

```typescript
// my-lessons.routes.ts
{
    path: 'my-lessons',
    component: MyLessonsComponent,
    children: [
        { path: 'list', component: LessonsListComponent },
        { path: 'create', component: CreateLessonComponent },
        { path: ':id', component: LessonDetailsComponent }
    ]
}
```

## Backend Template Integration

### Template Structure

```
templates/
├── base.html              # Base template
├── accounts/             # Account templates
├── admin/               # Admin templates
├── corporate/           # Corporate templates
└── my-lessons/          # Lesson templates
```

### Template Features

1. **Server-Side Rendering**

    - Initial page load
    - SEO optimization
    - Meta tags management

2. **Authentication Integration**

    - Session management
    - CSRF protection
    - Security headers

3. **Content Management**
    - Dynamic content loading
    - Template inheritance
    - Asset management

## Route Handling Process

### 1. Initial Request

```
Browser Request → Backend Server → Template Rendering → Angular Bootstrap
```

### 2. Angular Navigation

```
Angular Router → Component Loading → API Calls → Template Updates
```

### 3. Backend Integration

```
API Request → Backend Processing → Response → Frontend Update
```

## Security Considerations

### Backend Security

-   CSRF token validation
-   Session management
-   Authentication checks
-   Permission verification

### Frontend Security

-   Route guards
-   Authentication state
-   API token management
-   Secure communication

## Best Practices

### Backend Templates

1. Use template inheritance
2. Implement proper caching
3. Optimize asset loading
4. Handle errors gracefully

### Frontend Routes

1. Implement lazy loading
2. Use route guards
3. Handle navigation errors
4. Maintain clean URLs

### Integration

1. Consistent error handling
2. Proper state management
3. Clear API contracts
4. Efficient data loading

## Development Guidelines

### Adding New Routes

1. Backend Template:

    ```python
    # urls.py
    path('new-feature/', views.new_feature, name='new_feature')
    ```

2. Frontend Route:
    ```typescript
    // feature.routes.ts
    {
        path: 'new-feature',
        component: NewFeatureComponent
    }
    ```

### Route Testing

1. Backend Tests:

    - URL resolution
    - View functions
    - Template rendering

2. Frontend Tests:
    - Route navigation
    - Component loading
    - Guard functionality

## Common Issues and Solutions

### 1. Route Conflicts

-   **Problem**: Backend and frontend route conflicts
-   **Solution**: Clear route separation and documentation

### 2. Authentication Issues

-   **Problem**: Session/token mismatches
-   **Solution**: Consistent auth state management

### 3. Loading Performance

-   **Problem**: Slow initial page load
-   **Solution**: Optimize template rendering and asset loading

## Related Files

-   `app.routes.ts`: Main application routes
-   `angular.json`: Angular configuration
-   `proxy.conf.json`: Development proxy settings
-   Backend URL configuration files

## Notes

-   Most routes are handled by backend templates for better SEO
-   Angular routes are used for dynamic features
-   Regular route audits are recommended
-   Keep documentation updated with route changes
