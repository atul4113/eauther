import { Component, OnInit, Input, Output, EventEmitter } from "@angular/core";
import { RadioOption } from "../../model/radio-option";
import { CheckboxOption } from "../../model/checkbox-option";

type Direction = "horizontal" | "vertical";

@Component({
    selector: "popup-with-checkbox",
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
                <p class="check-container">
                    <mat-checkbox
                        *ngFor="let check of checkOptions"
                        [(ngModel)]="check.value"
                        >{{ check.displayName }}</mat-checkbox
                    >
                </p>
            </span>
        </popup-base>
    `,
})
export class PopupWithCheckboxComponent implements OnInit {
    @Input() isVisible: boolean = false;
    @Input() title: string = "";
    @Input() content: string = "";
    @Input() checkOptions: CheckboxOption[] = [];
    @Input() acceptLabel: string = "";
    @Input() rejectLabel: string = "";
    @Input() direction: Direction = "horizontal";

    @Output() accept = new EventEmitter<CheckboxOption[]>();
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
        this.accept.emit(this.checkOptions);
        this.hidePopup();
    }

    public onReject(event: MouseEvent): void {
        this.reject.emit(event);
        this.hidePopup();
    }

    private hidePopup(): void {
        this.isVisible = false;
        this.isVisibleChange.emit(this.isVisible);
    }
}
