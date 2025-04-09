import { Injectable } from "@angular/core";
import { Observable, of, map, share } from "rxjs";

import { ISettingsRaw, Settings } from "../model";
import { RestClientService } from "./rest-client.service";
import { environment } from "../../../environments/environment";

// Use the settings endpoint
const SETTINGS_URL = "/settings";

const DEFAULT_SETTINGS: ISettingsRaw = {
    application_id: "",
    email: "",
    lang: "",
    select_user_language: false,
    referrers: {},
    supported_languages: [],
    version: "",
};

@Injectable()
export class SettingsService {
    private settings: Settings | null = null;
    private settingsObservable: Observable<Settings> | null = null;

    constructor(private readonly _restClient: RestClientService) {
        this.load();
    }

    private mapSettings = (response: ISettingsRaw): Settings =>
        new Settings(response);

    private load(): void {
        this.settingsObservable = this._restClient
            .getPublic<ISettingsRaw>(SETTINGS_URL)
            .pipe(map(this.mapSettings), share());

        this.settingsObservable.subscribe({
            next: (settings) => (this.settings = settings),
        });
    }

    public get(): Observable<Settings> {
        if (this.settings !== null) {
            return of(this.settings);
        } else if (this.settingsObservable !== null) {
            return this.settingsObservable;
        } else {
            this.load();
            return (
                this.settingsObservable || of(new Settings(DEFAULT_SETTINGS))
            );
        }
    }
}
