import { Injectable } from "@angular/core";
import { Observable, Observer } from "rxjs";
import { AuthUser, IAuthUserRaw } from "../model/auth-user";
import { RestClientService } from "./rest-client.service";
import { map, share, catchError } from 'rxjs/operators';
import "rxjs/add/observable/of";

const USER_URL: string = '/user/';

@Injectable()
export class AuthUserService {
    private user: AuthUser;
    private observe: Observable<any>;
    private changeObserve: Observable<AuthUser>;
    private changeObserver: Observer<AuthUser>;

    constructor (private _restClient: RestClientService) {
        this.load();
    }

    private mapAuthUser (response: any) {
        return new AuthUser(<IAuthUserRaw> response);
    }

    private handleError (error: string): Observable<AuthUser> {
        return Observable.of(new AuthUser());
    }


    public get (): Observable<AuthUser> {
        if (this.user) {
            return Observable.of(this.user);
        } else if (this.observe){
            return this.observe;
        } else {
            return null;
        }
    }

    public onChange (): Observable<AuthUser> {
        return this.changeObserve;
    }

    private load () {
        this.observe =
            this._restClient
                .get(USER_URL)
                .pipe(
                    map(this.mapAuthUser),
                    catchError(this.handleError),
                    share()
                );

        this.observe
            .subscribe(user => this.user = user);

        this.changeObserve =
            Observable.create( (observer: Observer<AuthUser>) => {
                this.changeObserver = observer;
            }).pipe(
                share()
            );
    }
}
