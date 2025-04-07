import { Component, OnInit } from "@angular/core";
import { DomSanitizer, SafeResourceUrl } from "@angular/platform-browser";
import { ActivatedRoute } from "@angular/router";
import { forkJoin } from "rxjs";
import { mergeMap } from "rxjs/operators";

import { ITranslations } from "../../../common/model/translations";
import { TranslationsService } from "../../../common/service";
import { SettingsService } from "../../../common/service/settings.service";
import { AuthUserService } from "../../../common/service/auth-user.service";
import { ReferrerService } from "../../../common/service/referrer.service";

@Component({
    templateUrl: "./home-main.component.html",
})
export class HomeMainComponent implements OnInit {
    public homeIframeSrc: any;
    public HomeIframeHeight: any;
    public translations: any;

    constructor(
        private _route: ActivatedRoute,
        private _referrer: ReferrerService,
        private _translations: TranslationsService,
        private _domSanitization: DomSanitizer,
        private _authUser: AuthUserService,
        private _settings: SettingsService
    ) {}

    ngOnInit() {
        let referrerKey = this._route.snapshot.params["referrerKey"] || null;

        forkJoin([
            this._translations.getTranslations(),
            this._authUser.get(),
            this._settings.get(),
        ])
            .pipe(
                mergeMap(
                    ([translations, user, settings]: [
                        ITranslations | null,
                        any,
                        any
                    ]) => {
                        this.translations =
                            translations ?? ({} as ITranslations);
                        let currentLanguage =
                            this._translations.getCurrentLanguage(
                                settings,
                                user
                            );
                        return this._translations.getTranslations();
                    }
                )
            )
            .subscribe((translations: ITranslations | null) => {
                if (translations) {
                    this.translations = translations;
                }
            });
    }

    public onMessage(event: Event | MessageEvent): void {
        if (
            event instanceof MessageEvent &&
            event.data &&
            typeof event.data === "object" &&
            "height" in event.data
        ) {
            this.HomeIframeHeight = event.data.height;
        }
    }
}
