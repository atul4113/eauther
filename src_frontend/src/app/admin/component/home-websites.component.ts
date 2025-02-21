import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Observable } from 'rxjs';

import { ITranslations } from "../../common/model/translations";
import { HomeWebsitesWithLanguage } from "../model/home-websites-with-language";
import { TranslationsService } from "../../common/service";
import { HomeWebsitesService } from 'app/admin/service/home-websites.service';
import { FileData } from "../../common/model/upload-file";
import { HomeWebsite } from 'app/admin/model/home-website';
import { InfoMessageService } from "../../common/service/info-message.service";
import { HomeWebsiteStatus } from "../model/home-website-status";


@Component({
    templateUrl: '../templates/home-websites.component.html',
    providers: [HomeWebsitesService]
})
export class HomeWebsitesComponent implements OnInit, OnDestroy {
    public translations: ITranslations;
    public isInitialized = false;
    public homeWebsitesWithLanguages: HomeWebsitesWithLanguage[];

    private timeoutId: any;

    constructor(
        private _translations: TranslationsService,
        private _homeWebsitesService: HomeWebsitesService,
        private _infoMessage: InfoMessageService,
    ) {}

    ngOnInit() {
        Observable.forkJoin(
            this._translations.getTranslations(),
            this._homeWebsitesService.getHomeWebsitesWithLanguages(),
        ).subscribe(([translations, homeWebsitesWithLanguages]) => {
            this.translations = translations;
            this.homeWebsitesWithLanguages = homeWebsitesWithLanguages;
            this.isInitialized = true;
        });
    }

    ngOnDestroy (): void {
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }
    }

    public startingUpload (website: HomeWebsite) {
        website.status = HomeWebsiteStatus.IN_PROGRESS;
    }

    public onUploaded (file: FileData, website: HomeWebsite) {
        this._homeWebsitesService.updateHomeWebsite(website, file).subscribe(
            () => {
                this.updateStatus(website);
            }, (error) => {
                let msg: string;
                if (error.body.msg) {
                    msg = this.translations.labels['plain.admin.panel.home_websites.file_not_valid'];
                    msg += this.translations.labels[error.body.msg];
                } else {
                    msg = this.translations.labels['common.file_upload.error'];
                }
                this._infoMessage.addError(msg);
                this._homeWebsitesService.getHomeWebsitesWithLanguages().subscribe(
                    (homeWebsitesWithLanguages) => {
                        this.homeWebsitesWithLanguages = homeWebsitesWithLanguages;
                    }
                );
            }
        );
    }

    private updateStatus (website: HomeWebsite) {
        this.timeoutId = setTimeout(() => {
            this._homeWebsitesService.getHomeWebsitesWithLanguages().subscribe(
                (homeWebsitesWithLanguages) => {
                    this.homeWebsitesWithLanguages = homeWebsitesWithLanguages;
                    homeWebsitesWithLanguages.forEach(
                        homeWebsitesWithLanguage => {
                            homeWebsitesWithLanguage.websites.forEach(ws => {
                                if (ws.id === website.id) {
                                    if (ws.status === HomeWebsiteStatus.IN_PROGRESS) {
                                        this.updateStatus(website);
                                    } else {
                                        this._infoMessage.addSuccess(this.translations.labels['common.file_upload.success'])
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
