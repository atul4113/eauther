import { Injectable } from '@angular/core';
import { Observable, Observer } from 'rxjs';
import { map, share } from 'rxjs/operators';
import "rxjs/add/observable/of";

import { RestClientService } from './rest-client.service';
import { ITranslations } from "../model/translations";
import { Settings, SupportedLanguage } from "../model/settings";
import { AuthUser } from "../model/auth-user";


const TRANSLATIONS_URL: string = '/translations/';

@Injectable()
export class TranslationsService {
    private translations: ITranslations;
    private translationsObservable: Observable<any>;
    private translationsObserver: Observer<any>;

    private isReady: boolean = false;

    constructor (
        private _restClient: RestClientService
    ) {
        this.translationsObservable = Observable.create(
            (observer: Observer<any>) => {
                this.translationsObserver = observer;
            }
        ).pipe(
            share()
        );

        this.translationsObservable.subscribe(translations => this.translations = translations);
    }

    public getTranslations (): Observable<ITranslations> {
        if (this.translations) {
            return  Observable.of(this.translations);
        } else if (this.translationsObservable) {
            return this.translationsObservable;
        } else {
            return null;
        }
    }

    public load (settings: Settings, user?: AuthUser/*, profileService: ProfileService*/) {
        if (!this.isReady) {
            this.isReady = true;

            let language: SupportedLanguage = this.getCurrentLanguage(settings, user);

            this._restClient
                .getPublic(TRANSLATIONS_URL + (language ? language.id : ''))
                .pipe(
                    map(this.mapTranslations)
                )
                .subscribe( (translations: ITranslations) => {
                    this.translationsObserver.next(translations);
                    this.translationsObserver.complete();
                });
        }
    }

    public getCurrentLanguage (settings: Settings, user?: AuthUser) {
        let currentLanguage = null;
        let defaultLanguage = settings.getDefaultLanguage();

        currentLanguage = currentLanguage || defaultLanguage;

        return currentLanguage;
    }

    private mapTranslations (response: any): ITranslations {
        if (!response) {
            return null;
        } else {
            return <ITranslations> response;
        }
    }
}
