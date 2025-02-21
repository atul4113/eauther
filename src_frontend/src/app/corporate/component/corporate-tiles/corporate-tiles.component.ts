import { Component, Input } from '@angular/core';

import { Space, ITranslations } from "../../../common/model";
import { EditToken } from "../../../my-lessons/model/edit-token";
import { TranslationsService} from "../../../common/service";
import { Lesson } from "../../../my-lessons/model/lesson";


@Component({
    selector: 'app-corporate-tiles',
    templateUrl: './corporate-tiles.component.html'
})
export class CorporateTilesComponent {
    @Input() privateSpace: Space;
    @Input() lastEditedLesson: Lesson;
    @Input() editLessonToken: EditToken;

    public translations: ITranslations;

    constructor (
        private _translations: TranslationsService
    ) {}

    ngOnInit () {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }

}
