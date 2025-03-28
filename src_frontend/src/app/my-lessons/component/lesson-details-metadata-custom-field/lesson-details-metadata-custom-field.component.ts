import { Component, Input, OnChanges } from '@angular/core';
import { Observable, forkJoin, of } from "rxjs";
import "rxjs/add/observable/of";

import { CustomMetadata } from "../../model/lesson";


@Component({
    selector: 'app-lesson-details-metadata-custom-field',
    templateUrl: './lesson-details-metadata-custom-field.component.html'
})
export class LessonDetailsMetadataCustomFieldComponent implements OnChanges {
    @Input() value!: CustomMetadata;

    public values!: string[];

    public editValue!: CustomMetadata;

    constructor () {}

    ngOnChanges () {
        this.reset();

        if (this.value.fieldType.isSelect()) {
            this.values = this.value.definedValue.split(',');
        }
    }

    public reset () {
        if (this.value) {
            this.editValue = this.value.copy();
        }
    }

    public save (): Observable<CustomMetadata> {
        if (!this.editValue.isEnabled) {
            this.editValue.value = "";
        }

        return of(this.editValue);
    }

}
