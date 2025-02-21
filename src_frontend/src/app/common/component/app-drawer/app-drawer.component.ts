import { Component, Input, OnInit } from '@angular/core';

import { AuthUser, Space, ITranslations } from "../../model";
import { TranslationsService } from "../../../common/service";

declare var window: any;

@Component({
    selector: 'app-drawer',
    templateUrl: './app-drawer.component.html',
})
export class AppDrawerComponent implements OnInit {
    @Input() isHeaderCompact: boolean = false;

    @Input() user: AuthUser;
    @Input() projects: Space[];

    public isOpen: boolean = false;
    public assetsUrl: string = window.mAuthorAssetsUrl;

    public text: string;
    public translations: ITranslations;
    public isFullSize = true;

    constructor (
        private _translations: TranslationsService
    ) {}

    ngOnInit () {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }

    public close () {
        this.isOpen = false;
    }

    public open () {
        this.isOpen = true;
    }

    public onSearchSubmit() {
        window.location.href = '/search/search?q=' + this.text;
    }

    public onResize($event) {
        if(window.screen.width !== window.innerWidth){
            this.isFullSize = false;
        } else {
           this.isFullSize = true;
        }
    }
}
