import { Component, EventEmitter, Input, OnChanges, Output, ViewChild } from '@angular/core';
import { Observable } from "rxjs";
import { mergeMap, map } from "rxjs/operators";

import { LessonDetailsMetadataBaseFormComponent } from "../lesson-details-metadata-base-form/lesson-details-metadata-base-form.component";
import { ITranslations } from "../../../common/model/translations";
import { Lesson, Metadata } from "../../model/lesson";
import { MyContentService } from "../../service/my-content.service";


@Component({
    selector: 'app-lesson-details-metadata-form',
    template: `
        <app-lesson-details-metadata-base-form
            [translations]="translations"
            [data]="data"
            [withCustomFields]="lesson.contentType.isLesson() && isProject"
            (isValidChange)="isValidChanged($event)"
        ></app-lesson-details-metadata-base-form>
    `
})
export class LessonDetailsMetadataFormComponent implements OnChanges {

    @ViewChild(LessonDetailsMetadataBaseFormComponent) baseFormComponent!: LessonDetailsMetadataBaseFormComponent;

    @Input() translations!: ITranslations;
    @Input() lesson!: Lesson;
    @Input() metadata!: Metadata;
    @Input() isProject: boolean = true;
    @Output() isValidChange: EventEmitter<boolean> = new EventEmitter<boolean>();

    public data!: Metadata;

    constructor (
        private _myContent: MyContentService
    ) {}

    ngOnChanges () {
        if (this.metadata) {
            this.reset();
        }
    }

    public edit () {
        this.baseFormComponent.edit();
    }

    public  save (): Observable<Metadata> {
        return this.baseFormComponent.save().pipe(
            mergeMap( (data: Metadata) => {
                this.data = data;
                return this._myContent.updateLessonMetadata(this.lesson, data);
            }),
            map( (_) => { return this.data; })
        );
    }

    public reset () {
        this.data = this.metadata.copy();
        this.baseFormComponent.reset();
    }

    public isValidChanged (isValid: boolean) {
        this.isValidChange.emit(isValid);
    }

}
