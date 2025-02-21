import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { HttpModule } from '@angular/http';
import { CommonModule } from '@angular/common';

import { AppCommonModule } from '../common/app.common.module';
import { CorporateRoutes } from './corporate.routes';

import { CorporateComponent } from './component/corporate/corporate.component';
import { CorporateTilesComponent } from './component/corporate-tiles/corporate-tiles.component';
import { CorporateNewsComponent } from './component/corporate-news/corporate-news.component';
import { CorporateLessonsListComponent } from './component/corporate-lessons-list/corporate-lessons-list.component';
import { CorporateProjectsListComponent } from './component/corporate-projects-list/corporate-projects-list.component';
import { QuickTourComponent } from './component/quick-tour/quick-tour.component';


@NgModule({
    imports: [
        CommonModule, FormsModule, RouterModule, HttpModule,
        AppCommonModule, RouterModule.forChild(CorporateRoutes)
    ],
    declarations: [
        CorporateComponent,
        CorporateTilesComponent,
        CorporateNewsComponent,
        CorporateLessonsListComponent,
        CorporateProjectsListComponent,
        QuickTourComponent,
    ]
})
export class CorporateModule {}
