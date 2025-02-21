import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { HttpModule } from "@angular/http";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { PERFECT_SCROLLBAR_CONFIG, PerfectScrollbarConfigInterface } from "ngx-perfect-scrollbar";

import { AppCommonModule } from "./common/app.common.module";
import { APP_ROUTER_PROVIDERS, AUTH_PROVIDERS } from "./app.routes";

import { HomeModule } from "./home/home.module";

import { BaseComponent } from "./base.component";
import { AccountsLoginComponent } from "./accounts/component/accounts-login/accounts-login.component";

import { CookieService } from "./common/service/cookie/cookies.service";
import { AuthUserService } from "./common/service/auth-user.service";
import { InfoMessageService } from "./common/service/info-message.service";
import { PathsService } from "./common/service/paths.service";
import { TokenService } from "./common/service/token.service";
import { ProjectsService } from "./common/service/projects.service";
import { TranslationsService } from "./common/service/translations.service";
import { RestClientService } from "./common/service/rest-client.service";
import { SettingsService } from "./common/service/settings.service";
import { UtilsService } from "./common/service/utils.service";
import { ReferrerService } from "./common/service/referrer.service";


const DEFAULT_PERFECT_SCROLLBAR_CONFIG: PerfectScrollbarConfigInterface = {
    suppressScrollX: true,
    wheelPropagation: true,
};


@NgModule({
    imports: [
        BrowserModule, FormsModule, RouterModule, HttpModule, BrowserAnimationsModule,
        AppCommonModule, APP_ROUTER_PROVIDERS,

        HomeModule,
    ],
    declarations: [
        AppComponent,

        BaseComponent,
        AccountsLoginComponent,
    ],
    bootstrap: [ AppComponent ],
    providers: [
        AUTH_PROVIDERS,

        RestClientService,
        AuthUserService,
        InfoMessageService,
        PathsService,
        TokenService,
        ProjectsService,
        TranslationsService,
        CookieService,
        SettingsService,
        UtilsService,
        ReferrerService,
        {
            provide: PERFECT_SCROLLBAR_CONFIG,
            useValue: DEFAULT_PERFECT_SCROLLBAR_CONFIG
        }
    ]
})
export class AppModule { }
