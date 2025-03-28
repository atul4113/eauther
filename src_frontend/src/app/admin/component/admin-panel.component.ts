import { Component, OnInit } from '@angular/core';

import { Label } from "../model/label";
import { ITranslations } from "../../common/model/translations";
import { TranslationsService } from "../../common/service";
import { GlobalSettings } from "../model/global-settings";

@Component({
    templateUrl: '../templates/admin-panel.component.html'
})
export class AdminPanelComponent implements OnInit {
    public translations: ITranslations | null = null;
    public isInitialized = true;
    public settings: GlobalSettings | null = null;
    public labels: Label[] = [];

    constructor(
        private _translations: TranslationsService
    ) {}

    ngOnInit(): void {
        this._translations.getTranslations().subscribe(t => {
            if (t) {
                this.translations = t;
            }
        });
    }
}
