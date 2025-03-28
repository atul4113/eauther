import {
    Component,
    OnInit,
    OnDestroy,
    Output,
    EventEmitter,
} from "@angular/core";

import { InfoMessage, ITranslations } from "../../model";
import {
    InfoMessageService,
    PathsService,
    TranslationsService,
} from "../../service";

@Component({
    selector: "info-messages",
    templateUrl: "./info-messages.component.html",
})
export class InfoMessagesComponent implements OnInit, OnDestroy {
    @Output() toggleErrorMessage = new EventEmitter<boolean>();

    public showErrorMessage: boolean = false;
    public errorMessageType: number = 0;
    public message: InfoMessage | null = null;
    public serverEmail: string = "admin@mauthor.com";
    public translations: ITranslations | null = null;

    private removeMessageTimeout: number | null = null;

    constructor(
        private _infoMessage: InfoMessageService,
        private _paths: PathsService,
        private _translations: TranslationsService
    ) {}

    ngOnInit(): void {
        this._translations
            .getTranslations()
            .subscribe((t: ITranslations | null) => {
                if (t) {
                    this.translations = t;
                }
            });

        this._infoMessage.get().subscribe((message: InfoMessage | null) => {
            this.message = null;
            this.clearRemoveMessageTimeout();
            this.message = message;

            if (
                this.message &&
                this.message.isCloseable() &&
                this.message.isAutoClose()
            ) {
                this.removeMessageTimeout = window.setTimeout(
                    () => this.removeInfoMessage(),
                    15 * 1000
                );
            }
        });

        this._infoMessage.errors().subscribe((error: number) => {
            if (error === 500 || error === 404) {
                this.errorMessageType = error;
                this.showErrorMessage = true;
                this.toggleErrorMessage.emit(this.showErrorMessage);
            }
        });

        this._paths.onChange().subscribe(() => {
            if (this._paths.getPreviousPath()) {
                this.showErrorMessage = false;
                this.toggleErrorMessage.emit(this.showErrorMessage);
            }
        });
    }

    ngOnDestroy(): void {
        this.clearRemoveMessageTimeout();
    }

    public closeInfoMessage(): void {
        this.clearRemoveMessageTimeout();
        this.removeInfoMessage();
    }

    private removeInfoMessage(): void {
        this.message = null;
    }

    private clearRemoveMessageTimeout(): void {
        if (this.removeMessageTimeout) {
            clearTimeout(this.removeMessageTimeout);
            this.removeMessageTimeout = null;
        }
    }
}
