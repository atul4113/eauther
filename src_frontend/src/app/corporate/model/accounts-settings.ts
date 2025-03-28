export interface IAccountsSettingsRaw {
    sign_in_with_librus_active: boolean;
    sign_in_with_librus_url: string;
    sign_in_with_google_active: boolean;
    sign_in_with_google_url: string;
    sign_in_with_office_active: boolean;
    sign_in_with_office_url: string;
    registration_type: number;
}

export class SSOProviderSettings {
    constructor(
        public isActive: boolean = false,
        public url: string = ""
    ) {}
}

export class AccountsSettings {
    public google: SSOProviderSettings;
    public office: SSOProviderSettings;
    public librus: SSOProviderSettings;
    public registrationType: number;

    constructor (accountsSettings?: IAccountsSettingsRaw) {
        if (accountsSettings) {
            this.google =
                new SSOProviderSettings(
                    accountsSettings.sign_in_with_google_active,
                    accountsSettings.sign_in_with_google_url
                );
            this.office =
                new SSOProviderSettings(
                    accountsSettings.sign_in_with_office_active,
                    accountsSettings.sign_in_with_office_url
                );
            this.librus =
                new SSOProviderSettings(
                    accountsSettings.sign_in_with_librus_active,
                    accountsSettings.sign_in_with_librus_url
                );
            this.registrationType = accountsSettings.registration_type;
        } else {
            this.google = new SSOProviderSettings();
            this.office = new SSOProviderSettings();
            this.librus = new SSOProviderSettings();
            this.registrationType = 0;
        }
    }
}
