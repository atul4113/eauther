import { Component, OnInit, OnDestroy } from '@angular/core';

import { ITranslations } from "../../../common/model/translations";
import { AccountsService } from '../../service/accounts.service';
import { TranslationsService } from "../../../common/service";


declare let window: any;
declare let document: any;

@Component({
    templateUrl: './accounts-register-finish.component.html',
    providers: [AccountsService]
})

export class AccountsRegisterFinishComponent implements OnInit, OnDestroy {
    public translations: ITranslations;

    constructor (
        private _translations: TranslationsService
    ) {}

    ngOnInit () {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }

    ngOnDestroy () {}

 }
