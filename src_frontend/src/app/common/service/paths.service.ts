import { Injectable } from "@angular/core";
import { Router, NavigationEnd } from "@angular/router";
import { Observable, Subject } from "rxjs";
import { share, map } from "rxjs/operators";

interface Urls {
    [key: string]: string[];
}

const URLS: Urls = {
    HOME: ["/home"],
    PROJECT: ["/corporate/list"],
    DASHBOARD: ["/corporate"],
    MY_LESSONS: ["/mycontent"],
};

type Section = keyof typeof URLS;

@Injectable()
export class PathsService {
    private previousPath: string | null = null;
    private currentPath: string | null = null;
    private readonly pathsSubject = new Subject<string>();

    constructor(private readonly _router: Router) {
        this._router.events.subscribe((event) => {
            if (
                event instanceof NavigationEnd &&
                event.url !== this.currentPath
            ) {
                this.previousPath = this.currentPath;
                this.currentPath = event.url;
                this.pathsSubject.next(this.currentPath);
            }
        });
    }

    public getActiveSection(path: string): Section | null {
        for (const [section, sectionUrls] of Object.entries(URLS)) {
            for (const sectionUrl of sectionUrls) {
                if (path.startsWith(sectionUrl)) {
                    return section as Section;
                }
            }
        }
        return path === "/" ? "HOME" : null;
    }

    public getPreviousPath(): string | null {
        return this.previousPath;
    }

    public getCurrentPath(): string {
        return this.currentPath || window.location.pathname;
    }

    public onChange(): Observable<string> {
        return this.pathsSubject.asObservable().pipe(share());
    }

    public onActiveSectionChange(): Observable<Section | null> {
        return this.pathsSubject.asObservable().pipe(
            map((path) => this.getActiveSection(path)),
            share()
        );
    }

    public getParameterByName(name: string, url?: string): string | null {
        if (!url) url = window.location.href;
        name = name.replace(/[\[\]]/g, "\\$&");
        const regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)");
        const results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return "";
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }

    public encodeNextUrl(url: string): string {
        const slashCoded = "~";
        const semicolonCoded = "|";
        return url.replace(/\//g, slashCoded).replace(/;/g, semicolonCoded);
    }

    public decodeNextUrl(url: string | null): string | null {
        if (!url) return null;

        const slash = "/";
        const semicolon = ";";
        const nextSeparator = "~next~";

        const firstIndex = url.indexOf(nextSeparator);

        if (firstIndex > -1) {
            let decodedUrl = url.substring(
                0,
                firstIndex + nextSeparator.length
            );
            decodedUrl = decodedUrl
                .replace(/~/g, slash)
                .replace(/\|/g, semicolon);
            const nextUrl = url.substring(firstIndex + nextSeparator.length);

            return decodedUrl + nextUrl;
        }

        return url.replace(/~/g, slash).replace(/\|/g, semicolon);
    }
}
