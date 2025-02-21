import { Component, EventEmitter, Input, Output, ViewChild } from "@angular/core";
import { Observable } from "rxjs";

import { FileData } from "../../model";
import { BaseUploadFileComponent } from "../base-upload-file/base-upload-file.component";


/*
    Upload file component based on ng2-file-upload module.

    Usage:
        * in template:
            <upload-file #uploadFileUniqueId
                (selected)="onFileSelected($event)">
            </upload-file>
            <span *ngIf="file">{{ file.name }} ({{ file.fileId }})</span>
            <button
                (click)="doUpload()"
                [disabled]="!file || file.isUploaded"
                class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored">
              upload
            </button>

        * in component:
            @ViewChild('uploadFileUniqueId') uploadFile: UploadFileComponent;

            private file: File;

            public onFileSelected (file: FileData) {
                this.file = file;
            }

            public doUpload () {
                if ( !file.isUploaded ) {
                    uploadFile.upload().subscribe(
                    (uploadedFile: FileData) => {
                        this.file = uploadedFile;
                        // do sth with uploadedFile
                    }, (error: UploadFileError) => {
                        // do sth about error
                    });
                }
            }

    Events:
        * selected - emitted when file has been selected, $event object holds File instance.
        * uploaded - emitted when file has been successfully uploaded, $event object holds UploadedFile instance,
        * error - emitted when file upload fails, $event object holds UploadFileError instance,
        * fileChange - emitted when file upload status is changing, $event is a boolean value.
 */
@Component({
    selector: 'upload-file',
    template: `
        <base-upload-file (selected)="onSelected($event)">
            <button (click)="baseUploadFile.openFilePicker()"
                    [disabled]="!baseUploadFile.uploader || (baseUploadFile.file && baseUploadFile.file.isUploading) || disabled"
                    mat-mini-fab 
                    color="accent">
                <i class="material-icons">file_upload</i>
            </button>
        </base-upload-file>
    `
})
export class UploadFileComponent {
    @Input() disabled: boolean = false;

    @Output() selected: EventEmitter<FileData> = new EventEmitter<FileData>();

    @ViewChild(BaseUploadFileComponent)
    public baseUploadFile: BaseUploadFileComponent;

    public upload (): Observable<FileData> {
        return this.baseUploadFile.upload();
    }

    public onSelected (file) {
        this.selected.emit(file);
    }

    public clear () {
        this.baseUploadFile.clear();
    }
}
