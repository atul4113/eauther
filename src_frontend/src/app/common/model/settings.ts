import { Referrers } from "./referrers";

export interface ISupportedLanguageRaw {
    id: number;
    key: string;
    description: string;
}

export class SupportedLanguage {
    public id: number;
    public key: string;
    public description: string;
    public iconKey: string;

    constructor (lang: ISupportedLanguageRaw) {
        this.id = lang.id;
        this.key = lang.key;
        this.description = lang.description;
        this.iconKey = this.normalizeIconKey(lang.key);
    }

    private normalizeIconKey (key: string): string {
        if (key.length >= 2) {
            return key.substr(0, 2).toLocaleLowerCase();
        } else {
            return 'en';
        }
    }
}


export interface ISettingsRaw {
    application_id: string;
    email: string;
    lang: string;
    select_user_language: boolean;
    referrers: Referrers;

    supported_languages: any[];
    version: string;
}

export class Settings {
    public applicationId: string;
    public email: string;
    public languageCode: string;
    public selectUserLanguage: boolean;
    public supportedLanguages: SupportedLanguage[];
    public referrers: Referrers;

    constructor (settings?: ISettingsRaw) {
        if (settings) {
            this.applicationId = settings.application_id;
            this.email = settings.email;
            this.languageCode = settings.lang;
            this.selectUserLanguage = settings.select_user_language;
            this.supportedLanguages = settings.supported_languages
                .map(lang => new SupportedLanguage(lang)).sort((l1, l2) => l1.iconKey.localeCompare(l2.iconKey));
            this.referrers = settings.referrers;
        }
    }

    // public getPublisher (publisherId: number): Publisher {
    //     return this.publishers.filter(publisher => publisher.id === publisherId)[0];
    // }

    public getSupportedLanguage (langId: number): SupportedLanguage {
        return this.supportedLanguages.filter(lang => lang.id === langId)[0];
    }

    public getSupportedLanguageByKey (langKey: string): SupportedLanguage {
        return this.supportedLanguages.filter(lang => lang.key.localeCompare(langKey) === 0)[0];
    }

    public getDefaultLanguage (): SupportedLanguage {
        return this.getSupportedLanguageByKey(this.languageCode);
    }
}
