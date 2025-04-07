import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { HttpClientModule } from "@angular/common/http";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { MomentModule } from "ngx-moment";
import { FileUploadModule } from "ng2-file-upload";
import { PerfectScrollbarModule } from "ngx-perfect-scrollbar";

// Angular Material Modules
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
import { MatFormFieldModule } from "@angular/material/form-field";

// Guards
import { AuthGuard, OnlyNoAuthGuard, CanDeactivateGuard } from "./guard";

// Pipes
import { GetLabelPipe, PaginatePipe, TruncatePipe, SafeHtmlPipe } from "./pipe";

// Directives
import {
    TrimText,
    MDL,
    PutFooterBottom,
    MDLUP,
    AutoFocusAfterInit,
    FullScreenHeightDirective,
    MatMenuItemDisableHoverDirective,
} from "./directive";

// Components
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
    PaginatorComponent,
    AddLabelComponent,
    UploadFileComponent,
    PopupWithCheckboxComponent,
    SimpleUploadFileComponent,
    PopupWithInputComponent,
    PaginatorBaseComponent,
    BaseUploadFileComponent,
} from "./component";

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        HttpClientModule,
        RouterModule,
        MomentModule,
        FileUploadModule,
        PerfectScrollbarModule,

        // Angular Material Modules
        MatCheckboxModule,
        MatRadioModule,
        MatInputModule,
        MatFormFieldModule,
        MatCardModule,
        MatButtonModule,
        MatToolbarModule,
        MatListModule,
        MatTabsModule,
        MatMenuModule,
        MatTooltipModule,
        MatSelectModule,
        MatSlideToggleModule,

        // Standalone Components & Pipes
        BaseUploadFileComponent,
        SimpleUploadFileComponent,
        UploadFileComponent,
        PaginatorBaseComponent,
        GetLabelPipe, // ✅ moved from declarations
    ],
    declarations: [
        // ONLY non-standalone components/pipes/directives here
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
        PaginatorComponent,
        AddLabelComponent,
        PopupWithCheckboxComponent,
        PopupWithInputComponent,

        PutFooterBottom,
        TrimText,
        MDL,
        AutoFocusAfterInit,
        FullScreenHeightDirective,
        MatMenuItemDisableHoverDirective,

        // These must be NON-standalone pipes
        MDLUP,
        PaginatePipe,
        TruncatePipe,
        SafeHtmlPipe,
    ],
    exports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        HttpClientModule,
        RouterModule,
        MomentModule,
        FileUploadModule,
        PerfectScrollbarModule,

        // Angular Material
        MatCheckboxModule,
        MatRadioModule,
        MatInputModule,
        MatFormFieldModule,
        MatCardModule,
        MatButtonModule,
        MatToolbarModule,
        MatListModule,
        MatTabsModule,
        MatMenuModule,
        MatTooltipModule,
        MatSelectModule,
        MatSlideToggleModule,

        // Standalone
        BaseUploadFileComponent,
        SimpleUploadFileComponent,
        UploadFileComponent,
        PaginatorBaseComponent,
        GetLabelPipe,

        // Shared components
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
        PaginatorComponent,
        AddLabelComponent,
        PopupWithCheckboxComponent,
        PopupWithInputComponent,

        // Directives
        PutFooterBottom,
        TrimText,
        MDL,
        AutoFocusAfterInit,
        FullScreenHeightDirective,
        MatMenuItemDisableHoverDirective,

        // Pipes (non-standalone only)
        MDLUP,
        PaginatePipe,
        TruncatePipe,
        SafeHtmlPipe,
    ],
    providers: [AuthGuard, OnlyNoAuthGuard, CanDeactivateGuard],
})
export class AppCommonModule {}
