import { Routes } from '@angular/router';

import { HomeMainComponent } from './component/home-main/home-main.component';


export const HomeRoutes: Routes = [
    {path: '', component: HomeMainComponent},
    {path: 'home', component: HomeMainComponent},
    {path: 'home/from/:referrerKey', component: HomeMainComponent},
];
