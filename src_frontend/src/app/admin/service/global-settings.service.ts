import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { map } from "rxjs/operators";

import { GlobalSettings, IGlobalSettingsRaw } from "../model/global-settings";
import { RestClientService } from "../../common/service";

const GLOBAL_SETTINGS_URL = "/global_settings";

@Injectable()
export class GlobalSettingsService {
    constructor(private readonly _restClient: RestClientService) {}

    public get(): Observable<GlobalSettings> {
        return this._restClient
            .get<IGlobalSettingsRaw>(GLOBAL_SETTINGS_URL)
            .pipe(map((settings) => new GlobalSettings(settings)));
    }

    public update(globalSettings: GlobalSettings): Observable<void> {
        return this._restClient.put<void>(GLOBAL_SETTINGS_URL, globalSettings);
    }
}
