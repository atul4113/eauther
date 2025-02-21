import { Routes } from '@angular/router';

import { AuthGuard/*, PortalAdminGuard*/ } from "../common/guard";
import { AdminPanelComponent } from "./component/admin-panel.component";
import { TranslationsPanelComponent } from "./component/translations-panel.component";
import { BrowseLabelsPanelComponent } from "./component/browse-labels-panel.component";
import { LanguagesPanelComponent } from "./component/languages-panel.component";
import { ImagesPanelComponent } from "./component/images-panel.component";
import { ResolveConflictsPanelComponent } from "./component/resolve-conflicts-panel.component";
import { HomeWebsitesComponent } from "./component/home-websites.component";
import { GlobalSettingsComponent } from "./component/global-settings.component";


export const AdminRoutes: Routes = [
    {path: '', component: AdminPanelComponent, canActivate: [AuthGuard/*, PortalAdminGuard*/]},
    {path: 'translations', component: TranslationsPanelComponent, canActivate: [AuthGuard/*, PortalAdminGuard*/]},
    {path: 'translations/labels', component: BrowseLabelsPanelComponent, canActivate: [AuthGuard/*, PortalAdminGuard*/]},
    {path: 'translations/languages', component: LanguagesPanelComponent, canActivate: [AuthGuard/*, PortalAdminGuard*/]},
    {path: 'translations/images', component: ImagesPanelComponent, canActivate: [AuthGuard/*, PortalAdminGuard*/]},
    {path: 'translations/import/3/:id', component: ResolveConflictsPanelComponent, canActivate: [AuthGuard/*, PortalAdminGuard*/]},
    {path: 'home_websites', component: HomeWebsitesComponent, canActivate: [AuthGuard/*, PortalAdminGuard*/]},
    {path: 'settings', component: GlobalSettingsComponent, canActivate: [AuthGuard/*, PortalAdminGuard*/]},
];
