import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { map } from "rxjs/operators";

import { GlobalSettings } from "../model/global-settings";
import { RestClientService } from '../../common/service';

const GLOBAL_SETTINGS_URL = '/global_settings';


@Injectable()
export class GlobalSettingsService {
    constructor (private _restClient: RestClientService) {}

    public get (): Observable<GlobalSettings> {
        return this._restClient.get(GLOBAL_SETTINGS_URL).pipe(
            map(settings => new GlobalSettings(settings))
        );
    }

    public update (globalSettings: GlobalSettings): Observable<any> {
        return this._restClient.put(GLOBAL_SETTINGS_URL, globalSettings);
    }
}
