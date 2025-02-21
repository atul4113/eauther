import { Component, OnInit, Input, Output, EventEmitter } from "@angular/core";
import { RadioOption } from "../../model/radio-option";
import { CheckboxOption } from "../../model/checkbox-option";


@Component({
    selector: 'popup-with-checkbox',
    template:
        `
         <popup-base
             [acceptLabel]="acceptLabel"
             [rejectLabel]="rejectLabel"
             [(isVisible)]="isVisible"
             (accept)="onAccept($event)"
             (reject)="onReject($event)">
                 <span class="popup__title">{{ title }}</span>
                 <span class="popup__content">
                    <p class="check-container">
                        <mat-checkbox *ngFor="let check of checkOptions" [(ngModel)]="check.value">{{ check.displayName }}</mat-checkbox>
                    </p>
                 </span>
         </popup-base>
        `
})
export class PopupWithCheckboxComponent implements OnInit {
    @Input() isVisible: boolean = false;
    @Input() title: string;
    @Input() content: string;
    @Input() checkOptions: CheckboxOption[];
    @Input() defaultRadioValue: any;
    @Input() acceptLabel: string;
    @Input() rejectLabel: string;
    @Input() direction: string = "horizontal"; // horizontal || vertical

    @Output() accept = new EventEmitter<CheckboxOption[]>();
    @Output() reject = new EventEmitter<any>();
    @Output() isVisibleChange = new EventEmitter<boolean>();

    public radioValue: any;

    ngOnInit () {
        if (!this.acceptLabel) {
            this.acceptLabel = 'Ok';
        }

        if (!this.rejectLabel) {
            this.rejectLabel = 'Cancel';
        }

        this.radioValue = this.defaultRadioValue;
    }

    public onAccept (event: any) {
        this.accept.emit(this.checkOptions);
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
