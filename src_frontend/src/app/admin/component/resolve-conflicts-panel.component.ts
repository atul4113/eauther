import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import 'rxjs/add/observable/forkJoin';

//import { ITranslations } from "../../common/model/translations";
import { AuthUser } from "../../common/model/auth-user";
import { TranslationsService, InfoMessageService, TranslationsAdminService } from "../../common/service";
import { ITranslations } from "../../common/model/translations";
import { Conflict, IConflict, ResolvedConflict } from "../model/conflict";
import { ActivatedRoute } from "@angular/router";


@Component({
    templateUrl: '../templates/resolve-conflicts-panel.component.html'
})
export class ResolveConflictsPanelComponent implements OnInit {

    public translations: any;
    public authUser: any;
    public isInitialized = false;
    public isResolved = false;

    public conflictId: any;
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

    ngOnInit () {
        this._route.params.subscribe(params => {

            this.conflictId = params['id'];

            Observable.forkJoin(
                this._translationsAdmin.getConflicts(this.conflictId),
                this._translations.getTranslations()
            ).subscribe( ([ conflicts, translations ]) => {
                this.translations = translations;
                this.conflicts = conflicts.conflict.map(this._translationsAdmin.mapConflicts);
                this.isInitialized = true;

                this.omitted = conflicts.omitted.map( (o:any) => o );
                this.added = conflicts.added.map( (a:any) => a );
                this.notValid = conflicts.not_valid.map( (nv:any) => nv );
            } );
        });
    }

    public finishImport() {

        let resolved = { };
        let key: number = 1;

        for (let con of this.conflicts) {
            resolved[key+""] = new ResolvedConflict(con);
            ++key;
        }

        this._translationsAdmin.resolveConflicts(this.conflictId, resolved).subscribe(
            result => {
                this.isResolved = true;
            },
            error => this._infoMessage.addError("Error while importing labels with resolved conflicts")
        );
    }

}
