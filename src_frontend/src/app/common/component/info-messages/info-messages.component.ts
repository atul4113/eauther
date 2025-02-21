import { Component, OnInit, OnDestroy, Output, EventEmitter } from '@angular/core';

import { InfoMessage, ITranslations } from '../../model';
import { InfoMessageService, PathsService, TranslationsService } from '../../service';


@Component({
    selector: 'info-messages',
    templateUrl: './info-messages.component.html'
})
export class InfoMessagesComponent implements OnInit, OnDestroy {
    @Output() toggleErrorMessage = new EventEmitter<boolean>();

    public showErrorMessage = false;
    public errorMessageType: number;
    public message: InfoMessage;
    public serverEmail: string = 'admin@mauthor.com';

    private removeMessageTimeout: any;

    public translations: ITranslations;

    constructor (
        private _infoMessage: InfoMessageService,
        private _paths: PathsService,
        private _translations: TranslationsService

    ) {}

    ngOnInit () {

         this._translations.getTranslations().subscribe(t => this.translations = t);

        this._infoMessage.get()
            .subscribe(message => {
                this.message = null;
                this.clearRemoveMessageTimeout();
                this.message = message;

                if (this.message && this.message.isCloseable() && this.message.isAutoClose()) {
                    this.removeMessageTimeout = setTimeout( () => this.removeInfoMessage() , 15 * 1000);
                }
            });

        this._infoMessage.errors()
            .subscribe(error => {
                if (error === 500 || error === 404) {
                    this.errorMessageType = error;
                    this.showErrorMessage = true;
                    this.toggleErrorMessage.emit(this.showErrorMessage);
                }
            });

        this._paths.onChange().subscribe( () => {
            if (this._paths.getPreviousPath()) {
                this.showErrorMessage = false;
                this.toggleErrorMessage.emit(this.showErrorMessage);
            }
        });
    }

    ngOnDestroy () {
        this.clearRemoveMessageTimeout();
    }

    public closeInfoMessage () {
        this.clearRemoveMessageTimeout();
        this.removeInfoMessage();
    }

    private removeInfoMessage () {
        this.message = null;
    }

    private clearRemoveMessageTimeout () {
        if (this.removeMessageTimeout) {
            clearTimeout(this.removeMessageTimeout);
            this.removeMessageTimeout = null;
        }
    }

}
