import { ILanguageRaw } from "../../common/model/language";
import { Language } from "./language";
import { HomeWebsite, IHomeWebsiteRaw } from "./home-website";

export interface IHomeWebsitesWithLanguageRaw {
    language: ILanguageRaw;
    websites: IHomeWebsiteRaw[];
}

export class HomeWebsitesWithLanguage {
    readonly language: Language;
    readonly websites: HomeWebsite[];

    constructor(homeWebsitesWithLanguageRaw: IHomeWebsitesWithLanguageRaw) {
        if (!homeWebsitesWithLanguageRaw) {
            throw new Error("Home websites with language data is required");
        }
        this.language = new Language(homeWebsitesWithLanguageRaw.language);

        // Create websites with the correct language
        this.websites = homeWebsitesWithLanguageRaw.websites.map((website) => {
            const websiteWithLanguage: IHomeWebsiteRaw = {
                ...website,
                language: this.language.id
            };
            return new HomeWebsite(websiteWithLanguage);
        });
        this.websites.sort((a, b) => a.version.localeCompare(b.version));
    }
}
