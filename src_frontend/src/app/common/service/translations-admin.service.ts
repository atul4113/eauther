import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { map } from 'rxjs/operators';

import { Language, ILanguageRaw } from "../../admin/model/language";
import { Label } from "../../admin/model/label";
import { ITranslations } from "../model/translations";
import { Conflict, IConflict } from "../../admin/model/conflict";
import { RestClientService } from "./rest-client.service";


const LANGUAGES_URL: string = '/translations/languages';
const LABELS_LIST_URL: string = '/translations';
const LABELS_IMPORT_URL: string = '/translations/import';
const LABELS_URL: string = '/translations/label';
const CONFLICTS_URL: string = '/translations/import/resolve_conflicts';


@Injectable()
export class TranslationsAdminService {

    constructor(
        private _restClient: RestClientService
    ) {
    }

    public getLanguagesList (): Observable<Language[]> {
        return this._restClient.get(LANGUAGES_URL).pipe(
            map(response => {
                return response.map(lang => new Language(lang));
            })
        );
    }

    /*
    returns id of the newly created lang:
     {
      "created_date": "2017-07-27T02:40:26.204017",
      "id": 5724160613416960,
      "lang_description": "english do usuniecia",
      "lang_key": "en_US7",
      "modified_date": "2017-07-27T02:40:26.204049"
     }
    */
    public addLanguage (lang: Language): Observable<ILanguageRaw> {
        let params = {
            "lang_key": lang.key,
            "lang_description": lang.description
        };
        return this._restClient.post(LANGUAGES_URL, params);
    }

    public deleteLanguage (lang: Language): Observable<any> {
        return this._restClient.delete(LANGUAGES_URL + "/" + lang.id );
    }

    public getLabels(lang: Language): Observable<ITranslations> {
        return this._restClient.get(LABELS_LIST_URL + "/" + lang.id );
    }

    // returns empty object
    public addLabel (createNotification: boolean, label: Label): Observable<any> {

        let params = {
            "create_notification": createNotification ,
            "name": label.key,
            "value": label.value
        };
        return this._restClient.post(LABELS_URL, params);
    }

    public isLabelKeyValid (key: string): boolean {
        let reg = RegExp(/^[\d\w.]+$/);
        let res = reg.exec(key);
        return (res !== null);
    }

     // for mass importing labels
     public importLabels (lang: Language, createNotification: boolean, labels: string): Observable<any> {

        let params = {
            "lang": lang.id,
            "create_notification": createNotification ,
            "pasted_json": JSON.parse(labels)
        };
        return this._restClient.post(LABELS_IMPORT_URL, params);
    }

    public removeLabel (label: Label): Observable<any> {
        return this._restClient.delete(LABELS_URL + "/" + label.key);
    }

    public modifyLabel (lang: Language, label: Label, newValue: string): Observable<any> {

        let params = {
            "lang_key": lang.key,
            "name": label.key ,
            "value": newValue
        };

        return this._restClient.put(LABELS_URL, params);
    }

    public getConflicts(id: number): Observable<any> {
        return this._restClient.get(CONFLICTS_URL + "/" + id );
    }

    public resolveConflicts(id: number, conflicts: any): Observable<any> {
        let params = {
            "replace_conflict": conflicts,
        };

        return this._restClient.post(CONFLICTS_URL + "/" + id, params );
    }

    public mapConflicts = (response: any) => new Conflict(<IConflict> response);

}
