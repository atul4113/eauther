import { Injectable } from "@angular/core";
import { Observable } from "rxjs";

import { RegisterAccount, RawRegisterAccount } from "../model/register-account";
import { RestClientService } from "../../common/service";

const ACCOUNT_REGISTER_URL = "/register";
const ACCOUNTS_ACTIVATE_URL = "/register/activate";

@Injectable()
export class AccountsService {
    constructor(private _restClient: RestClientService) {}

    public register(account: RegisterAccount): Observable<any> {
        return this._restClient.postPublic(
            ACCOUNT_REGISTER_URL,
            new RawRegisterAccount(account)
        );
    }

    public activate(key: string): Observable<any> {
        return this._restClient.postPublic(ACCOUNTS_ACTIVATE_URL, {
            activation_key: key,
        });
    }
}
