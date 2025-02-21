import { Component, OnInit } from '@angular/core';

import { Label } from "../model/label";
import { ITranslations } from "../../common/model/translations";
import { TranslationsService } from "../../common/service";


@Component({
    templateUrl: '../templates/admin-panel.component.html'
})
export class AdminPanelComponent implements OnInit {
    public translations: ITranslations;
    public isInitialized = true;
    public settings = null;
    public labels: Label[] = [];

    constructor(
        private _translations: TranslationsService
    ) {}

    ngOnInit() {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }
}
