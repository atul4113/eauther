import { Component, OnInit } from '@angular/core';

import { AccountsSettings } from '../../model/accounts-settings';
import { PathsService } from '../../../common/service';
import { ITranslations } from "../../../common/model/translations";
import { AccountsService } from '../../service/accounts.service';
import { TranslationsService } from "../../../common/service";


declare var document: any;

const ACCOUNTS_LOGIN_PATH = '/accounts/login';

@Component({
    templateUrl: './accounts-login.component.html',
    providers: [AccountsService]
})
export class AccountsLoginComponent implements OnInit {
    private DEFAULT_REDIRECT_URL = '/corporate';

    public loginSettings = new AccountsSettings();
    public previousPath: string = this.DEFAULT_REDIRECT_URL;
    public error: boolean = false;
    public rememberMe: boolean = false;
    public translations!: ITranslations;

    constructor (
        private _paths: PathsService,
        private _translations: TranslationsService
    ) {}

    ngOnInit () {
        this._translations.getTranslations().subscribe(t => {
            this.translations = t ?? {} as ITranslations;
        });
        let next = this._paths.getParameterByName('next');
        if (next) {
            this.setPreviousPath(next);
        } else {
            this.setPreviousPath();
            this._paths.onChange().subscribe(() => {
                if (this._paths.getPreviousPath()) {
                    this.error = false;
                }
                this.setPreviousPath();
            });
        }

        if (document.referrer.indexOf(ACCOUNTS_LOGIN_PATH) !== -1) {
            this.error = true;
        }
    }

    private setPreviousPath (next?: string) {
        let previousPath = next ? next : this.DEFAULT_REDIRECT_URL;

        if (!previousPath || previousPath === ACCOUNTS_LOGIN_PATH) {
            previousPath = this.DEFAULT_REDIRECT_URL;
        } else if (previousPath.indexOf('/') !== 0) {
            previousPath = '/' + previousPath;
        }

        this.previousPath = previousPath;
    }
 }
