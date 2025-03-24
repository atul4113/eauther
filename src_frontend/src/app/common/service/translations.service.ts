import { Injectable } from "@angular/core";
import { Observable, map, share, of, Observer } from "rxjs";

import { RestClientService } from "./rest-client.service";
import { ITranslations } from "../model/translations";
import { Settings, SupportedLanguage } from "../model/settings";
import { AuthUser } from "../model/auth-user";

const TRANSLATIONS_URL: string = "/translations/";

@Injectable()
export class TranslationsService {
    private translations: ITranslations | null = null;
    private translationsObservable: Observable<ITranslations>;
    private translationsObserver!: Observer<ITranslations>;

    private isReady: boolean = false;

    constructor(private readonly _restClient: RestClientService) {
        this.translationsObservable = new Observable<ITranslations>(
            (observer: Observer<ITranslations>) => {
                this.translationsObserver = observer;
            }
        ).pipe(share());

        this.translationsObservable.subscribe(
            (translations) => (this.translations = translations)
        );
    }

    public getTranslations(): Observable<ITranslations | null> {
        if (this.translations) {
            return of(this.translations);
        } else if (this.translationsObservable) {
            return this.translationsObservable;
        } else {
            return of(null);
        }
    }

    public load(settings: Settings, user?: AuthUser): void {
        if (!this.isReady) {
            this.isReady = true;

            const language = this.getCurrentLanguage(settings, user);

            this._restClient
                .getPublic(TRANSLATIONS_URL + (language ? language.id : ""))
                .pipe(map(this.mapTranslations))
                .subscribe({
                    next: (translations: ITranslations | null) => {
                        if (translations) {
                            this.translationsObserver.next(translations);
                            this.translationsObserver.complete();
                        } else {
                            this.translationsObserver.error(
                                new Error("Failed to load translations")
                            );
                        }
                    },
                    error: (err) => {
                        console.error("Error loading translations:", err);
                        this.translationsObserver.error(err);
                    },
                });
        }
    }

    public getCurrentLanguage(
        settings: Settings,
        user?: AuthUser
    ): SupportedLanguage | undefined {
        const defaultLanguage = settings.getDefaultLanguage();
        return defaultLanguage;
    }

    private mapTranslations(response: unknown): ITranslations | null {
        if (!response) {
            return null;
        }
        return response as ITranslations;
    }
}
