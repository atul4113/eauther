import { Component, OnInit } from '@angular/core';
import { TranslationsService } from '../../../common/service';
import { ITranslations } from '../../../common/model';

@Component({
    selector: 'app-quick-tour',
    templateUrl: './quick-tour.component.html'
})
export class QuickTourComponent implements OnInit {
    public translations: ITranslations;

    constructor(
        private _translations: TranslationsService
    ) {
    }

    ngOnInit() {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }

}
