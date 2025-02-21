import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable, Observer } from 'rxjs';
import { AuthUserService } from "../service/auth-user.service";
import {PathsService} from "../service";


@Injectable()
export class OnlyNoAuthGuard implements CanActivate {

  constructor (
      private _authService: AuthUserService,
      private _paths: PathsService,
      private _router: Router
  ) {}

  canActivate (next:  ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    return Observable.create( (observer: Observer<boolean>) => {
        this._authService.get().subscribe(user => {//TODO use get method after new API is ready
            if (!user.isAuthenticated) {
                observer.next(true);
                observer.complete();
            } else {
                observer.next(false);
                observer.complete();
                let next = this._paths.getParameterByName('next');
                if (next) {
                    window.location.href = window.location.protocol+ '//' + window.location.host + next;
                } else {
                    this._router.navigateByUrl('home');
                }
            }
        });
    });
  }
}
