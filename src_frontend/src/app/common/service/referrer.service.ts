import { Injectable } from "@angular/core";
import { Observable, of } from "rxjs";
import { map, share } from "rxjs/operators";

import { Settings } from "../model";
import { SettingsService } from "./settings.service";
import { CookieService } from "./cookie/cookies.service";
import { SupportedLanguage } from "../model/settings";

const HOME_REFERRER_COOKIE = "home_referer";
const HOME_DEFAULT = "default";

interface Referrers {
    [key: string]: string;
}

@Injectable()
export class ReferrerService {
    private referrerUrl: string | null = null;
    private observe: Observable<string | null> | null = null;

    constructor(
        private readonly _cookie: CookieService,
        private readonly _settings: SettingsService
    ) {}

    private setHomeReferrerCookie(referrer: string = ""): void {
        const dateYearPlus = new Date();
        dateYearPlus.setTime(dateYearPlus.getTime() + 365 * 24 * 3600 * 1000);

        this._cookie.put(HOME_REFERRER_COOKIE, referrer, {
            expires: dateYearPlus,
        });
    }

    private mapReferrer(
        settings: Settings,
        referrerKey: string | null = null,
        currentLanguage: SupportedLanguage | null = null
    ): string | null {
        if (settings.referrers) {
            const referrers = settings.referrers as Referrers;
            let referrer: string | null = null;
            const httpReferrer = document.referrer;

            if (referrerKey && referrers[referrerKey]) {
                referrer = referrerKey;
            } else if (referrers[httpReferrer]) {
                referrer = httpReferrer;
            } else if (httpReferrer === "") {
                referrer = "";
            } else {
                const referrerCookie = this._cookie.get(HOME_REFERRER_COOKIE);
                if (referrerCookie) {
                    referrer = referrerCookie;
                } else {
                    referrer = "";
                }
            }

            if (referrer === "") {
                const languageKeyReferrer = currentLanguage
                    ? `${HOME_DEFAULT}_${currentLanguage.key}`
                    : HOME_DEFAULT;

                if (currentLanguage && referrers[languageKeyReferrer]) {
                    referrer = languageKeyReferrer;
                } else if (referrers[HOME_DEFAULT]) {
                    referrer = HOME_DEFAULT;
                }
                this.setHomeReferrerCookie("");
            } else {
                this.setHomeReferrerCookie(referrer);
            }
            return referrers[referrer] || null;
        }
        return null;
    }

    public getReferrerUrl(
        referrerKey: string | null = null,
        currentLanguage: SupportedLanguage | null = null
    ): Observable<string | null> {
        if (this.referrerUrl !== null) {
            return of(this.referrerUrl);
        } else if (this.observe) {
            return this.observe;
        } else {
            this.observe = this._settings.get().pipe(
                map((response) =>
                    this.mapReferrer(response, referrerKey, currentLanguage)
                ),
                share()
            );

            this.observe.subscribe({
                next: (referrerUrl) => (this.referrerUrl = referrerUrl),
            });

            return this.observe;
        }
    }
}
