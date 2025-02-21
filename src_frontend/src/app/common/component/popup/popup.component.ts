import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

/*
 * Popup component
 *
 * usage:
 *
 * <popup
 *   [title]="'Popup title'"
 *   [content]="'Some popup content'"
 *   [acceptLabel]="'Accept'"
 *   [rejectLabel]="'Cancel'"
 *   [(isVisible)]="isPopupVisible"
 *   (accept)="onAccept($event)"
 *   (reject)="onReject($event)"></popup>
 *
 */
@Component({
    selector: 'popup',
    template:
        `
         <popup-base
             [acceptLabel]="acceptLabel"
             [rejectLabel]="rejectLabel"
             [(isVisible)]="isVisible"
             (accept)="onAccept($event)"
             (reject)="onReject($event)">
                 <span class="popup__title">{{ title }}</span>
                 <span class="popup__content" [innerHTML]="content"></span>
         </popup-base>
        `
})
export class PopupComponent implements OnInit {
    @Input() isVisible: boolean = false;
    @Input() title: string;
    @Input() content: string;
    @Input() acceptLabel: string;
    @Input() rejectLabel: string;

    @Output() accept = new EventEmitter<any>();
    @Output() reject = new EventEmitter<any>();
    @Output() isVisibleChange = new EventEmitter<boolean>();

    ngOnInit () {
        if (!this.acceptLabel) {
            this.acceptLabel = 'Ok';
        }

        if (!this.rejectLabel) {
            this.rejectLabel = 'Cancel';
        }
    }

    public onAccept (event: any) {
        this.accept.emit(event);
        this.hidePopup();
    }

    public onReject (event: any) {
        this.reject.emit(event);
        this.hidePopup();
    }

    private hidePopup () {
        this.isVisible = false;
        this.isVisibleChange.emit(this.isVisible);
    }
}