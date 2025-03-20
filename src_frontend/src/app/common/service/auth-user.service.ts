import { Injectable } from "@angular/core";
import { Observable, Subject, of } from "rxjs";
import { AuthUser, IAuthUserRaw } from "../model/auth-user";
import { RestClientService } from "./rest-client.service";
import { map, share, catchError, tap } from "rxjs/operators";

const USER_URL = "/user/";

@Injectable()
export class AuthUserService {
    private user: AuthUser | null = null;
    private observe: Observable<AuthUser> | null = null;
    private readonly changeSubject = new Subject<AuthUser>();

    constructor(private readonly _restClient: RestClientService) {
        this.load();
    }

    private mapAuthUser(response: IAuthUserRaw): AuthUser {
        return new AuthUser(response);
    }

    private handleError(error: unknown): Observable<AuthUser> {
        console.error("AuthUserService ERROR:", error);
        return of(new AuthUser());
    }

    public get(): Observable<AuthUser> {
        if (this.user !== null) {
            return of(this.user);
        } else if (this.observe !== null) {
            return this.observe;
        } else {
            this.load();
            return this.observe || of(new AuthUser());
        }
    }

    public onChange(): Observable<AuthUser> {
        return this.changeSubject.asObservable().pipe(share());
    }

    private load(): void {
        this.observe = this._restClient.get<IAuthUserRaw>(USER_URL).pipe(
            map(this.mapAuthUser),
            tap((user) => {
                this.user = user;
                this.changeSubject.next(user);
            }),
            catchError(this.handleError),
            share()
        );

        this.observe.subscribe();
    }
}
