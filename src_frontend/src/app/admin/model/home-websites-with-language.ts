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

        this.websites = homeWebsitesWithLanguageRaw.websites.map((website) => {
            const wb = new HomeWebsite(website);
            // @ts-ignore - We know this is safe because we're setting the language from the parent
            wb.language = this.language;
            return wb;
        });
        this.websites.sort((a, b) => a.version.localeCompare(b.version));
    }
}
