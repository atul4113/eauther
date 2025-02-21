import { Component, OnInit } from '@angular/core';

import { ITranslations } from "../../common/model";
import { TranslationsService, InfoMessageService } from "../../common/service";


@Component({
    templateUrl: '../templates/translations-panel.component.html'
})
export class TranslationsPanelComponent implements OnInit {
    public translations: ITranslations;
    public isInitialized = true;
    public settings = null;


    constructor(
        private _translations: TranslationsService,
        private _infoMessage: InfoMessageService
    ) {}

    ngOnInit() {
        this._translations.getTranslations().subscribe(translations => {
                this.translations = translations;
                this.isInitialized = true;
            },
            (reason) => { // error
                console.warn(reason);
                this._infoMessage.error404();
            });

    }
}
