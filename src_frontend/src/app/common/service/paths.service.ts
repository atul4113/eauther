import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { Observable } from 'rxjs/Observable';
import { Observer } from 'rxjs/Observer';
import { share, map } from 'rxjs/operators';

let URLS = {
    HOME:        ['/home'],
    PROJECT: ['/corporate/list'],
    DASHBOARD:     ['/corporate'],
    MY_LESSONS: ['/mycontent']

};

declare let window: any;

@Injectable()
export class PathsService {
    private previousPath: string;
    private currentPath: string;
    private pathsObservable: Observable<string>;
    private pathsObserver: Observer<string>;

    constructor (
        private _router: Router
    ) {
        this.pathsObservable = Observable.create((observer: Observer<string>) => {
            this.pathsObserver = observer;
            this._router.events.subscribe((event: any) => {
                    if (event.url && event.url !== this.currentPath) {
                        this.previousPath = this.currentPath;
                        this.currentPath = event.url;
                        observer.next(this.currentPath);
                    }
                }
            );
        }).pipe(
            share()
        );
    }

    public getActiveSection (path: string): string {
        for (let section in URLS) {
            let sectionUrls = URLS[section];
            for (let url in sectionUrls) {
                let sectionUrl = sectionUrls[url];
                if (path.indexOf(sectionUrl) === 0) {
                    return section;
                }
            }
        }
        return path === '/' ? 'HOME' : null;
    }

    public getPreviousPath (): string {
        return this.previousPath;
    }

    public getCurrentPath (): string {
        return this.currentPath || window.location.pathname;
    }

    public onChange (): Observable<string> {
        return this.pathsObservable;
    }

    public onActiveSectionChange (): Observable<string> {
        return this.pathsObservable.pipe(
            map(path => this.getActiveSection(path))
        );
    }

    public getParameterByName (name: string, url?: string): string {
      if (!url) url = window.location.href;
      name = name.replace(/[\[\]]/g, "\\$&");
      let regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
          results = regex.exec(url);
      if (!results) return null;
      if (!results[2]) return '';
      return decodeURIComponent(results[2].replace(/\+/g, " "));
    }

    public encodeNextUrl (url: string): string {
        let slashesRegExp = new RegExp('/', 'g');
        let semicolonRegExp = new RegExp(';', 'g');
        let slashCoded = '~';
        let semicolonCoded = '|';

        return url.replace(slashesRegExp, slashCoded).replace(semicolonRegExp, semicolonCoded);
    }

    public decodeNextUrl (url: string): string {
        if (url) {
            let slashCodedRegExp = new RegExp('~', 'g');
            let semicolonCodedRegExp = /\|/g;
            let slash = '/';
            let semicolon = ';';
            let nextSeparator = '~next~';

            let firstIndex = url.indexOf(nextSeparator);

            if (firstIndex > -1) {
                let decodedUrl = url.substring(0, firstIndex + nextSeparator.length);
                decodedUrl = decodedUrl.replace(slashCodedRegExp, slash).replace(semicolonCodedRegExp, semicolon);
                let nextUrl = url.substring(firstIndex + nextSeparator.length);

                return decodedUrl + nextUrl;
            } else {
                return url.replace(slashCodedRegExp, slash).replace(semicolonCodedRegExp, semicolon);
            }
        } else {
            return null;
        }

    }
}
