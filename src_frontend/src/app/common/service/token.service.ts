import { Injectable } from "@angular/core";
import { HttpClient, HttpResponse } from "@angular/common/http";
import { Observable, of } from "rxjs";
import { map, share, catchError } from "rxjs/operators";
import { throwError } from "rxjs";

const API_URL: string = "/api/v2";
const TOKEN_URL: string = "/jwt/session_token";

@Injectable()
export class TokenService {
    private token: string;
    private observe: Observable<string>;

    constructor(private _http: HttpClient) {}

    private extractData(res: HttpResponse<any>): string {
        if (res.status < 200 || res.status >= 300) {
            throw new Error("BAD RESPONSE STATUS: " + res.status);
        }
        let body = res.body;
        return <string>body.token;
    }

    private handleError(error: any) {
        if (error.status === 400) {
            return of(null);
        } else {
            let errMsg = error.message || "Server error";
            console.error("TokenService ERROR: ", errMsg);
            return throwError(errMsg);
        }
    }

    public get() {
        if (this.token !== undefined) {
            return of(this.token);
        } else if (this.observe) {
            return this.observe;
        } else {
            this.observe = this._http
                .get(API_URL + TOKEN_URL)
                .pipe(
                    map(this.extractData),
                    catchError(this.handleError),
                    share()
                );

            this.observe.subscribe(
                (token) => (this.token = token),
                (error) => (this.token = null)
            );

            return this.observe;
        }
    }

    public clear() {
        this.token = undefined;
        this.observe = undefined;
    }

    public getFreshToken() {
        this.clear();
        return this.get();
    }
}
