import { Component, OnInit, Input, Output, EventEmitter } from "@angular/core";

/*
 * Popup base component
 *
 * usage:
 *
 * <popup-base
 *   [acceptLabel]="'Accept'"
 *   [rejectLabel]="'Cancel'"
 *   [(isVisible)]="isPopupVisible"
 *   (accept)="onAccept($event)"
 *   (reject)="onReject($event)">
 *      <span class="popup-title">Some popup title</span>
 *      <span class="popup-content">Some popup contnet</span>
 *   </popup-base>
 *
 */
@Component({
    selector: "popup-base",
    template: `
        <div *ngIf="isVisible" class="popup-mask">
            <div class="popup mdl-shadow--4dp">
                <div class="popup-title">
                    <ng-content select=".popup__title"></ng-content>
                </div>
                <div class="popup-content">
                    <ng-content select=".popup__content"></ng-content>
                </div>
                <div class="popup-actions">
                    <button
                        (click)="onReject($event)"
                        class="mdl-button mdl-js-button mdl-button--accent"
                    >
                        {{ rejectLabel }}
                    </button>

                    <button
                        (click)="onAccept($event)"
                        class="mdl-button mdl-js-button mdl-button--primary"
                    >
                        {{ acceptLabel }}
                    </button>
                </div>
            </div>
        </div>
    `,
})
export class PopupBaseComponent implements OnInit {
    @Input() isVisible: boolean = false;
    @Input() acceptLabel: string = "";
    @Input() rejectLabel: string = "";
    @Input() autoClose: boolean = true;

    @Output() accept = new EventEmitter<MouseEvent>();
    @Output() reject = new EventEmitter<MouseEvent>();
    @Output() isVisibleChange = new EventEmitter<boolean>();

    ngOnInit(): void {
        if (!this.acceptLabel) {
            this.acceptLabel = "Ok";
        }

        if (!this.rejectLabel) {
            this.rejectLabel = "Cancel";
        }
    }

    public onAccept(event: MouseEvent): void {
        this.accept.emit(event);
        this.hidePopup();
    }

    public onReject(event: MouseEvent): void {
        this.reject.emit(event);
        this.hidePopup();
    }

    private hidePopup(): void {
        if (this.autoClose) {
            this.isVisible = false;
            this.isVisibleChange.emit(this.isVisible);
        }
    }
}
