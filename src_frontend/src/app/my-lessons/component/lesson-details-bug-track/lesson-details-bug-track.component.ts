import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';

import { Lesson } from "../../model/lesson";
import {AuthUser, ITranslations} from "../../../common/model";
import {Bug} from "../../model/bug";
import { TranslationsService } from "../../../common/service";
import { RolePermissions } from "../../../common/model/auth-user";


@Component({
    selector: 'app-lesson-details-bug-track',
    templateUrl: './lesson-details-bug-track.component.html'
})
export class LessonDetailsBugTrackComponent implements OnInit {
    @Input() user!: AuthUser;
    @Input() lesson!: Lesson;
    @Input() bugs!: Bug[];
    @Input() userPermissions!: RolePermissions;

    @Output() deleteBug: EventEmitter<Bug> = new EventEmitter<Bug>();
    @Output() reportBug: EventEmitter<Bug> = new EventEmitter<Bug>();

    public translations!: ITranslations;
    public isVisible: boolean = false;

    constructor (
        private _translations: TranslationsService
    ) {}

    ngOnInit() {
        this._translations.getTranslations().subscribe(t => {
            this.translations = t ?? {} as ITranslations;
        });
    }

    public onBugReport (bug: Bug) {
        this.reportBug.emit(bug);
    }

    public onBugDelete (bug: Bug) {
        this.deleteBug.emit(bug);
    }

}
