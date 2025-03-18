import { Component, Input } from '@angular/core';
import { TranslationsService} from "../../../common/service";


@Component({
    selector: 'app-corporate-tiles',
    templateUrl: './corporate-tiles.component.html'
})
export class CorporateTilesComponent {
    @Input() privateSpace: any;
    @Input() lastEditedLesson: any;
    @Input() editLessonToken: any;

    public translations: any;

    constructor (
        private _translations: TranslationsService
    ) {}

    ngOnInit () {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }

}
