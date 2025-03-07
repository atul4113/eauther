import { Injectable } from "@angular/core";
import { Http, Response } from "@angular/http";
import { Observable } from "rxjs";
import { map, share, catchError } from "rxjs/operators";
import "rxjs/add/observable/of";
import "rxjs/add/observable/throw";

const API_URL: string = "/api/v2";
const TOKEN_URL: string = "/jwt/session_token";

@Injectable()
export class TokenService {
    private token: string;
    private observe: Observable<string>;

    constructor(private _http: Http) {}

    private extractData(res: Response): string {
        if (res.status < 200 || res.status >= 300) {
            throw new Error("BAD RESPONSE STATUS: " + res.status);
        }
        let body = res.json();
        return <string>body.token;
    }

    private handleError(error: any) {
        if (error.status === 400) {
            return Observable.of(null);
        } else {
            let errMsg = error.message || "Server error";
            console.error("TokenService ERROR: ", errMsg);
            return Observable.throw(errMsg);
        }
    }

    public get() {
        if (this.token !== undefined) {
            return Observable.of(this.token);
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
