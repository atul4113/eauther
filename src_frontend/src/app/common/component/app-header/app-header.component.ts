import { Component, Input, OnInit } from "@angular/core";

import { AuthUser, Space, ITranslations } from "../../model";
import { PathsService, TranslationsService } from "../../service";
import { LogoService } from "../../service/logo.service";

interface WindowWithMAuthor extends Window {
    mAuthorAssetsUrl: string;
}

declare let window: WindowWithMAuthor;

@Component({
    selector: "app-header",
    templateUrl: "./app-header.component.html",
    providers: [LogoService],
})
export class AppHeaderComponent implements OnInit {
    @Input() user!: AuthUser;
    @Input() isCompact: boolean = false;
    @Input() projects!: Space[];

    public activeSection: string = "";
    public assetsUrl: string = window.mAuthorAssetsUrl;
    public text: string = "";
    public translations: ITranslations | null = null;
    public logoId: number = 0;
    public isFullSize: boolean = true;

    constructor(
        private _paths: PathsService,
        private _translations: TranslationsService,
        private _logo: LogoService
    ) {}

    ngOnInit(): void {
        this._translations
            .getTranslations()
            .subscribe((t: ITranslations | null) => {
                if (t) {
                    this.translations = t;
                }
            });

        this._paths.onActiveSectionChange().subscribe((activeSection: string | number | null) => {
            if (typeof activeSection === 'string') {
                this.activeSection = activeSection;
            }
        });

        this._logo.get().subscribe((logo: number) => {
            this.logoId = logo;
        });

        const currentPath = this._paths.getCurrentPath();
        if (currentPath) {
            const section = this._paths.getActiveSection(currentPath);
            if (typeof section === 'string') {
                this.activeSection = section;
            }
        }
    }

    public onSearchSubmit(): void {
        window.location.href = "/search/search?q=" + this.text;
    }

    public onResize($event: Event): void {
        this.isFullSize = window.screen.width === window.innerWidth;
    }
}
