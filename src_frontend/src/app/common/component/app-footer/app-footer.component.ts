import { Component, Input, OnInit } from "@angular/core";

import { AuthUser, ITranslations } from "../../model";
import { TranslationsService } from "../../../common/service";

interface WindowWithMAuthor extends Window {
    mAuthorAssetsUrl: string;
}

declare let window: WindowWithMAuthor;

@Component({
    selector: "app-footer",
    templateUrl: "./app-footer.component.html",
})
export class AppFooterComponent implements OnInit {
    @Input() user!: AuthUser;

    public assetsUrl: string = window.mAuthorAssetsUrl;
    public currentYear: number = new Date().getUTCFullYear();
    public translations!: ITranslations;

    constructor(private _translations: TranslationsService) {}

    ngOnInit(): void {
        this._translations
            .getTranslations()
            .subscribe((t) => (this.translations = t));
    }
}
