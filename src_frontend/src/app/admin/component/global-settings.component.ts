import { Component, OnInit } from '@angular/core';
import { Observable, forkJoin } from 'rxjs';

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
    public translations: ITranslations | null = null;
    public isInitialized = false;
    public globalSettings: GlobalSettings | null = null;
    public referrersStringIsValid: boolean = false;
    private _referrersString: string = '';

    constructor(
        private _translations: TranslationsService,
        private _globalSettings: GlobalSettingsService,
        private _utils: UtilsService,
        private _infoMessage: InfoMessageService,
    ) {}

    ngOnInit() {
        forkJoin(
            this._translations.getTranslations(),
            this._globalSettings.get(),
        ).subscribe(([translations, globalSettings]: [ITranslations | null, GlobalSettings | null]) => {
            if (translations) {
                this.translations = translations;
            }
            if (globalSettings) {
                this.globalSettings = globalSettings;
                this.referrersString = JSON.stringify(this.globalSettings.referrers, null, 4);
            }
            this.isInitialized = true;
        });
    }

    public submit(): void {
        if (!this.globalSettings) return;
        
        try {
            const referrers = JSON.parse(this.referrersString);
            this.globalSettings = { ...this.globalSettings, referrers };
            this._globalSettings.update(this.globalSettings).subscribe(
                () => {
                    if (this.translations) {
                        this._infoMessage.addSuccess(this.translations.labels['plain.admin.panel.global_settings.save_ok']);
                    }
                },
                () => {
                    if (this.translations) {
                        this._infoMessage.addError(this.translations.labels['plain.admin.panel.global_settings.save_not_ok']);
                    }
                }
            );
        } catch (error) {
            this._infoMessage.addError('Invalid JSON format');
        }
    }

    public isFormValid(): boolean {
        return this.referrersStringIsValid;
    }

    public get referrersString(): string {
        return this._referrersString;
    }

    public set referrersString(value: string) {
        this._referrersString = value;
        this.referrersStringIsValid = this._utils.isJsonValid(value);
    }
}
