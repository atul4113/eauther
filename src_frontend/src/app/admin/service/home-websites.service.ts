import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { map } from "rxjs/operators";

import {
    HomeWebsitesWithLanguage,
    IHomeWebsitesWithLanguageRaw,
} from "../model/home-websites-with-language";
import { RestClientService } from "../../common/service";
import { HomeWebsite } from "../model/home-website";
import { FileData } from "../../common/model/upload-file";

const HOME_WEBSITES_URL = "/home_websites";

interface IUpdateHomeWebsiteParams {
    website: number;
    uploaded_file: number;
}

@Injectable()
export class HomeWebsitesService {
    constructor(private readonly _restClient: RestClientService) {}

    public getHomeWebsitesWithLanguages(): Observable<
        HomeWebsitesWithLanguage[]
    > {
        return this._restClient
            .get<IHomeWebsitesWithLanguageRaw[]>(HOME_WEBSITES_URL)
            .pipe(map(this.mapHomeWebsitesForLanguage));
    }

    public updateHomeWebsite(
        homeWebsite: HomeWebsite,
        fileData: FileData
    ): Observable<void> {
        if (!fileData.fileId) {
            throw new Error("File ID is required");
        }

        const params: IUpdateHomeWebsiteParams = {
            website: homeWebsite.id,
            uploaded_file: fileData.fileId,
        };
        return this._restClient.put<void>(HOME_WEBSITES_URL, params);
    }

    private mapHomeWebsitesForLanguage(
        homeWebsitesForLanguageRaw: IHomeWebsitesWithLanguageRaw[]
    ): HomeWebsitesWithLanguage[] {
        return homeWebsitesForLanguageRaw.map(
            (hwfl) => new HomeWebsitesWithLanguage(hwfl)
        );
    }
}
