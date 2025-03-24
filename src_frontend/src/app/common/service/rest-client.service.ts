import { Injectable } from "@angular/core";
import {
    HttpClient,
    HttpHeaders,
    HttpErrorResponse,
    HttpResponse,
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
} as const;

type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";

@Injectable({ providedIn: "root" })
export class RestClientService {
    constructor(
        private readonly _http: HttpClient,
        private readonly _token: TokenService,
        private readonly _infoMessage: InfoMessageService
    ) {}

    public get<T>(url: string): Observable<T> {
        return this.requestWithToken<T>("GET", url);
    }

    public getPublic<T>(url: string): Observable<T> {
        return this._http
            .get<T>(API_URL + url, { headers: this.getHeaders() })
            .pipe(map(this.extractData), catchError(this.handleError));
    }

    public post<T>(url: string, params: unknown = {}): Observable<T> {
        return this.requestWithToken<T>("POST", url, params);
    }

    public postPublic<T>(url: string, params: unknown): Observable<T> {
        return this._http
            .post<T>(API_URL + url, params, { headers: this.getHeaders() })
            .pipe(map(this.extractData), catchError(this.handleError));
    }

    public put<T>(url: string, params: unknown): Observable<T> {
        return this.requestWithToken<T>("PUT", url, params);
    }

    public putPublic<T>(url: string, params: unknown = {}): Observable<T> {
        return this._http
            .put<T>(API_URL + url, params, { headers: this.getHeaders() })
            .pipe(map(this.extractData), catchError(this.handleError));
    }

    public delete<T>(url: string): Observable<T> {
        return this.requestWithToken<T>("DELETE", url);
    }

    private extractData<T>(response: T): T {
        return response || ({} as T);
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

    private requestWithToken<T>(
        method: HttpMethod,
        url: string,
        params?: unknown
    ): Observable<T> {
        return this._token.get().pipe(
            switchMap((token: string | null) => {
                if (!token) {
                    return throwError(() => new Error(UNAUTHORIZED_ERROR));
                }

                const headers = this.getHeaders().set(
                    "Authorization",
                    `JWT ${token}`
                );
                const options = { headers };

                let request$: Observable<T>;
                switch (method) {
                    case "GET":
                        request$ = this._http.get<T>(API_URL + url, options);
                        break;
                    case "POST":
                        request$ = this._http.post<T>(
                            API_URL + url,
                            params,
                            options
                        );
                        break;
                    case "PUT":
                        request$ = this._http.put<T>(
                            API_URL + url,
                            params,
                            options
                        );
                        break;
                    case "DELETE":
                        request$ = this._http.delete<T>(API_URL + url, options);
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
