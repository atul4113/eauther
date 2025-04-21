import { Injectable } from "@angular/core";
import { HttpClient, HttpResponse } from "@angular/common/http";
import { Observable, of } from "rxjs";
import { map, share, catchError } from "rxjs/operators";
import { throwError } from "rxjs";

interface TokenResponse {
    access: string;
    refresh: string;
}

const API_URL: string = "/api/v2";
const TOKEN_URL: string = "/jwt/session_token";

@Injectable()
export class TokenService {
    private token: string | null = null;
    private refreshToken: string | null = null;
    private observe: Observable<string | null> | null = null;

    constructor(private readonly _http: HttpClient) {}

    private extractData(res: TokenResponse): string {
        if (!res?.access) {
            throw new Error("No access token in response");
        }
        this.refreshToken = res.refresh;
        return res.access;
    }

    private handleError(error: unknown): Observable<null> {
        if (
            error &&
            typeof error === "object" &&
            "status" in error &&
            typeof (error as { status: number }).status === "number" &&
            (error as { status: number }).status === 400
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
                    map(this.extractData.bind(this)),
                    catchError(this.handleError),
                    share()
                );

            this.observe.subscribe({
                next: (token) => (this.token = token),
                error: () => {
                    this.token = null;
                    this.refreshToken = null;
                },
            });

            return this.observe;
        }
    }

    public clear(): void {
        this.token = null;
        this.refreshToken = null;
        this.observe = null;
    }

    public getFreshToken(): Observable<string | null> {
        this.clear();
        return this.get();
    }

    public getRefreshToken(): string | null {
        return this.refreshToken;
    }

    public setTokens(accessToken: string, refreshToken: string): void {
        this.token = accessToken;
        this.refreshToken = refreshToken;
        this.observe = null;
    }
}
