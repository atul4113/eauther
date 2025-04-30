import { Component, OnInit } from "@angular/core";
import { Router } from "@angular/router";

import { AccountsSettings } from "../../model/accounts-settings";
import { PathsService } from "../../../common/service";
import { ITranslations } from "../../../common/model/translations";
import { AccountsService } from "../../service/accounts.service";
import { TranslationsService } from "../../../common/service";

declare var document: any;

const ACCOUNTS_LOGIN_PATH = "/accounts/login";

@Component({
    templateUrl: "./accounts-login.component.html",
    providers: [AccountsService],
})
export class AccountsLoginComponent implements OnInit {
    private DEFAULT_REDIRECT_URL = "/corporate";

    public loginSettings = new AccountsSettings();
    public previousPath: string = this.DEFAULT_REDIRECT_URL;
    public error: boolean = false;
    public rememberMe: boolean = false;
    public translations!: ITranslations;
    public username: string = "";
    public password: string = "";

    constructor(
        private _paths: PathsService,
        private _translations: TranslationsService,
        private _accounts: AccountsService,
        private _router: Router
    ) {}

    ngOnInit() {
        this._translations
            .getTranslations()
            .subscribe((t) => (this.translations = t ?? ({} as ITranslations)));

        let next = this._paths.getParameterByName("next");
        if (next) {
            this.setPreviousPath(next);
        } else {
            this.setPreviousPath("/corporate/no_space_info");
        }

        if (document.referrer.indexOf(ACCOUNTS_LOGIN_PATH) !== -1) {
            this.error = true;
        }

        console.log("Test log message");
    }

    public onSubmit() {
        this.error = false;
        this._accounts
            .login(this.username, this.password, this.rememberMe)
            .subscribe({
                next: () => {
                    window.location.href = this.previousPath;
                },
                error: () => {
                    this.error = true;
                },
            });
    }

    private setPreviousPath(next?: string) {
        let previousPath = next ? next : this.DEFAULT_REDIRECT_URL;

        if (!previousPath || previousPath === ACCOUNTS_LOGIN_PATH) {
            previousPath = this.DEFAULT_REDIRECT_URL;
        } else if (previousPath.indexOf("/") !== 0) {
            previousPath = "/" + previousPath;
        }

        this.previousPath = previousPath;
    }
}
