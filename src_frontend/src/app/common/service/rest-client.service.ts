import { Injectable } from "@angular/core";
import {
    HttpClient,
    HttpHeaders,
    HttpErrorResponse,
} from "@angular/common/http";
import { Observable, throwError } from "rxjs";
import { catchError, map, switchMap } from "rxjs/operators";

import { TokenService } from "./token.service";
import { InfoMessageService } from "./info-message.service";

const API_URL = "/api/v2";
export const UNAUTHORIZED_ERROR = "Unauthorized";

const SERVER_RESPONSE_STATUS = {
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    INTERNAL_SERVER_ERROR: 500,
};

@Injectable({ providedIn: "root" })
export class RestClientService {
    constructor(
        private _http: HttpClient,
        private _token: TokenService,
        private _infoMessage: InfoMessageService
    ) {}

    public get(url: string): Observable<any> {
        return this.requestWithToken("GET", url);
    }

    public getPublic(url: string): Observable<any> {
        return this._http
            .get(API_URL + url, { headers: this.getHeaders() })
            .pipe(map(this.extractData), catchError(this.handleError));
    }

    public post(url: string, params: any = {}): Observable<any> {
        return this.requestWithToken("POST", url, params);
    }

    public postPublic(url: string, params: any): Observable<any> {
        return this._http
            .post(API_URL + url, params, { headers: this.getHeaders() })
            .pipe(map(this.extractData), catchError(this.handleError));
    }

    public put(url: string, params: any): Observable<any> {
        return this.requestWithToken("PUT", url, params);
    }

    public putPublic(url: string, params: any = {}): Observable<any> {
        return this._http
            .put(API_URL + url, params, { headers: this.getHeaders() })
            .pipe(map(this.extractData), catchError(this.handleError));
    }

    public delete(url: string): Observable<any> {
        return this.requestWithToken("DELETE", url);
    }

    private extractData(response: any): any {
        return response || {};
    }

    private handleError(error: HttpErrorResponse): Observable<never> {
        console.error("RestClientService ERROR:", error);
        if (error.status === SERVER_RESPONSE_STATUS.INTERNAL_SERVER_ERROR) {
            this._infoMessage.error500();
        }
        return throwError(() => error);
    }

    private getHeaders(): HttpHeaders {
        return new HttpHeaders({
            Accept: "application/json",
            "Content-Type": "application/json",
        });
    }

    private requestWithToken(
        method: string,
        url: string,
        params?: any
    ): Observable<any> {
        return this._token.get().pipe(
            switchMap((token: string) => {
                if (!token) {
                    return throwError(() => new Error(UNAUTHORIZED_ERROR));
                }

                const headers = this.getHeaders().set(
                    "Authorization",
                    `JWT ${token}`
                );
                const options = { headers };

                let request$: Observable<any>;
                switch (method) {
                    case "GET":
                        request$ = this._http.get(API_URL + url, options);
                        break;
                    case "POST":
                        request$ = this._http.post(
                            API_URL + url,
                            params,
                            options
                        );
                        break;
                    case "PUT":
                        request$ = this._http.put(
                            API_URL + url,
                            params,
                            options
                        );
                        break;
                    case "DELETE":
                        request$ = this._http.delete(API_URL + url, options);
                        break;
                    default:
                        return throwError(
                            () => new Error("Invalid request method")
                        );
                }

                return request$.pipe(
                    map(this.extractData),
                    catchError((error) => {
                        if (
                            error.status === SERVER_RESPONSE_STATUS.UNAUTHORIZED
                        ) {
                            this._token.clear();
                        }
                        return this.handleError(error);
                    })
                );
            })
        );
    }
}
