import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';

import { ITranslations } from "../../common/model/translations";
import { TranslationsService } from "../../common/service";
import { InfoMessageService } from "../../common/service/info-message.service";
import { GlobalSettingsService } from 'app/admin/service/global-settings.service';
import { GlobalSettings } from "../model/global-settings";
import { UtilsService } from "../../common/service/utils.service";


@Component({
    templateUrl: '../templates/global-settings.component.html',
    providers: [GlobalSettingsService]
})
export class GlobalSettingsComponent implements OnInit {
    public translations: ITranslations;
    public isInitialized = false;

    public globalSettings: GlobalSettings;

    public referrersStringIsValid: boolean;
    private _referrersString: string;

    constructor(
        private _translations: TranslationsService,
        private _globalSettings: GlobalSettingsService,
        private _utils: UtilsService,
        private _infoMessage: InfoMessageService,
    ) {}

    ngOnInit() {
        Observable.forkJoin(
            this._translations.getTranslations(),
            this._globalSettings.get(),
        ).subscribe(([translations, globalSettings]) => {
            this.translations = translations;
            this.globalSettings = globalSettings;
            this.referrersString = JSON.stringify(this.globalSettings.referrers, null, 4);
            this.isInitialized = true;
        });
    }

    public submit () {
        this.globalSettings.referrers = JSON.parse(this.referrersString);
        this._globalSettings.update(this.globalSettings).subscribe(
            () => {
                this._infoMessage.addSuccess(this.translations['plain.admin.panel.global_settings.save_ok']);
            },
            () => {
                this._infoMessage.addError(this.translations['plain.admin.panel.global_settings.save_not_ok']);
            }
        );
    }

    public isFormValid () {
        return this.referrersStringIsValid;
    }

    public get referrersString () {
        return this._referrersString;
    }

    public set referrersString (_referrersString: string) {
        this._referrersString = _referrersString;
        this.referrersStringIsValid = this._utils.isJsonValid(_referrersString);
    }

}
