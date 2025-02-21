import { NgModule } from '@angular/core';
import { CommonModule } from "@angular/common";
import { HttpModule } from "@angular/http";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { MomentModule } from "angular2-moment";
import {
    MatCheckboxModule, MatRadioModule, MatInputModule, MatCardModule, MatButtonModule,
    MatToolbarModule, MatListModule, MatTabsModule, MatMenuModule, MatTooltipModule, MatSelectModule,
    MatSlideToggleModule,
} from "@angular/material";
import { FileUploadModule } from "ng2-file-upload";
import { PerfectScrollbarModule } from "ngx-perfect-scrollbar";

import { AuthGuard, OnlyNoAuthGuard, CanDeactivateGuard } from "./guard";
import { GetLabelPipe, PaginatePipe, TruncatePipe, SafeHtmlPipe } from "./pipe";
import { TrimText, MDL, PutFooterBottom, MDLUP, AutoFocusAfterInit, FullScreenHeightDirective, MatMenuItemDisableHoverDirective } from "./directive";
import {
    AppHeaderComponent, AppFooterComponent, AppDrawerComponent, TinyMCEComponent, PageTitleBarComponent,
    PopupComponent, PopupBaseComponent, PopupWithRadioComponent, InfoMessagesComponent, LoadingComponent,
    PaginatorBaseComponent, PaginatorComponent, AddLabelComponent, UploadFileComponent, PopupWithCheckboxComponent,
    BaseUploadFileComponent, SimpleUploadFileComponent, PopupWithInputComponent
} from "./component";


const MODULES = [
    MomentModule, FileUploadModule, PerfectScrollbarModule,

    MatCheckboxModule, MatRadioModule, MatInputModule, MatCardModule, MatButtonModule,
    MatToolbarModule, MatListModule, MatTabsModule, MatMenuModule, MatTooltipModule, MatSelectModule,
    MatSlideToggleModule,
];

const COMMON_COMPONENTS = [
    AppHeaderComponent, AppFooterComponent, AppDrawerComponent, TinyMCEComponent, PageTitleBarComponent,
    PopupBaseComponent, PopupComponent, PopupWithRadioComponent, InfoMessagesComponent,
    LoadingComponent, PaginatorBaseComponent, PaginatorComponent, AddLabelComponent, PopupWithCheckboxComponent, PopupWithInputComponent,
    UploadFileComponent, BaseUploadFileComponent, SimpleUploadFileComponent
];

const COMMON_DIRECTIVES = [
    PutFooterBottom, TrimText, MDL, AutoFocusAfterInit, FullScreenHeightDirective, MatMenuItemDisableHoverDirective
];

const COMMON_PIPES = [
    GetLabelPipe, MDLUP, PaginatePipe, TruncatePipe, SafeHtmlPipe,
];

@NgModule({
    imports: [
        CommonModule, HttpModule, FormsModule, ReactiveFormsModule, RouterModule,

        MODULES,
    ],
    declarations: [
        COMMON_COMPONENTS, COMMON_DIRECTIVES, COMMON_PIPES,
    ],
    providers: [
        AuthGuard,
        OnlyNoAuthGuard,
        CanDeactivateGuard,
    ],
    exports: [
        MODULES, COMMON_COMPONENTS, COMMON_DIRECTIVES, COMMON_PIPES,
    ]
})
export class AppCommonModule {}
