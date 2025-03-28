/**
 * angular2-cookie - Implementation of Angular 1.x $cookies service to Angular 2
 * @version v1.2.5
 * @link https://github.com/salemdar/angular2-cookie#readme
 * @license MIT
 */
import {APP_BASE_HREF} from '@angular/common';
import {Inject, Injectable, Injector, Optional} from '@angular/core';
import {CookieOptionsArgs} from './cookie-options-args.model';

/** @private */
export class CookieOptions {
  path: string;
  domain: string;
  expires: string|Date;
  secure: boolean;

  constructor({path, domain, expires, secure}: CookieOptionsArgs = {}) {
    this.path = path ?? "";
    this.domain = domain ?? "";
    this.expires = expires ?? "";
    this.secure = secure ?? false;
  }

  merge(options?: CookieOptionsArgs): CookieOptions {
    if (!options) {
      return new CookieOptions({
        path: this.path,
        domain: this.domain,
        expires: this.expires,
        secure: this.secure
      });
    }
    return new CookieOptions(<CookieOptionsArgs>{
      path: this.isPresent(options) && this.isPresent(options.path) ? options.path : this.path,
      domain: this.isPresent(options) && this.isPresent(options.domain) ? options.domain :
                                                                          this.domain,
      expires: this.isPresent(options) && this.isPresent(options.expires) ? options.expires :
                                                                            this.expires,
      secure: this.isPresent(options) && this.isPresent(options.secure) ? options.secure :
                                                                          this.secure,
    });
  }

  private isPresent(obj: any): boolean {
    return obj !== undefined && obj !== null;
  }
}

/** @private */
@Injectable()
export class BaseCookieOptions extends CookieOptions {
  constructor(@Optional() @Inject(APP_BASE_HREF) private baseHref: string) {
    super({path: baseHref || '/'});
  }
}
