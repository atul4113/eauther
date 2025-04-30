import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { map, tap, switchMap } from "rxjs/operators";
import { TokenService } from "../../common/service/token.service";
import { HttpClient } from "@angular/common/http";

import { RegisterAccount, RawRegisterAccount } from "../model/register-account";

const ACCOUNT_REGISTER_URL = "/register";
const ACCOUNTS_ACTIVATE_URL = "/register/activate";
const API_URL = "/api/v2";
const SESSION_TOKEN_URL = API_URL + "/jwt/session_token";

interface LoginResponse {
    access: string;
    refresh: string;
    success?: boolean;
    user?: string;
}

@Injectable()
export class AccountsService {
    constructor(private _token: TokenService, private _http: HttpClient) {}

    public register(account: RegisterAccount): Observable<any> {
        return this._http.post(
            ACCOUNT_REGISTER_URL,
            new RawRegisterAccount(account),
            { withCredentials: true }
        );
    }

    public activate(key: string): Observable<any> {
        return this._http.post(
            ACCOUNTS_ACTIVATE_URL,
            { activation_key: key },
            { withCredentials: true }
        );
    }

    private getSessionToken(): Observable<any> {
        return this._http.get(SESSION_TOKEN_URL, {
            headers: {
                Authorization: `Bearer ${this._token.getToken()}`,
            },
            withCredentials: true,
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

        return this._http
            .post<LoginResponse>("/accounts/login/session", data, {
                withCredentials: true,
            })
            .pipe(
                tap((response) => {
                    if (response.access && response.refresh) {
                        this._token.setTokens(
                            response.access,
                            response.refresh
                        );
                    }
                }),
                switchMap(() => this.getSessionToken()),
                map(() => true)
            );
    }
}
