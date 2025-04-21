import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { RestClientService } from "../../common/service/rest-client.service";
import { map, tap } from "rxjs/operators";
import { TokenService } from "../../common/service/token.service";

import { RegisterAccount, RawRegisterAccount } from "../model/register-account";

const ACCOUNT_REGISTER_URL = "/register";
const ACCOUNTS_ACTIVATE_URL = "/register/activate";

interface LoginResponse {
    access: string;
    refresh: string;
}

@Injectable()
export class AccountsService {
    constructor(
        private _restClient: RestClientService,
        private _token: TokenService
    ) {}

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

    public login(
        username: string,
        password: string,
        rememberMe: boolean
    ): Observable<boolean> {
        const data = {
            username: username,
            password: password,
            remember_me: rememberMe,
        };

        return this._restClient
            .postPublic<LoginResponse>("/accounts/login/session", data)
            .pipe(
                tap((response) => {
                    // Store tokens
                    this._token.setTokens(response.access, response.refresh);
                }),
                map(() => true)
            );
    }
}
