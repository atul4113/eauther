import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import 'rxjs/add/observable/forkJoin';

import {
    TranslationsService, TranslationsAdminService, InfoMessageService, SettingsService, UtilsService
} from "../../common/service";
import { Label } from "../model/label";
import { ILanguageRaw, Language } from "../model/language";
import { ITranslations } from "../../common/model/translations";


@Component({
    templateUrl: '../templates/languages-panel.component.html'
})
export class LanguagesPanelComponent implements OnInit {
    public translations: ITranslations;
    public isInitialized = true;
    public settings = null;
    public newLanguageDescription: string;
    public newLanguageKey: string;
    public translationsTextarea: string = '';
    public notificationCheckbox: boolean = false;
    public importLabelsStatus: boolean = false;
    public languages: Language[];
    public selectedLanguage: Language;
    public labelTableInitialized = false;

    public labels: Label[] = [];
    public filteredLabels: Label[];

    constructor(
        private _translations: TranslationsService,
        private _infoMessage: InfoMessageService,
        private _translationsAdmin: TranslationsAdminService,
        private _settings: SettingsService,
        private _utils: UtilsService
    ) { }

    ngOnInit() {

        Observable.forkJoin(
            this._translationsAdmin.getLanguagesList(),
            this._settings.get()
        ).subscribe(([lang, settings]) => {

            this.languages = lang;
            if (this.languages.length) {
                this.selectedLanguage = this.languages[0];
            } else {
                this.selectedLanguage = this.languages[0];
            }

            // todo change localeCompare to new method isSameByKey
            let defaultLang = this.languages.find( lang => lang.key.localeCompare(settings.languageCode) === 0 );
            if (defaultLang !== undefined) {
                defaultLang.isDefault = true;
            }

            this.isInitialized = true;

        } );

        this._translations.getTranslations().subscribe(translations => {
            this.translations = translations;
        });
    }

    public addLanguage () {
        // check if language with this key already exists
        if (this.languages.find( elem => elem.key === this.newLanguageKey ) !== undefined) {
            this._infoMessage.addWarning('Language with this key already exists');
            return;
        }

        if (this.newLanguageKey.length > 7) {
            this._infoMessage.addWarning("Language key can't have more than 7 characters");
            return;
        }

        let lang = new Language(null);
        lang.id = 0; // will come from API
        lang.description = this.newLanguageDescription;
        lang.key = this.newLanguageKey;

        this._translationsAdmin.addLanguage( lang ).subscribe(
            (response : ILanguageRaw) => {
                lang.id = response.id;
                this.languages.push(lang);
                if (!this.selectedLanguage) {
                    this.selectedLanguage = lang;
                }
                this.newLanguageKey = '';
                this.newLanguageDescription = '';
                this._infoMessage.addSuccess('Sent request to add new language. Please check email.');
                },
            error => { this._infoMessage.addError('Error while adding new language'); }
        );

    }

    public deleteLanguage (lang: Language) {
        if (lang.isDefault)
            return;


        this._translationsAdmin.deleteLanguage( lang ).subscribe(
            _ => {
                this.languages = this.languages.filter(iter => iter.key.localeCompare(lang.key) );

                if (this.selectedLanguage.key.localeCompare(lang.key) === 0) {
                    this.selectedLanguage = this.languages[0];
                }

                this._infoMessage.addSuccess('Removed language ' + lang.key);
            },
            error => {
                this._infoMessage.addError('Error while removing language');
            }
        );
    }

    public exportLabels(lang: Language) {

        this._translationsAdmin.getLabels(lang).subscribe(
            (translations: ITranslations) => {

                let generatedJson: string = this._utils.generateJson(translations);

                const blob = new Blob([generatedJson], { type: 'text/plain' });
                const url = window.URL.createObjectURL(blob);
                window.open(url);
            }

        );
    }

    public translationsTextboxChange(newValue: string) {
        this.translationsTextarea = newValue;

        this.importLabelsStatus = this._utils.isJsonValid(this.translationsTextarea);
    }

    public importLanguage() {
         this._translationsAdmin.importLabels(this.selectedLanguage, this.notificationCheckbox, this.translationsTextarea).subscribe(
            result => {
                this._infoMessage.addSuccess("Sent request to import labels. Please wait for email.");
            },
            error => {
                this._infoMessage.addError("Couldn't import labels");
            }
        );
    }
}
