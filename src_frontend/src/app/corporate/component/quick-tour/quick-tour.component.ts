import { Component, OnInit } from '@angular/core';
import { TranslationsService } from '../../../common/service';

@Component({
    selector: 'app-quick-tour',
    templateUrl: './quick-tour.component.html'
})
export class QuickTourComponent implements OnInit {
    public translations: any;

    constructor(
        private _translations: TranslationsService
    ) {
    }

    ngOnInit() {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }

}
