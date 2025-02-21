import { Component, OnInit } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from "@angular/platform-browser";
import { ActivatedRoute } from "@angular/router";
import { Observable } from "rxjs";

import { ITranslations } from "../../../common/model/translations";
import { TranslationsService } from "../../../common/service";
import { SettingsService } from "../../../common/service/settings.service";
import { AuthUserService } from "../../../common/service/auth-user.service";
import { ReferrerService } from "../../../common/service/referrer.service";


@Component({
    templateUrl: './home-main.component.html'
})
export class HomeMainComponent implements OnInit {
    public homeIframeSrc: SafeResourceUrl;
    public HomeIframeHeight: number;
    public translations: ITranslations;

    constructor(
        private _route: ActivatedRoute,
        private _referrer: ReferrerService,
        private _translations: TranslationsService,
        private _domSanitization: DomSanitizer,
        private _authUser: AuthUserService,
        private _settings: SettingsService
    ) {}

    ngOnInit() {
        let referrerKey = this._route.snapshot.params['referrerKey'] || null;

        Observable.forkJoin(
            this._translations.getTranslations(),
            this._authUser.get(),
            this._settings.get()
        ).flatMap(([translations, user, settings]) => {
            this.translations = translations;
            let currentLanguage = this._translations.getCurrentLanguage(settings, user);
            return this._referrer.getReferrerUrl(referrerKey, currentLanguage)
        }).subscribe((referrerUrl: string) => {
            if (referrerUrl) {
                this.homeIframeSrc = this._domSanitization.bypassSecurityTrustResourceUrl(referrerUrl);
            }
        });

        this._translations.getTranslations().subscribe(t => this.translations = t);
    }

    public onMessage (event: MessageEvent) {
        if (event && event.data && event.data.indexOf && event.data.indexOf('mCurriculum_RESIZE:') === 0) {
            let size = event.data
                .substring('mCurriculum_RESIZE:'.length)
                .split(':');
            this.HomeIframeHeight = parseInt(size[1]);
        }
    }
 }
