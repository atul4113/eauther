import { Component, EventEmitter, Input, OnInit, Output, ViewChild } from '@angular/core';
import { mergeMap } from "rxjs/operators";
import "rxjs/add/observable/forkJoin";
import "rxjs/add/observable/of";

import { UploadFileComponent } from "../../../common/component/upload-file/upload-file.component";
import { FileData } from "../../../common/model/upload-file";
import { Lesson } from "../../model/lesson";
import { InfoMessageService } from "../../../common/service/info-message.service";
import { MyContentService } from "../../service/my-content.service";
import { RolePermissions } from "../../../common/model/auth-user";


@Component({
    selector: 'app-lesson-details-metadata-icon',
    template: `
        <div
            [ngStyle]="{'background-image': 'url(' + lesson.iconHref + ')'}"
            [ngClass]="{'edit': isEditMode}"
            class="icon">
            <button *ngIf="isEditMode"
                    mat-icon-button color="primary"
                    (click)="toggleEditMode()"
                    class="white">
                <i class="material-icons">close</i>
            </button>
            <button *ngIf="!isEditMode && (userPermissions && userPermissions.contentUploadLessonsAddonsIcon)"
                     mat-mini-fab color="primary"
                    (click)="toggleEditMode()"
                    class="white">
                <i class="material-icons">edit</i>
            </button>

            <upload-file *ngIf="isEditMode"
                         [disabled]="isUploadingIcon"
                         (selected)="onFileSelected($event)"
                         [ngClass]="{'hidden': isUploadingIcon}">
            </upload-file>
            <app-loading *ngIf="isUploadingIcon"
            ></app-loading>
        </div>
    `
})
export class LessonDetailsMetadataIconComponent implements OnInit {

    @Input() lesson: Lesson;
    @Input() userPermissions: RolePermissions;
    @Output() iconChange: EventEmitter<FileData> = new EventEmitter<FileData>();

    @ViewChild(UploadFileComponent) uploadFileComponent: UploadFileComponent;

    public isEditMode: boolean = false;
    public isUploadingIcon: boolean = false;

    constructor (
        private _infoMessage: InfoMessageService,
        private _myContent: MyContentService,
    ) {}

    ngOnInit () {}

    public toggleEditMode () {
        this.isEditMode = !this.isEditMode;
    }

    public onFileSelected (file: FileData) {
        if (!file.isUploaded) {
            this.isUploadingIcon = true;
            this.uploadFileComponent.upload().pipe(
                mergeMap(
                (uploadedFile: FileData) => {
                    file = uploadedFile;
                    return this._myContent.updateLessonIcon(this.lesson, uploadedFile);
                })
            ).subscribe(
                () => {
                    this.lesson.iconHref = file.link;
                    this.isUploadingIcon = false;
                    this.isEditMode = false;
                    this._infoMessage.addSuccess('Preview Icon saved successfully.');
                    this.iconChange.emit(file);
                },
                (error) => {
                    console.error(error);
                    this.isUploadingIcon = false;
                    this.isEditMode = false;
                    this._infoMessage.addError('An error occured during saving Preview Icon.');
                }
            )
        }
    }

}
