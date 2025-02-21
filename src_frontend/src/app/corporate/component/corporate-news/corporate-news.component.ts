import { Component, Input } from '@angular/core';

import { News, ITranslations } from "../../../common/model";
import { TranslationsService} from "../../../common/service";


@Component({
    selector: 'app-corporate-news',
    templateUrl: './corporate-news.component.html'
})
export class CorporateNewsComponent {
    @Input() assetsUrl: string;
    @Input() news: News[];

    public translations: ITranslations;

     constructor (
         private _translations: TranslationsService
    ) {}

    ngOnInit () {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }

}
