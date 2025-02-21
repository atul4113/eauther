import { Component, Input, OnInit } from '@angular/core';

import { ITranslations } from "../../../common/model/translations";
import { MergeLesson } from "../../model/merge-lesson";
import { Lesson } from "../../model/lesson";
import { TranslationsService } from "../../../common/service";

@Component({
  selector: 'app-lesson-pages',
  templateUrl: './lesson-pages.component.html'
})
export class LessonPagesComponent implements OnInit {

    @Input() pages: MergeLesson[];
    @Input() commons: MergeLesson[] = [];
    @Input() lesson: Lesson;
    public translations: ITranslations;

    constructor(
        private _translations: TranslationsService
    ) {}

    ngOnInit() {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }

    public selectAll() {
        this.pages.forEach(page => {
           page._ui.isSelected = true;
        });

        this.commons.forEach(common => {
           common._ui.isSelected = true;
        });
    }

}
