import { NgModule } from '@angular/core';
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { HttpModule } from "@angular/http";
import { CommonModule } from "@angular/common";

import { AppCommonModule } from "../common/app.common.module";
import { HomeMainComponent } from "./component/home-main/home-main.component";


@NgModule({
    imports: [
        CommonModule, FormsModule, RouterModule, HttpModule,
        AppCommonModule
    ],
    declarations: [
        HomeMainComponent,
    ],
    exports: [
        HomeMainComponent,
    ]
})
export class HomeModule {}
