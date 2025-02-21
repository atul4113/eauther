import { HomeWebsiteStatus } from "./home-website-status";
import { Language } from "./language";

export interface IHomeWebsiteRaw {
    id: number;
    language: number;
    modified_date: string;
    status: string;
    url: string;
    version: string;
}

export class HomeWebsite {
    id: number;
    language: Language;
    modifiedDate: string;
    status: string;
    url: string;
    version: string;

    constructor (homeWebsiteRaw: IHomeWebsiteRaw) {
        this.id = homeWebsiteRaw.id;
        this.modifiedDate = homeWebsiteRaw.modified_date;
        this.status = homeWebsiteRaw.status;
        this.url = homeWebsiteRaw.url;
        this.version = homeWebsiteRaw.version;
    }

    get displayPreviewButtons (): boolean {
        return this.status === HomeWebsiteStatus.SERVING;
    }

    get displayUploadButton (): boolean {
        return this.status !== HomeWebsiteStatus.IN_PROGRESS;
    }

    get previewHomePageUrl (): string {
        return `/home/from/${this.language.key}_${this.version}`;
    }
}
