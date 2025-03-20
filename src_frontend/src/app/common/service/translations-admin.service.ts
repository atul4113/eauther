import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { map } from "rxjs/operators";

import { Language, ILanguageRaw } from "../../admin/model/language";
import { Label } from "../../admin/model/label";
import { ITranslations } from "../model/translations";
import { Conflict, IConflict } from "../../admin/model/conflict";
import { RestClientService } from "./rest-client.service";

const LANGUAGES_URL = "/translations/languages";
const LABELS_LIST_URL = "/translations";
const LABELS_IMPORT_URL = "/translations/import";
const LABELS_URL = "/translations/label";
const CONFLICTS_URL = "/translations/import/resolve_conflicts";

interface ILabelParams {
    create_notification: boolean;
    name: string;
    value: string;
}

interface IImportLabelsParams {
    lang: number;
    create_notification: boolean;
    pasted_json: unknown;
}

interface IModifyLabelParams {
    lang_key: string;
    name: string;
    value: string;
}

interface IResolveConflictsParams {
    replace_conflict: unknown;
}

@Injectable()
export class TranslationsAdminService {
    constructor(private readonly _restClient: RestClientService) {}

    public getLanguagesList(): Observable<Language[]> {
        return this._restClient
            .get<ILanguageRaw[]>(LANGUAGES_URL)
            .pipe(
                map((response) => response.map((lang) => new Language(lang)))
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
    public addLanguage(lang: Language): Observable<ILanguageRaw> {
        const params = {
            lang_key: lang.key,
            lang_description: lang.description,
        };
        return this._restClient.post<ILanguageRaw>(LANGUAGES_URL, params);
    }

    public deleteLanguage(lang: Language): Observable<void> {
        return this._restClient.delete<void>(`${LANGUAGES_URL}/${lang.id}`);
    }

    public getLabels(lang: Language): Observable<ITranslations> {
        return this._restClient.get<ITranslations>(
            `${LABELS_LIST_URL}/${lang.id}`
        );
    }

    // returns empty object
    public addLabel(
        createNotification: boolean,
        label: Label
    ): Observable<void> {
        const params: ILabelParams = {
            create_notification: createNotification,
            name: label.key,
            value: label.value,
        };
        return this._restClient.post<void>(LABELS_URL, params);
    }

    public isLabelKeyValid(key: string): boolean {
        const reg = /^[\d\w.]+$/;
        return reg.test(key);
    }

    // for mass importing labels
    public importLabels(
        lang: Language,
        createNotification: boolean,
        labels: string
    ): Observable<void> {
        const params: IImportLabelsParams = {
            lang: lang.id,
            create_notification: createNotification,
            pasted_json: JSON.parse(labels),
        };
        return this._restClient.post<void>(LABELS_IMPORT_URL, params);
    }

    public removeLabel(label: Label): Observable<void> {
        return this._restClient.delete<void>(`${LABELS_URL}/${label.key}`);
    }

    public modifyLabel(
        lang: Language,
        label: Label,
        newValue: string
    ): Observable<void> {
        const params: IModifyLabelParams = {
            lang_key: lang.key,
            name: label.key,
            value: newValue,
        };

        return this._restClient.put<void>(LABELS_URL, params);
    }

    public getConflicts(id: number): Observable<IConflict[]> {
        return this._restClient.get<IConflict[]>(`${CONFLICTS_URL}/${id}`);
    }

    public resolveConflicts(id: number, conflicts: unknown): Observable<void> {
        const params: IResolveConflictsParams = {
            replace_conflict: conflicts,
        };

        return this._restClient.post<void>(`${CONFLICTS_URL}/${id}`, params);
    }

    public mapConflicts = (response: IConflict): Conflict =>
        new Conflict(response);
}
