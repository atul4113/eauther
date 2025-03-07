import { NgModule } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { HttpClientModule } from "@angular/common/http";
import { CommonModule } from "@angular/common";

import { AppCommonModule } from "../common/app.common.module";
import { HomeMainComponent } from "./component/home-main/home-main.component";

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        RouterModule,
        HttpClientModule,
        AppCommonModule,
    ],
    declarations: [HomeMainComponent],
    exports: [HomeMainComponent],
})
export class HomeModule {}
