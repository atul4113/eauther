import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { map } from "rxjs/operators";

import { HomeWebsitesWithLanguage, IHomeWebsitesWithLanguageRaw } from "../model/home-websites-with-language";
import { RestClientService } from '../../common/service';
import { HomeWebsite } from "../model/home-website";
import { FileData } from "../../common/model/upload-file";


const HOME_WEBSITES_URL = '/home_websites';

@Injectable()
export class HomeWebsitesService {
    constructor (private _restClient: RestClientService) {}

    public getHomeWebsitesWithLanguages (): Observable<HomeWebsitesWithLanguage[]> {
        return this._restClient.get(HOME_WEBSITES_URL).pipe(
            map(this.mapHomeWebsitesForLanguage)
        );
    }

    public updateHomeWebsite (homeWebsite: HomeWebsite, fileData: FileData) {
        return this._restClient.put(HOME_WEBSITES_URL, {
            website: homeWebsite.id,
            uploaded_file: fileData.fileId
        });
    }

    private mapHomeWebsitesForLanguage (homeWebsitesForLanguageRaw: IHomeWebsitesWithLanguageRaw[]): HomeWebsitesWithLanguage[] {
        return homeWebsitesForLanguageRaw.map(hwfl => new HomeWebsitesWithLanguage(hwfl));
    }
}
