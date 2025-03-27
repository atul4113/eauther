import { Component, OnInit } from "@angular/core";
import { forkJoin } from "rxjs";
import { ITranslations } from "./common/model/translations";
import {
    InfoMessageService,
    TranslationsService,
    AuthUserService,
    SettingsService,
} from "./common/service";

@Component({
    selector: "app-root",
    templateUrl: "./app.component.html",
})
export class AppComponent implements OnInit {
    public translations: ITranslations = {} as ITranslations;
    private translationsReady = false;

    constructor(
        private _infoMessage: InfoMessageService,
        private _settings: SettingsService,
        private _translations: TranslationsService,
        private _authUser: AuthUserService
    ) {}

    ngOnInit() {
        this._translations
            .getTranslations()
            .subscribe((t) => (this.translations = t ?? {} as ITranslations))
        this._infoMessage.init();

        forkJoin([
            this._settings.get(),
            this._authUser.get()
        ]).subscribe(([settings, user]) => {
            this._translations.load(settings /*, user, this._profile*/);
        });
        

        this._translations
            .getTranslations()
            .subscribe((translations: any) => {
                this.translations = translations;
                this.translationsReady = true;
            });
    }

    public isAppReady(): boolean {
        return this.translationsReady;
    }
}
