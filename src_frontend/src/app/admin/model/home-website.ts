import {
    HomeWebsiteStatus,
    HomeWebsiteStatusType,
} from "./home-website-status";
import { Language, ILanguageRaw } from "./language";

export interface IHomeWebsiteRaw {
    id: number;
    language: number;
    modified_date: string;
    status: HomeWebsiteStatusType;
    url: string;
    version: string;
}

export class HomeWebsite {
    readonly id: number;
    readonly language: Language;
    readonly modifiedDate: string;
    readonly status: HomeWebsiteStatusType;
    readonly url: string;
    readonly version: string;

    constructor(homeWebsiteRaw: IHomeWebsiteRaw) {
        if (!homeWebsiteRaw) {
            throw new Error("Home website data is required");
        }
        this.id = homeWebsiteRaw.id;
        this.modifiedDate = homeWebsiteRaw.modified_date;
        this.status = homeWebsiteRaw.status;
        this.url = homeWebsiteRaw.url;
        this.version = homeWebsiteRaw.version;

        // Create a minimal ILanguageRaw with required properties
        const languageRaw: ILanguageRaw = {
            id: homeWebsiteRaw.language,
            lang_key: "", // These will be populated by the Language service
            lang_description: "",
            created_date: "",
            modified_date: "",
        };
        this.language = new Language(languageRaw);
    }

    get displayPreviewButtons(): boolean {
        return this.status === HomeWebsiteStatus.SERVING;
    }

    get displayUploadButton(): boolean {
        return this.status !== HomeWebsiteStatus.IN_PROGRESS;
    }

    get previewHomePageUrl(): string {
        return `/home/from/${this.language.key}_${this.version}`;
    }
}
