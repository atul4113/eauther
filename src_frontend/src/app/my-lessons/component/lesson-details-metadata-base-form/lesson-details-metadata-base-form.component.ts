import { Component, EventEmitter, Input, OnChanges, Output, QueryList, ViewChildren } from '@angular/core';
import { Observable, forkJoin, of } from "rxjs";
import { mergeMap } from "rxjs/operators";

import { LessonDetailsMetadataCustomFieldComponent } from "../lesson-details-metadata-custom-field/lesson-details-metadata-custom-field.component";
import { Metadata } from "../../model/lesson";
import { ITranslations } from "../../../common/model/translations";

@Component({
    selector: 'app-lesson-details-metadata-base-form',
    templateUrl: './lesson-details-metadata-base-form.component.html'
})
export class LessonDetailsMetadataBaseFormComponent implements OnChanges {
    @ViewChildren(LessonDetailsMetadataCustomFieldComponent) customFields!: QueryList<LessonDetailsMetadataCustomFieldComponent>;

    @Input() translations!: ITranslations;
    @Input() data!: Metadata;
    @Input() withTitle: boolean = true;
    @Input() withCustomFields: boolean = true;

    @Output() isValidChange: EventEmitter<boolean> = new EventEmitter<boolean>();

    public isEditMode: boolean = false;
    public editData!: Metadata;
    public isTitleValid: boolean = true;

    public get title(): string {
        return this.editData?.title || '';
    }

    public set title(value: string) {
        if (this.editData) {
            this.editData.title = value;
            this.isTitleValid = this.editData.title.length > 0;
            this.isValidChange.emit(this.isTitleValid);
        }
    }

    ngOnChanges(): void {
        if (this.data) {
            this.editData = this.data.copy();
        }
    }

    public edit(): void {
        this.title = this.editData?.title || '';
        this.isEditMode = true;
    }

    public save(): Observable<Metadata> {
        this.isEditMode = false;
        const data = this.editData.copy();
        
        if (this.withCustomFields && this.customFields?.length > 0) {
            return forkJoin(
                this.customFields.map(customField => customField.save())
            ).pipe(
                mergeMap((customFieldsValues) => {
                    data.customValues = customFieldsValues as any[]; // Explicit cast if necessary
                    return of(data);
                })
            );
        } else {
            data.customValues = [];
            return of(data);
        }
    }

    public reset(): void {
        this.isEditMode = false;
    }
}