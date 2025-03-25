import { Component, OnInit } from '@angular/core';

import { ITranslations } from "../../common/model";
import { TranslationsService, InfoMessageService } from "../../common/service";

@Component({
    templateUrl: '../templates/translations-panel.component.html'
})
export class TranslationsPanelComponent implements OnInit {
    public translations: ITranslations | null = null;
    public isInitialized = true;
    public settings: any = null;

    constructor(
        private _translations: TranslationsService,
        private _infoMessage: InfoMessageService
    ) {}

    ngOnInit(): void {
        this._translations.getTranslations().subscribe(
            translations => {
                this.translations = translations;
                this.isInitialized = true;
            },
            (reason: any) => { // error
                console.warn(reason);
                this._infoMessage.error404();
            }
        );
    }
}
