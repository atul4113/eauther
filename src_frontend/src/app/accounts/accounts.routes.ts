import { Routes } from '@angular/router';

import {OnlyNoAuthGuard} from "../common/guard/only-no-auth.guard";
import { AccountsRegisterComponent } from "./component/accounts-register/accounts-register.component";
import { AccountsRegisterFinishComponent } from "./component/accounts-register-finish/accounts-register-finish.component";


export const AccountsRoutes: Routes = [
    {
        path: 'register',
        component: AccountsRegisterComponent,
        canActivate: [OnlyNoAuthGuard]
    },
    {
        path: 'register\/',
        component: AccountsRegisterComponent,
        canActivate: [OnlyNoAuthGuard]
    },
    {
        path: 'register/finish',
        component: AccountsRegisterFinishComponent,
        canActivate: [OnlyNoAuthGuard]
    },
];
