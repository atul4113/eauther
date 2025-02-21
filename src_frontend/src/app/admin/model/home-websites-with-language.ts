import { ILanguageRaw } from "../../common/model/language";
import { Language } from "./language";
import { HomeWebsite, IHomeWebsiteRaw } from "./home-website";

export interface IHomeWebsitesWithLanguageRaw {
    language: ILanguageRaw;
    websites: IHomeWebsiteRaw[];
}

export class HomeWebsitesWithLanguage {
    public language: Language;
    public websites: HomeWebsite[];

    constructor (homeWebsitesWithLanguageRaw: IHomeWebsitesWithLanguageRaw) {
        this.language = new Language(homeWebsitesWithLanguageRaw.language);

        this.websites = homeWebsitesWithLanguageRaw.websites.map(
            website => {
                let wb = new HomeWebsite(website);
                wb.language = this.language;
                return wb;
            }
        );
        this.websites.sort((a, b) => a.version.localeCompare(b.version));
    }
}
