import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable, Observer } from 'rxjs';
import { AuthUserService } from "../service/auth-user.service";


@Injectable()
export class AuthGuard implements CanActivate {

  constructor (
      private _authService: AuthUserService,
      private _router: Router
  ) {}

  canActivate (next:  ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    return Observable.create( (observer: Observer<boolean>) => {
        this._authService.get().subscribe(user => {//TODO use get method after new API is ready
            if (user.isAuthenticated) {
                observer.next(true);
                observer.complete();
            } else {
                observer.next(false);
                observer.complete();
                this._router.navigateByUrl('/accounts/login?next=' + state.url);
            }
        });
    });
  }
}