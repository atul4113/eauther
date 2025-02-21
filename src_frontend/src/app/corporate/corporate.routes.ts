import { Routes } from '@angular/router';

import { CorporateComponent } from "./component/corporate/corporate.component";
import { QuickTourComponent } from "./component/quick-tour/quick-tour.component";
import { AuthGuard } from "../common/guard/auth.guard";


export const CorporateRoutes: Routes = [
    {
        path: '',
        component: CorporateComponent,
        canActivate: [AuthGuard]
    },
    {
        path: '\/',
        component: CorporateComponent,
        canActivate: [AuthGuard]
    },
    {
        path: 'interactive-tutorials',
        component: QuickTourComponent,
        canActivate: [AuthGuard]
    },
];
