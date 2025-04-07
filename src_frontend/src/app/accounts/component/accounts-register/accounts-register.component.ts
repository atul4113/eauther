import { Component, OnInit } from "@angular/core";
import { Router } from "@angular/router";

import { ITranslations } from "../../../common/model/translations";
import {
    RegisterAccount,
    ACCOUNT_REQUIRED_FIELDS,
} from "../../model/register-account";
import {
    InfoMessageService,
    TranslationsService,
} from "../../../common/service";
import { AccountsService } from "../../service/accounts.service";

declare let document: any;

@Component({
    templateUrl: "./accounts-register.component.html",
    providers: [AccountsService],
})
export class AccountsRegisterComponent implements OnInit {
    private DEFAULT_REDIRECT_URL = "/register";
    public registerAccount = new RegisterAccount();
    public previousPath: string = this.DEFAULT_REDIRECT_URL;
    public error = false;
    public errors: string[] = [];
    public isUsernameServerError = false;
    public isEmailServerError = false;
    public isEmailConfirmedServerError = false;
    public isSSORegistration = false;
    public registerIsClicked = false;
    public translations: ITranslations | null = null;

    public get usernameErrorText(): string {
        if (this.isUsernameServerError) {
            return (
                this.errors.find((error) => error.includes("username")) || ""
            );
        }
        return "";
    }

    public formValid = {
        username: true,
        password: true,
        passwordAgain: true,
        accountEmail: true,
        accountEmailConfirmed: true,
        regulationAgreementInfo: true,
    };

    public static scrollTopMain(): void {
        document.body.scrollTop = 0;
    }

    constructor(
        private _accounts: AccountsService,
        private _infoMessage: InfoMessageService,
        private _router: Router,
        private _translations: TranslationsService
    ) {}

    ngOnInit(): void {
        this._translations.getTranslations().subscribe((t) => {
            if (t) {
                this.translations = t;
            }
        });
    }

    public checkPasswords(): boolean {
        if (!this.registerAccount) return false;
        return (
            this.registerAccount.password === this.registerAccount.passwordAgain
        );
    }

    public checkEmails(): boolean {
        if (!this.registerAccount) return false;
        return (
            this.registerAccount.accountEmail ===
            this.registerAccount.accountEmailConfirmed
        );
    }

    public checkAccountFields(): boolean {
        if (!this.registerAccount) return false;
        return (
            this.registerAccount.username.length > 0 &&
            this.registerAccount.password.length > 0 &&
            this.registerAccount.passwordAgain.length > 0 &&
            this.registerAccount.accountEmail.length > 0 &&
            this.registerAccount.accountEmailConfirmed.length > 0
        );
    }

    public checkRequiredFields(): boolean {
        if (!this.registerAccount) return false;
        return ACCOUNT_REQUIRED_FIELDS.every((field) => {
            const value = this.registerAccount[field as keyof RegisterAccount];
            return value !== undefined && value !== null && value !== "";
        });
    }

    public isFormValid(): boolean {
        return (
            this.checkPasswords() &&
            this.checkEmails() &&
            this.checkRequiredFields() &&
            this.registerAccount.regulationAgreementInfo
        );
    }

    public invalidFormMessage(): string {
        if (!this.translations) return "";
        return (
            this.translations.accounts?.register?.form?.invalid ||
            "Please check the form for errors."
        );
    }

    public checkServerError(obj: any): void {
        if (!obj) return;

        this.isUsernameServerError = obj.username !== undefined;
        this.isEmailServerError = obj.email !== undefined;
        this.isEmailConfirmedServerError = obj.email_confirmed !== undefined;

        if (obj.username) {
            this.errors.push(obj.username);
        }
        if (obj.email) {
            this.errors.push(obj.email);
        }
        if (obj.email_confirmed) {
            this.errors.push(obj.email_confirmed);
        }
        if (obj.password1) {
            this.errors.push(obj.password1);
        }
        if (obj.password2) {
            this.errors.push(obj.password2);
        }
        if (obj.non_field_errors) {
            this.errors.push(obj.non_field_errors);
        }
    }

    public register(): void {
        if (!this.registerAccount) return;

        this.registerIsClicked = true;
        this.error = false;
        this.errors = [];

        if (this.isFormValid()) {
            this._accounts.register(this.registerAccount).subscribe(
                () => {
                    this._infoMessage.addSuccess(
                        this.translations?.accounts?.register?.success ||
                            "Registration successful!"
                    );
                    this._router.navigate(["/login"]);
                },
                (error) => {
                    this.error = true;
                    this.checkServerError(error);
                }
            );
        }
    }
}
