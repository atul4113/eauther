import { Component, Input } from "@angular/core";

import { AuthUser, ITranslations } from "../../model";
import { TranslationsService } from "../../../common/service";

declare var window: any;


@Component({
    selector: 'app-footer',
    templateUrl: './app-footer.component.html'
})
export class AppFooterComponent {
    @Input() user: AuthUser;

    public assetsUrl: string = window.mAuthorAssetsUrl;
    public currentYear = (new Date()).getUTCFullYear();
    public translations: ITranslations;


    constructor (
        private _translations: TranslationsService
    ) {}

    ngOnInit () {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }
}
