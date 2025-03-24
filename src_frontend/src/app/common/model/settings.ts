import { Referrers } from "./referrers";

export interface ISupportedLanguageRaw {
    id: number;
    key: string;
    description: string;
}

export class SupportedLanguage {
    public readonly id: number;
    public readonly key: string;
    public readonly description: string;
    public readonly iconKey: string;

    constructor(lang: ISupportedLanguageRaw) {
        this.id = lang.id;
        this.key = lang.key;
        this.description = lang.description;
        this.iconKey = this.normalizeIconKey(lang.key);
    }

    private normalizeIconKey(key: string): string {
        if (key.length >= 2) {
            return key.substr(0, 2).toLocaleLowerCase();
        } else {
            return "en";
        }
    }
}

export interface ISettingsRaw {
    application_id: string;
    email: string;
    lang: string;
    select_user_language: boolean;
    referrers: Referrers;
    supported_languages: ISupportedLanguageRaw[];
    version: string;
}

export class Settings {
    public readonly applicationId: string = "";
    public readonly email: string = "";
    public readonly languageCode: string = "";
    public readonly selectUserLanguage: boolean = false;
    public readonly supportedLanguages: SupportedLanguage[] = [];
    public readonly referrers: Referrers = {};

    constructor(settings?: ISettingsRaw) {
        if (settings) {
            this.applicationId = settings.application_id;
            this.email = settings.email;
            this.languageCode = settings.lang;
            this.selectUserLanguage = settings.select_user_language;
            this.supportedLanguages = settings.supported_languages
                .map((lang) => new SupportedLanguage(lang))
                .sort((l1, l2) => l1.iconKey.localeCompare(l2.iconKey));
            this.referrers = settings.referrers;
        }
    }

    // public getPublisher (publisherId: number): Publisher {
    //     return this.publishers.filter(publisher => publisher.id === publisherId)[0];
    // }

    public getSupportedLanguage(langId: number): SupportedLanguage | undefined {
        return this.supportedLanguages.find((lang) => lang.id === langId);
    }

    public getSupportedLanguageByKey(
        langKey: string
    ): SupportedLanguage | undefined {
        return this.supportedLanguages.find(
            (lang) => lang.key.localeCompare(langKey) === 0
        );
    }

    public getDefaultLanguage(): SupportedLanguage | undefined {
        return this.getSupportedLanguageByKey(this.languageCode);
    }
}
