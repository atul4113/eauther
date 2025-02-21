import { Injectable }    from '@angular/core';
import { CanDeactivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable }    from 'rxjs/Observable';


export interface CanComponentDeactivate {
 canDeactivate: () => boolean | Observable<boolean>;
}


@Injectable()
export class CanDeactivateGuard implements CanDeactivate<CanComponentDeactivate> {
  canDeactivate(component: CanComponentDeactivate, route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean>| boolean {
    return component.canDeactivate ? component.canDeactivate() : true;
  }
}
