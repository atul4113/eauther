import { Injectable } from "@angular/core";
import { HttpClient, HttpResponse } from "@angular/common/http";
import { Observable, of } from "rxjs";
import { map, share, catchError } from "rxjs/operators";
import { throwError } from "rxjs";

interface TokenResponse {
    token: string;
}

const API_URL: string = "/api/v2";
const TOKEN_URL: string = "/jwt/session_token";

@Injectable()
export class TokenService {
    private token: string | null = null;
    private observe: Observable<string | null> | null = null;

    constructor(private readonly _http: HttpClient) {}

    private extractData(res: TokenResponse): string {
        if (!res?.token) {
            throw new Error("No token in response");
        }
        return res.token;
    }

    private handleError(error: any): Observable<null> {
        if (
            error &&
            typeof error === "object" &&
            "status" in error &&
            error.status === 400
        ) {
            return of(null);
        } else {
            const errMsg =
                error instanceof Error ? error.message : "Server error";
            console.error("TokenService ERROR: ", errMsg);
            return throwError(() => errMsg);
        }
    }

    public get(): Observable<string | null> {
        if (this.token !== null) {
            return of(this.token);
        } else if (this.observe) {
            return this.observe;
        } else {
            this.observe = this._http
                .get<TokenResponse>(API_URL + TOKEN_URL)
                .pipe(
                    map(this.extractData),
                    catchError(this.handleError),
                    share()
                );

            this.observe.subscribe({
                next: (token) => (this.token = token),
                error: () => (this.token = null),
            });

            return this.observe;
        }
    }

    public clear(): void {
        this.token = null;
        this.observe = null;
    }

    public getFreshToken(): Observable<string | null> {
        this.clear();
        return this.get();
    }
}
