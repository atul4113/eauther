import { Component, Input, OnInit } from "@angular/core";

import { AuthUser, Space, ITranslations } from "../../model";
import { TranslationsService } from "../../../common/service";

interface WindowWithMAuthor extends Window {
    mAuthorAssetsUrl: string;
}

declare let window: WindowWithMAuthor;

@Component({
    selector: "app-drawer",
    templateUrl: "./app-drawer.component.html",
})
export class AppDrawerComponent implements OnInit {
    @Input() isHeaderCompact: boolean = false;
    @Input() user!: AuthUser;
    @Input() projects: Space[] = [];

    public isOpen: boolean = false;
    public assetsUrl: string = window.mAuthorAssetsUrl;
    public text: string = "";
    public translations: ITranslations | null = null;
    public isFullSize: boolean = true;

    constructor(private _translations: TranslationsService) {}

    ngOnInit(): void {
        this._translations
            .getTranslations()
            .subscribe((t: ITranslations | null) => {
                if (t) {
                    this.translations = t;
                }
            });
    }

    public close(): void {
        this.isOpen = false;
    }

    public open(): void {
        this.isOpen = true;
    }

    public onSearchSubmit(): void {
        window.location.href = "/search/search?q=" + this.text;
    }

    public onResize(event: Event): void {
        this.isFullSize = window.screen.width === window.innerWidth;
    }
}
