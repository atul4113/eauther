import { Component, Input } from '@angular/core';

import { ITranslations } from "../../../common/model/translations";
import { Lesson } from '../../../my-lessons/model/lesson';
import { EditToken } from "../../../my-lessons/model/edit-token";
import { TranslationsService} from "../../../common/service";


@Component({
    selector: 'app-corporate-lessons-list',
    templateUrl: './corporate-lessons-list.component.html'
})
export class CorporateLessonsListComponent {
    @Input() lessons: any;
    @Input() editLessonToken: any;

    public translations: any;

     constructor (
        private _translations: TranslationsService
    ) {}

    ngOnInit () {

        this._translations.getTranslations().subscribe(t => this.translations = t);
    };
}
