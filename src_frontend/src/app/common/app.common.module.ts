import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { HttpClientModule } from "@angular/common/http";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { MomentModule } from "ngx-moment";
import { FileUploadModule } from "ng2-file-upload";
import { PerfectScrollbarModule } from "ngx-perfect-scrollbar";

// ✅ Correct Angular Material Imports
import { MatCheckboxModule } from "@angular/material/checkbox";
import { MatRadioModule } from "@angular/material/radio";
import { MatInputModule } from "@angular/material/input";
import { MatCardModule } from "@angular/material/card";
import { MatButtonModule } from "@angular/material/button";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatListModule } from "@angular/material/list";
import { MatTabsModule } from "@angular/material/tabs";
import { MatMenuModule } from "@angular/material/menu";
import { MatTooltipModule } from "@angular/material/tooltip";
import { MatSelectModule } from "@angular/material/select";
import { MatSlideToggleModule } from "@angular/material/slide-toggle";

// ✅ Import Guards
import { AuthGuard, OnlyNoAuthGuard, CanDeactivateGuard } from "./guard";

// ✅ Import Pipes
import { GetLabelPipe, PaginatePipe, TruncatePipe, SafeHtmlPipe } from "./pipe";

// ✅ Import Directives
import {
    TrimText,
    MDL,
    PutFooterBottom,
    MDLUP,
    AutoFocusAfterInit,
    FullScreenHeightDirective,
    MatMenuItemDisableHoverDirective,
} from "./directive";

// ✅ Import Components
import {
    AppHeaderComponent,
    AppFooterComponent,
    AppDrawerComponent,
    TinyMCEComponent,
    PageTitleBarComponent,
    PopupComponent,
    PopupBaseComponent,
    PopupWithRadioComponent,
    InfoMessagesComponent,
    LoadingComponent,
    PaginatorBaseComponent,
    PaginatorComponent,
    AddLabelComponent,
    UploadFileComponent,
    PopupWithCheckboxComponent,
    BaseUploadFileComponent,
    SimpleUploadFileComponent,
    PopupWithInputComponent,
} from "./component";

// ✅ Material Modules
const MATERIAL_MODULES = [
    MatCheckboxModule,
    MatRadioModule,
    MatInputModule,
    MatCardModule,
    MatButtonModule,
    MatToolbarModule,
    MatListModule,
    MatTabsModule,
    MatMenuModule,
    MatTooltipModule,
    MatSelectModule,
    MatSlideToggleModule,
];

// ✅ Common Components
const COMMON_COMPONENTS = [
    AppHeaderComponent,
    AppFooterComponent,
    AppDrawerComponent,
    TinyMCEComponent,
    PageTitleBarComponent,
    PopupBaseComponent,
    PopupComponent,
    PopupWithRadioComponent,
    InfoMessagesComponent,
    LoadingComponent,
    PaginatorBaseComponent,
    PaginatorComponent,
    AddLabelComponent,
    PopupWithCheckboxComponent,
    PopupWithInputComponent,
    UploadFileComponent,
    BaseUploadFileComponent,
    SimpleUploadFileComponent,
];

// ✅ Common Directives
const COMMON_DIRECTIVES = [
    PutFooterBottom,
    TrimText,
    MDL,
    AutoFocusAfterInit,
    FullScreenHeightDirective,
    MatMenuItemDisableHoverDirective,
];

// ✅ Common Pipes
const COMMON_PIPES = [
    GetLabelPipe,
    MDLUP,
    PaginatePipe,
    TruncatePipe,
    SafeHtmlPipe,
];

@NgModule({
    imports: [
        CommonModule,
        HttpClientModule,
        FormsModule,
        ReactiveFormsModule,
        RouterModule,
        MomentModule,
        FileUploadModule,
        PerfectScrollbarModule,
        ...MATERIAL_MODULES, // ✅ Spread Operator for Material Modules
    ],
    declarations: [...COMMON_COMPONENTS, ...COMMON_DIRECTIVES, ...COMMON_PIPES],
    providers: [AuthGuard, OnlyNoAuthGuard, CanDeactivateGuard],
    exports: [
        ...MATERIAL_MODULES,
        ...COMMON_COMPONENTS,
        ...COMMON_DIRECTIVES,
        ...COMMON_PIPES,
    ],
})
export class AppCommonModule {}
