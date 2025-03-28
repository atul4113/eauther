import { Component, Input, OnChanges, QueryList, ViewChildren } from '@angular/core';
import { forkJoin, Observable } from "rxjs";

import "rxjs/add/observable/forkJoin";

import { LessonDetailsMetadataBaseFormComponent } from "../lesson-details-metadata-base-form/lesson-details-metadata-base-form.component";
import { Lesson, LessonPage, Metadata } from "../../model/lesson";
import { ITranslations } from "../../../common/model/translations";


@Component({
    selector: 'app-lesson-details-metadata-pages-form',
    template: `
        <div *ngFor="let pageData of data" 
             class="wrapper">
            <h5>{{ pageData.title }}</h5>
            
            <app-lesson-details-metadata-base-form
                [translations]="translations"
                [data]="pageData"
                [withCustomFields]="lesson.contentType.isLesson() && isProject"
                [withTitle]="false">
            </app-lesson-details-metadata-base-form>
        </div>
    `
})
export class LessonDetailsMetadataPagesFormComponent implements OnChanges {

    @ViewChildren(LessonDetailsMetadataBaseFormComponent) metadataComponents: any;

    @Input() translations: any;
    @Input() lesson: any;
    @Input() pages: any;
    @Input() isProject: boolean = true;

    public data: any;

    constructor () {}

    ngOnChanges () {
        if (this.pages) {
            this.reset();
        }
    }

    public edit () {
        this.metadataComponents.forEach( (item:any) => {
            item.edit();
        });
    }

    public save (): Observable<Metadata[]> {
        return forkJoin(this.metadataComponents.map((item: any) => item.save())) as Observable<Metadata[]>;
    }
    

    public reset () {
        this.data = this.pages.map((page:any) => Metadata.fromLessonPage(page));
        if (this.metadataComponents && this.metadataComponents.forEach) {
            this.metadataComponents.forEach( (item:any) => {
                item.reset();
            });
        }
    }

}
