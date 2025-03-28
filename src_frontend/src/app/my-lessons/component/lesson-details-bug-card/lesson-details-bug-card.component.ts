import {Component, OnInit, Input, EventEmitter, Output} from '@angular/core';

import {AuthUser, ITranslations} from "../../../common/model";
import {Bug} from "../../model/bug";
import {TranslationsService} from "../../../common/service";


@Component({
    selector: 'app-lesson-details-bug-card',
    templateUrl: './lesson-details-bug-card.component.html'
})
export class LessonDetailsBugCardComponent implements OnInit {

    @Input() set isActive (value: boolean) {
        setTimeout( () => {
            this.isVisible = value;
        }, 0);
    }

    @Input() user!: AuthUser;
    @Input() bug!: Bug;
    @Output() deleteBug: EventEmitter<Bug> = new EventEmitter<Bug>();

    public translations: ITranslations | null = null;
    public isVisible: boolean = false;

    constructor(
        private _translations: TranslationsService
    ) {}

    ngOnInit(): void {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }

    public onDelete () {
        this.deleteBug.emit(this.bug);
    }

    public get isOwner () {
        if (this.bug && this.user) {
            return this.bug.username.localeCompare(this.user.username) === 0;
        } else {
            return false;
        }
    }
}
