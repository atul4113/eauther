import { NgModule } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { HttpClientModule } from "@angular/common/http";
import { CommonModule } from "@angular/common";
import { MatCardModule } from "@angular/material/card";
import { MatDividerModule } from "@angular/material/divider";
import { MatButtonModule } from "@angular/material/button";

import { PutFooterBottom } from "../common/directive/put-footer-bottom.directive";

import { AppCommonModule } from "../common/app.common.module";
import { CorporateRoutes } from "./corporate.routes";

import { CorporateComponent } from "./component/corporate/corporate.component";
import { CorporateTilesComponent } from "./component/corporate-tiles/corporate-tiles.component";
import { CorporateNewsComponent } from "./component/corporate-news/corporate-news.component";
import { CorporateLessonsListComponent } from "./component/corporate-lessons-list/corporate-lessons-list.component";
import { CorporateProjectsListComponent } from "./component/corporate-projects-list/corporate-projects-list.component";
import { QuickTourComponent } from "./component/quick-tour/quick-tour.component";

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        RouterModule,
        HttpClientModule,
        MatCardModule,
        MatDividerModule,
        MatButtonModule,
        AppCommonModule,
        RouterModule.forChild(CorporateRoutes),
    ],
    declarations: [
        CorporateComponent,
        CorporateTilesComponent,
        CorporateNewsComponent,
        CorporateLessonsListComponent,
        CorporateProjectsListComponent,
        QuickTourComponent,
    ],
})
export class CorporateModule {}
