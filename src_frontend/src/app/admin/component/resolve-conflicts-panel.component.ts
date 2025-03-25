import { Component, OnInit } from '@angular/core';
import { Observable, forkJoin } from 'rxjs';
import { Params } from '@angular/router';

//import { ITranslations } from "../../common/model/translations";
import { AuthUser } from "../../common/model/auth-user";
import { TranslationsService, InfoMessageService, TranslationsAdminService } from "../../common/service";
import { ITranslations } from "../../common/model/translations";
import { Conflict, IConflict, ResolvedConflict } from "../model/conflict";
import { ActivatedRoute } from "@angular/router";

interface ConflictsResponse {
    conflict: IConflict[];
    omitted: string[];
    added: string[];
    not_valid: string[];
}

@Component({
    templateUrl: '../templates/resolve-conflicts-panel.component.html'
})
export class ResolveConflictsPanelComponent implements OnInit {
    public translations: ITranslations | null = null;
    public authUser: AuthUser | null = null;
    public isInitialized = false;
    public isResolved = false;

    public conflictId: number = 0;
    public conflicts: Conflict[] = [];
    public paginatedConflictsPage = 1;
    public pageSize = 15;

    public omitted: string[] = [];
    public added: string[] = [];
    public notValid: string[] = [];

    constructor(
        private _translations: TranslationsService,
        private _infoMessage: InfoMessageService,
        private _translationsAdmin: TranslationsAdminService,
        private _route: ActivatedRoute,
    ) { }

    ngOnInit(): void {
        this._route.params.subscribe((params: Params) => {
            this.conflictId = parseInt(params['id'] as string, 10);

            forkJoin({
                conflicts: this._translationsAdmin.getConflicts(this.conflictId),
                translations: this._translations.getTranslations()
            }).subscribe(({ conflicts, translations }) => {
                if (translations) {
                    this.translations = translations;
                }
                this.conflicts = conflicts.map(this._translationsAdmin.mapConflicts);
                this.isInitialized = true;

                // Since we're not getting these from the API anymore, we'll initialize them as empty arrays
                this.omitted = [];
                this.added = [];
                this.notValid = [];
            });
        });
    }

    public finishImport(): void {
        const resolved: { [key: string]: ResolvedConflict } = {};
        let key: number = 1;

        for (let con of this.conflicts) {
            resolved[key.toString()] = new ResolvedConflict(con);
            ++key;
        }

        this._translationsAdmin.resolveConflicts(this.conflictId, resolved).subscribe(
            () => {
                this.isResolved = true;
            },
            () => this._infoMessage.addError("Error while importing labels with resolved conflicts")
        );
    }
}
