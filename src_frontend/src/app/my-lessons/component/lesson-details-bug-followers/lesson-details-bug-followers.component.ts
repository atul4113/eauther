import {Component, OnInit, Input} from '@angular/core';

import {ITranslations} from "../../../common/model/translations";
import {Lesson} from "../../model/lesson";
import {TranslationsService} from "../../../common/service";


@Component({
  selector: 'app-lesson-details-bug-followers',
  templateUrl: './lesson-details-bug-followers.component.html',
})
export class LessonDetailsBugFollowersComponent implements OnInit {

    @Input() lesson: Lesson;
    public translations: ITranslations;

    constructor (
        private _translations: TranslationsService
    ) {}

    ngOnInit () {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }
}
