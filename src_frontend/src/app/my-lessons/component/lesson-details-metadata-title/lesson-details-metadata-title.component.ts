import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

import { ITranslations } from "../../../common/model/translations";
import { RolePermissions } from "../../../common/model/auth-user";


@Component({
    selector: 'app-lesson-details-metadata-title',
    template: `
        <h3>
            <ng-content></ng-content>
        </h3>

        <app-loading *ngIf="isLoading">
        </app-loading>

        <button *ngIf="(!isToggleMode || isToggleOpen) && isEditMode && !isLoading"
                mat-icon-button
                [matTooltip]="translations | getLabel: 'plain.my_lessons.panel.lesson_details.title.save'"
                [matTooltipPosition]="'above'"
                [disabled]="!canSave"
                (click)="onSave()">
            <i class="material-icons">save</i>
        </button>

        <button *ngIf="(userPermissions && userPermissions.contentEditMetadataOfLessonsAddons) && (!isToggleMode || isToggleOpen) && !isLoading" 
                mat-icon-button
                [matTooltip]="translations | getLabel: (isEditMode ? 'plain.my_lessons.panel.lesson_details.title.close' : 'plain.my_lessons.panel.lesson_details.title.edit')"
                [matTooltipPosition]="'above'"
                (click)="changeEditMode()">
            <i *ngIf="!isEditMode"
               class="material-icons">edit</i>
            <i *ngIf="isEditMode"
               class="material-icons">close</i>
        </button>

        <button *ngIf="!isLoading && isToggleMode" 
                mat-icon-button
                (click)="changeToggleMode()">
            <i *ngIf="!isToggleOpen"
               class="material-icons">keyboard_arrow_down</i>
            <i *ngIf="isToggleOpen"
               class="material-icons">keyboard_arrow_up</i>
        </button>
    `
})
export class LessonDetailsMetadataTitleComponent implements OnInit {
    @Input() translations: ITranslations;
    @Input() isEditMode: boolean = false;
    @Input() isLoading: boolean = false;
    @Input() isToggleMode: boolean = false;
    @Input() canSave: boolean = true;
    @Input() userPermissions: RolePermissions;

    @Output() editModeChange: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() toggleModeChange: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() save: EventEmitter<any> = new EventEmitter<any>();

    public isToggleOpen: boolean = false;

    constructor () {}

    ngOnInit () {}

    public onSave () {
        this.save.emit(null);
    }

    public changeEditMode () {
        if (this.userPermissions && this.userPermissions.contentEditMetadataOfLessonsAddons) {
            this.editModeChange.emit(this.isEditMode);
        }
    }

    public changeToggleMode () {
        this.isToggleOpen = !this.isToggleOpen;

        this.toggleModeChange.emit(this.isToggleOpen);
    }

}
