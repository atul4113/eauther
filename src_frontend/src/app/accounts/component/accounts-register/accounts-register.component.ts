import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { ITranslations } from "../../../common/model/translations";
import { RegisterAccount, ACCOUNT_REQUIRED_FIELDS } from '../../model/register-account';
import { InfoMessageService, TranslationsService } from '../../../common/service';
import { AccountsService } from '../../service/accounts.service';

declare let document: any;

@Component({
    templateUrl: './accounts-register.component.html',
    providers: [AccountsService]
})
export class AccountsRegisterComponent implements OnInit {
    private DEFAULT_REDIRECT_URL = '/register';
    public registerAccount = new RegisterAccount();
    public previousPath: string = this.DEFAULT_REDIRECT_URL;
    public error = false;
    public errors = [];
    public isUsernameServerError = false;
    public isEmailServerError = false;
    public isEmailConfirmedServerError = false;
    public isSSORegistration = false;
    public registerIsClicked = false;
    public translations!: ITranslations;

    public formValid = {
        username: true,
        password: true,
        passwordAgain: true,
        accountEmail: true,
        accountEmailConfirmed: true,
        regulationAgreementInfo: true
    };

    public static scrollTopMain () {
        document.body.scrollTop = 0;
    }

    constructor (
        private _accounts: AccountsService,
        private _infoMessage: InfoMessageService,
        private _router: Router,
        private _translations: TranslationsService
    ) {}

    ngOnInit () {
        this._translations.getTranslations().subscribe(t => {
            this.translations = t ?? {} as ITranslations;
        });
    }

    public checkPasswords () {
        if (this.registerAccount.password !== undefined && this.registerAccount.passwordAgain !== undefined &&
            this.registerAccount.password.localeCompare('') !== 0 && this.registerAccount.passwordAgain.localeCompare('') !== 0) {
            this.formValid.passwordAgain = this.registerAccount.password.localeCompare(this.registerAccount.passwordAgain) === 0;
        }
    }

    public checkEmails () {
        if (this.registerAccount.accountEmail !== undefined && this.registerAccount.accountEmailConfirmed !== undefined &&
            this.registerAccount.accountEmail.localeCompare('') !== 0 &&
            this.registerAccount.accountEmailConfirmed.localeCompare('') !== 0) {
            this.formValid.accountEmailConfirmed =
                this.registerAccount.accountEmail.localeCompare(this.registerAccount.accountEmailConfirmed) === 0;
        }
    }

    public checkAccountFields () {
        for (let i = 0; i < ACCOUNT_REQUIRED_FIELDS.length; i++) {
            this.formValid[ACCOUNT_REQUIRED_FIELDS[i]] = !!this.registerAccount[ACCOUNT_REQUIRED_FIELDS[i]];
        }
    }

    public checkRequiredFields () {
        this.checkAccountFields();
    }

    public isFormValid () {
        for (const field in this.formValid) {
            if (!this.formValid[field]) {
                return false;
            }
        }

        return true;
    }

    public invalidFormMessage () {
        this._infoMessage.addError('Form is invalid. Please check errors');
    }

    public checkServerError (obj: any) {
        this.isEmailServerError = false;
        this.isEmailConfirmedServerError = false;
        this.isUsernameServerError = false;
        this.formValid.accountEmail = true;
        this.formValid.accountEmailConfirmed = true;
        this.formValid.username = true;

        this.checkPasswords();
        this.checkEmails();

        for (const key in obj) {
            if (key === 'email') {
                this.formValid.accountEmail = false;
                this.isEmailServerError = true;
            } else if (key === 'email_confirmed') {
                this.formValid.accountEmailConfirmed = false;
                this.isEmailConfirmedServerError = true;
            } else if (key === 'username') {
                this.formValid.username = false;
                this.isUsernameServerError = true;
            }
        }
    }

    public register () {
        this.checkRequiredFields();
        this.checkPasswords();
        this.checkEmails();

        if (this.isFormValid()) {
            this._accounts.register(this.registerAccount).subscribe(data => {
                console.log('CORRECT');
                this._router.navigateByUrl('/accounts/register/finish');
            }, error => {
                console.log('ERROR');
                console.log(error);
                this.checkServerError(error.body);
                AccountsRegisterComponent.scrollTopMain();
                this.invalidFormMessage();
                this.registerIsClicked = false;
            });
        } else {
            this.invalidFormMessage();
        }
    }

 }
