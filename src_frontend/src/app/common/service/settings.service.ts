import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { map, share } from "rxjs/operators";
import "rxjs/add/observable/of";

import { ISettingsRaw, Settings } from "../model";
import { RestClientService } from "./rest-client.service";

const SETTINGS_URL: string = "/settings";

@Injectable()
export class SettingsService {
    private settings: Settings;
    private settingsObservable: Observable<any>;

    constructor(private _restClient: RestClientService) {
        this.load();
    }

    private mapSettings = (response: any) =>
        new Settings(<ISettingsRaw>response);

    private load() {
        this.settingsObservable = this._restClient
            .getPublic(SETTINGS_URL)
            .pipe(map(this.mapSettings), share());

        this.settingsObservable.subscribe(
            (settings) => (this.settings = settings)
        );
    }

    public get(): Observable<Settings> {
        if (this.settings) {
            return Observable.of(this.settings);
        } else if (this.settingsObservable) {
            return this.settingsObservable;
        } else {
            return null;
        }
    }
}
