import { ModuleWithProviders } from "@angular/core";
import { Routes, RouterModule } from "@angular/router";

import { AppComponent } from "./app.component";
import { BaseComponent } from "./base.component";
import { HomeRoutes } from "./home/home.routes";

import { AuthGuard, OnlyNoAuthGuard, CanDeactivateGuard } from "./common/guard";
import { AccountsLoginComponent } from "./accounts/component/accounts-login/accounts-login.component";

// Importing modules statically
import { CorporateModule } from "./corporate/corporate.module";
import { AccountsModule } from "./accounts/accounts.module";
import { MyLessonsModule } from "./my-lessons/my-lessons.module";
import { AdminModule } from "./admin/admin.module";

export const AUTH_PROVIDERS = [AuthGuard, OnlyNoAuthGuard, CanDeactivateGuard];

const appRoutes: Routes = [
    {
        path: "accounts/login",
        component: AccountsLoginComponent,
        canActivate: [OnlyNoAuthGuard],
    },
    {
        path: "accounts/login/",
        component: AccountsLoginComponent,
        canActivate: [OnlyNoAuthGuard],
    },
    {
        path: "corporate",
        loadChildren: () => CorporateModule, // Statically imported
    },
    {
        path: "accounts",
        loadChildren: () => AccountsModule, // Statically imported
    },
    {
        path: "mycontent",
        loadChildren: () => MyLessonsModule, // Statically imported
        data: { isProject: false },
    },
    {
        path: "corporate",
        loadChildren: () => MyLessonsModule, // Statically imported
        data: { isProject: true },
    },
    {
        path: "panel",
        loadChildren: () => AdminModule, // Statically imported
    },

    ...HomeRoutes,
];

export const routes: Routes = [
    {
        path: "",
        component: AppComponent,
        children: [
            {
                path: "",
                component: BaseComponent,
                children: [...appRoutes],
            },
        ],
    },
];

export const APP_ROUTER_PROVIDERS: ModuleWithProviders<RouterModule> =
    RouterModule.forRoot(routes);
