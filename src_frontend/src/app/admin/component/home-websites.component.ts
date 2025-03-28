import { Component, OnDestroy, OnInit } from '@angular/core';
import { Observable, forkJoin } from 'rxjs';

import { ITranslations } from "../../common/model/translations";
import { HomeWebsitesWithLanguage } from "../model/home-websites-with-language";
import { TranslationsService } from "../../common/service";
import { HomeWebsitesService } from 'app/admin/service/home-websites.service';
import { FileData } from "../../common/model/upload-file";
import { HomeWebsite, IHomeWebsiteRaw } from 'app/admin/model/home-website';
import { InfoMessageService } from "../../common/service/info-message.service";
import { HomeWebsiteStatus } from "../model/home-website-status";

@Component({
    templateUrl: '../templates/home-websites.component.html',
    providers: [HomeWebsitesService]
})
export class HomeWebsitesComponent implements OnInit, OnDestroy {
    public translations: ITranslations | null = null;
    public isInitialized = false;
    public homeWebsitesWithLanguages: HomeWebsitesWithLanguage[] = [];

    private timeoutId: number | null = null;

    constructor(
        private _translations: TranslationsService,
        private _homeWebsitesService: HomeWebsitesService,
        private _infoMessage: InfoMessageService,
    ) {}

    ngOnInit() {
        forkJoin(
            this._translations.getTranslations(),
            this._homeWebsitesService.getHomeWebsitesWithLanguages(),
        ).subscribe(([translations, homeWebsitesWithLanguages]: [ITranslations | null, HomeWebsitesWithLanguage[]]) => {
            if (translations) {
                this.translations = translations;
            }
            this.homeWebsitesWithLanguages = homeWebsitesWithLanguages;
            this.isInitialized = true;
        });
    }

    ngOnDestroy(): void {
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }
    }

    public startingUpload(website: HomeWebsite): void {
        const updatedWebsiteRaw: IHomeWebsiteRaw = {
            id: website.id,
            language: website.language.id,
            modified_date: website.modifiedDate,
            status: HomeWebsiteStatus.IN_PROGRESS,
            url: website.url,
            version: website.version
        };
        const updatedWebsite = new HomeWebsite(updatedWebsiteRaw);
        
        this.homeWebsitesWithLanguages = this.homeWebsitesWithLanguages.map(hwl => ({
            ...hwl,
            websites: hwl.websites.map(w => w.id === website.id ? updatedWebsite : w)
        }));
    }

    public onUploaded(file: FileData, website: HomeWebsite): void {
        this._homeWebsitesService.updateHomeWebsite(website, file).subscribe(
            () => {
                this.updateStatus(website);
            }, (error: { body?: { msg?: string } }) => {
                let msg: string;
                if (error.body?.msg) {
                    msg = this.translations?.labels['plain.admin.panel.home_websites.file_not_valid'] || '';
                    msg += this.translations?.labels[error.body.msg] || '';
                } else {
                    msg = this.translations?.labels['common.file_upload.error'] || '';
                }
                this._infoMessage.addError(msg);
                this._homeWebsitesService.getHomeWebsitesWithLanguages().subscribe(
                    (homeWebsitesWithLanguages: HomeWebsitesWithLanguage[]) => {
                        this.homeWebsitesWithLanguages = homeWebsitesWithLanguages;
                    }
                );
            }
        );
    }

    private updateStatus(website: HomeWebsite): void {
        this.timeoutId = window.setTimeout(() => {
            this._homeWebsitesService.getHomeWebsitesWithLanguages().subscribe(
                (homeWebsitesWithLanguages: HomeWebsitesWithLanguage[]) => {
                    this.homeWebsitesWithLanguages = homeWebsitesWithLanguages;
                    homeWebsitesWithLanguages.forEach(
                        homeWebsitesWithLanguage => {
                            homeWebsitesWithLanguage.websites.forEach(ws => {
                                if (ws.id === website.id) {
                                    if (ws.status === HomeWebsiteStatus.IN_PROGRESS) {
                                        this.updateStatus(website);
                                    } else {
                                        this._infoMessage.addSuccess(this.translations?.labels['common.file_upload.success'] || '');
                                    }
                                }
                            });
                        }
                    );
                }
            );
        }, 4000);
    }
}
