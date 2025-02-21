import { NgModule } from '@angular/core';
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { HttpModule } from "@angular/http";
import { CommonModule } from "@angular/common";

import { AppCommonModule } from "../common/app.common.module";
import { AdminRoutes } from "./admin.routes";

import { AdminPanelComponent } from "./component/admin-panel.component";
import { TranslationsPanelComponent } from "./component/translations-panel.component";
import { BrowseLabelsPanelComponent } from "./component/browse-labels-panel.component";
import { LanguagesPanelComponent } from "./component/languages-panel.component";
import { ImagesPanelComponent } from "./component/images-panel.component";
import { TranslationsAdminService } from "../common/service/translations-admin.service";
import { ResolveConflictsPanelComponent } from "./component/resolve-conflicts-panel.component";
import { HomeWebsitesComponent } from "./component/home-websites.component";
import { GlobalSettingsComponent } from "./component/global-settings.component";


@NgModule({
    imports: [
        CommonModule, FormsModule, RouterModule, HttpModule,
        AppCommonModule, RouterModule.forChild(AdminRoutes)
    ],
    declarations: [
        AdminPanelComponent, TranslationsPanelComponent, BrowseLabelsPanelComponent, LanguagesPanelComponent,
        ImagesPanelComponent, ResolveConflictsPanelComponent, HomeWebsitesComponent, GlobalSettingsComponent
    ],
    providers: [ TranslationsAdminService ],
    exports: []
})
export class AdminModule {}
