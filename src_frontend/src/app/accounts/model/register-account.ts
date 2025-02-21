export const ACCOUNT_REQUIRED_FIELDS = ['username', 'password', 'passwordAgain', 'accountEmail', 'accountEmailConfirmed'];
export const ADULT_REQUIRED_FIELDS = ['adultEmail', 'adultFirstname', 'adultLastname'];
export const REGULATION_REQUIRED_FIELDS = ['regulationAgreementInfo', 'regulationInformationInfo', 'regulationMarketing'];

export class RegisterAccount {
    public username: string;
    public password: string;
    public passwordAgain: string;
    public accountEmail: string;
    public accountEmailConfirmed: string;
    public regulationAgreementInfo = false;
}

export class RawRegisterAccount {
    public username: string;
    public password1: string;
    public password2: string;
    public email: string;
    public email_confirmed: string;
    public regulation_agreement: boolean; // "true"

    constructor (account: RegisterAccount) {
        this.username = account.username;
        this.password1 = account.password;
        this.password2 = account.passwordAgain;
        this.email = account.accountEmail;
        this.email_confirmed = account.accountEmailConfirmed;
        this.regulation_agreement = account.regulationAgreementInfo;
    }

}
