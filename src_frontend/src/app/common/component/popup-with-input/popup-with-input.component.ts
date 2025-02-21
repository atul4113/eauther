import {Component, OnInit, Input, Output, EventEmitter, ViewChild} from "@angular/core";
import { FormControl, Validators} from '@angular/forms';
import {PopupBaseComponent} from "../popup-base/popup-base.component";


@Component({
    selector: 'popup-with-input',
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
                    <p>{{ content }}</p>
                            <p>
                             <mat-form-field>
                                <input #inputText [placeholder]='placeholder' [formControl]="valueControl" required matInput>
                             </mat-form-field>
                            </p>
                 </span>
         </popup-base>
        `
})
export class PopupWithInputComponent implements OnInit {

    @ViewChild(PopupBaseComponent) popupBase: PopupBaseComponent;

    @Input() isVisible: boolean = false;
    @Input() placeholder: string = "";
    @Input() content: string;
    @Input() title: string;
    @Input() defaultValue: string = "";
    @Input() acceptLabel: string;
    @Input() rejectLabel: string;
    @Input() emptyWarningLabel: string = "";
    @Output() accept = new EventEmitter<string>();
    @Output() reject = new EventEmitter<any>();
    @Output() isVisibleChange = new EventEmitter<boolean>();

    valueControl = new FormControl(this.defaultValue, [Validators.required]);

    ngOnInit() {
        if (!this.acceptLabel) {
            this.acceptLabel = 'Ok';
        }

        if (!this.rejectLabel) {
            this.rejectLabel = 'Cancel';
        }

        this.popupBase.onAccept = this.onAccept.bind(this);
        this.valueControl.markAsUntouched();
    }

    public onAccept(event: any) {
        this.valueControl.markAsTouched();
        if (this.valueControl.value.length > 0) {
            this.accept.emit(this.valueControl.value);
            this.hidePopup();
        }
    }

    public onReject(event: any) {
        this.reject.emit(event);
        this.hidePopup();
    }

    private hidePopup() {
        this.isVisible = false;
        this.valueControl.setValue(this.defaultValue);
        this.isVisibleChange.emit(this.isVisible);
        this.valueControl.markAsUntouched();
    }
}
