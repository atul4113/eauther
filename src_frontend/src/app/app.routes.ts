import { ModuleWithProviders } from "@angular/core";
import { Routes, RouterModule } from '@angular/router';

import { AppComponent } from "./app.component";
import { BaseComponent } from "./base.component";
import { HomeRoutes } from './home/home.routes';

import {
    AuthGuard, OnlyNoAuthGuard,
    CanDeactivateGuard
} from "./common/guard";
import { AccountsLoginComponent } from "./accounts/component/accounts-login/accounts-login.component";


export const AUTH_PROVIDERS = [
    AuthGuard, OnlyNoAuthGuard,
    CanDeactivateGuard
];

const appRoutes: Routes = [
    {
        path: 'accounts/login',
        component: AccountsLoginComponent,
        canActivate: [OnlyNoAuthGuard]
    },
    {
        path: 'accounts/login\/',
        component: AccountsLoginComponent,
        canActivate: [OnlyNoAuthGuard]
    },
    {
        path: 'corporate',
        loadChildren: 'app/corporate/corporate.module#CorporateModule'
    },
    {
        path: 'accounts',
        loadChildren: 'app/accounts/accounts.module#AccountsModule'
    },
    {
        path: 'mycontent',
        loadChildren: 'app/my-lessons/my-lessons.module#MyLessonsModule',
        data: { isProject: false }
    },
    {
        path: 'corporate',
        loadChildren: 'app/my-lessons/my-lessons.module#MyLessonsModule',
        data: { isProject: true }
    },
    {
        path: 'panel',
        loadChildren: 'app/admin/admin.module#AdminModule'
    },

    ...HomeRoutes,
];


export const routes: Routes = [
    {
        path: '',
        component: AppComponent,
        children: [
            {
                path: '',
                component: BaseComponent,
                children: [
                    ...appRoutes
                ]
            },
        ]
    },
];


export const APP_ROUTER_PROVIDERS: ModuleWithProviders = RouterModule.forRoot(routes);
