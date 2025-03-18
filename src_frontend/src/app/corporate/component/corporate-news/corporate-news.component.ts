import { Component, Input } from '@angular/core';
import { TranslationsService} from "../../../common/service";


@Component({
    selector: 'app-corporate-news',
    templateUrl: './corporate-news.component.html'
})
export class CorporateNewsComponent {
    @Input() assetsUrl: any;
    @Input() news: any;

    public translations: any;

     constructor (
         private _translations: TranslationsService
    ) {}

    ngOnInit () {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }

}
