import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { map, share } from "rxjs/operators";

import { Settings } from "../model";
import { SettingsService } from "./settings.service";
import { CookieService } from "./cookie/cookies.service";
import { SupportedLanguage } from "../model/settings";

declare var document: any;

const HOME_REFERRER_COOKIE = "home_referer";
const HOME_DEFAULT = "default";

@Injectable()
export class ReferrerService {
    private referrerUrl: string;
    private observe: Observable<string>;

    constructor(
        private _cookie: CookieService,
        private _settings: SettingsService
    ) {}

    private setHomeReferrerCookie(referrer: string = "") {
        let dateYearPlus = new Date();
        dateYearPlus.setTime(dateYearPlus.getTime() + 365 * 24 * 3600 * 1000);

        this._cookie.put(HOME_REFERRER_COOKIE, referrer, {
            expires: dateYearPlus,
        });
    }

    private mapReferrer(
        settings: Settings,
        referrerKey: string = null,
        currentLanguage: SupportedLanguage = null
    ): string {
        if (settings.referrers) {
            let referrers = settings.referrers;
            let referrer: string = null;
            let httpReferrer = document.referrer;

            if (referrerKey && referrers[referrerKey]) {
                referrer = referrerKey;
            } else if (referrers[httpReferrer]) {
                referrer = httpReferrer;
            } else if (httpReferrer === "") {
                referrer = "";
            } else {
                let referrerCookie = this._cookie.get(HOME_REFERRER_COOKIE);
                if (referrerCookie) {
                    referrer = referrerCookie;
                } else {
                    referrer = "";
                }
            }

            if (referrer === "") {
                let languageKeyReferrer =
                    HOME_DEFAULT + "_" + currentLanguage.key;
                if (currentLanguage && referrers[languageKeyReferrer]) {
                    referrer = languageKeyReferrer;
                } else if (referrers[HOME_DEFAULT]) {
                    referrer = HOME_DEFAULT;
                }
                this.setHomeReferrerCookie("");
            } else {
                this.setHomeReferrerCookie(referrer);
            }
            return referrers[referrer];
        } else {
            return null;
        }
    }

    public getReferrerUrl(
        referrerKey: string = null,
        currentLanguage: SupportedLanguage = null
    ): Observable<string> {
        if (this.referrerUrl) {
            return Observable.of(this.referrerUrl);
        } else if (this.observe) {
            return this.observe;
        } else {
            this.observe = this._settings.get().pipe(
                map((response) =>
                    this.mapReferrer(response, referrerKey, currentLanguage)
                ),
                share()
            );

            this.observe.subscribe(
                (referrerUrl: string) => (this.referrerUrl = referrerUrl)
            );

            return this.observe;
        }
    }
}
