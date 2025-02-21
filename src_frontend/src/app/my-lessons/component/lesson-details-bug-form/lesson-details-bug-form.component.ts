import {Component, EventEmitter, OnInit, Input, Output} from '@angular/core';

import {Bug} from "../../model/bug";
import {ITranslations} from "../../../common/model/translations";
import {TranslationsService} from "../../../common/service";


@Component({
    selector: 'app-lesson-details-bug-form',
    templateUrl: './lesson-details-bug-form.component.html'
})
export class LessonDetailsBugFormComponent implements OnInit {
    @Output() reportBug: EventEmitter<Bug> = new EventEmitter<Bug>();

    public editBug: Bug;
    public translations: ITranslations;
    public isTitleValid: boolean = true;
    public isDescValid: boolean = true;

    constructor (
        private _translations: TranslationsService
    ) {}

    ngOnInit() {
        this._translations.getTranslations().subscribe(t => this.translations = t);
        this.editBug = new Bug();
    }

    public get title(): string {
        return this.editBug.title;
    }

    public set title(value: string) {
        this.editBug.title = value;
        this.checkIfTitleValid()
    }

    public get description(): string {
        return this.editBug.description;
    }

    public set description(value: string) {
        if (this.editBug.description.localeCompare(value) !== 0) {
            this.editBug.description = value;
            this.checkIfDescValid()
        }
    }

    public onSubmit() {
        this.checkIfTitleValid();
        this.checkIfDescValid();

        if (this.isTitleValid && this.isDescValid) {
            const bugCopy = this.editBug.copy();
            this.editBug = new Bug();
            this.reportBug.emit(bugCopy);
        }
    }

    private checkIfTitleValid() {
        this.isTitleValid = this.editBug.title.length > 0;
    }

    private checkIfDescValid() {
        this.isDescValid = this.editBug.description.length > 0;
    }

}
