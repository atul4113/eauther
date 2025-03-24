import { Component, OnInit, Input, Output, EventEmitter } from "@angular/core";
import { RadioOption } from "../../model/radio-option";

type Direction = "horizontal" | "vertical";

@Component({
    selector: "popup-with-radio",
    template: `
        <popup-base
            [acceptLabel]="acceptLabel"
            [rejectLabel]="rejectLabel"
            [(isVisible)]="isVisible"
            (accept)="onAccept($event)"
            (reject)="onReject($event)"
        >
            <span class="popup__title">{{ title }}</span>
            <span class="popup__content">
                <p>{{ content }}</p>
                <p>
                    <mat-radio-group
                        class="popup-with-radio__group"
                        [ngClass]="{ vertical: direction === 'vertical' }"
                        [(ngModel)]="radioValue"
                    >
                        <mat-radio-button
                            *ngFor="let option of radioOptions"
                            [value]="option.value"
                            >{{ option.content }}</mat-radio-button
                        >
                    </mat-radio-group>
                </p>
            </span>
        </popup-base>
    `,
})
export class PopupWithRadioComponent implements OnInit {
    @Input() isVisible: boolean = false;
    @Input() title: string = "";
    @Input() content: string = "";
    @Input() radioOptions: RadioOption[] = [];
    @Input() defaultRadioValue: unknown;
    @Input() acceptLabel: string = "";
    @Input() rejectLabel: string = "";
    @Input() direction: Direction = "horizontal";

    @Output() accept = new EventEmitter<unknown>();
    @Output() reject = new EventEmitter<unknown>();
    @Output() isVisibleChange = new EventEmitter<boolean>();

    public radioValue: unknown;

    ngOnInit(): void {
        if (!this.acceptLabel) {
            this.acceptLabel = "Ok";
        }

        if (!this.rejectLabel) {
            this.rejectLabel = "Cancel";
        }

        this.radioValue = this.defaultRadioValue;
    }

    public onAccept(event: unknown): void {
        this.accept.emit(this.radioValue);
        this.hidePopup();
    }

    public onReject(event: unknown): void {
        this.reject.emit(event);
        this.hidePopup();
    }

    private hidePopup(): void {
        this.isVisible = false;
        this.radioValue = this.defaultRadioValue;
        this.isVisibleChange.emit(this.isVisible);
    }
}
