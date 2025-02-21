import { Component, Input, OnInit } from '@angular/core';

import {ITranslations} from "../../../common/model/translations";
import { MergeLesson } from "../../model/merge-lesson";
import { Lesson } from "../../model/lesson";
import {TranslationsService} from "../../../common/service";


@Component({
  selector: 'app-pages-list',
  templateUrl: './pages-list.component.html'
})
export class PagesListComponent implements OnInit {

    @Input() pages: MergeLesson[];
    @Input() lesson: Lesson;
    public translations: ITranslations;

    constructor(
        private _translations: TranslationsService
    ) {}

    ngOnInit() {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }

}
