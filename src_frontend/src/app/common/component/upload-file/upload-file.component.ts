import {
    Component,
    EventEmitter,
    Input,
    OnInit,
    Output,
    ViewChild,
} from "@angular/core";
import { Observable } from "rxjs";
import { CommonModule } from "@angular/common";
import { MatButtonModule } from "@angular/material/button";

import { FileData } from "../../model";
import { BaseUploadFileComponent } from "../base-upload-file/base-upload-file.component";
import { UploadFileService } from "../../service";
import { TranslationsService } from "../../service/translations.service";
import { InfoMessageService } from "../../service/info-message.service";
import { ITranslations } from "../../model/translations";
import { GetLabelPipe } from "../../pipe/get-label.pipe";

/**
 * Upload file component based on ng2-file-upload module.
 *
 * Usage:
 * ```html
 * <upload-file #uploadFileUniqueId
 *     (selected)="onFileSelected($event)">
 * </upload-file>
 * <span *ngIf="file">{{ file.name }} ({{ file.fileId }})</span>
 * <button
 *     (click)="doUpload()"
 *     [disabled]="!file || file.isUploaded"
 *     class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored">
 *   upload
 * </button>
 * ```
 *
 * ```typescript
 * @ViewChild('uploadFileUniqueId') uploadFile: UploadFileComponent;
 *
 * private file: FileData;
 *
 * public onFileSelected(file: FileData): void {
 *     this.file = file;
 * }
 *
 * public doUpload(): void {
 *     if (!file.isUploaded) {
 *         uploadFile.upload().subscribe({
 *             next: (uploadedFile: FileData) => {
 *                 this.file = uploadedFile;
 *                 // do sth with uploadedFile
 *             },
 *             error: (error: unknown) => {
 *                 // do sth about error
 *             }
 *         });
 *     }
 * }
 * ```
 *
 * Events:
 * - selected: emitted when file has been selected, $event object holds FileData instance
 * - uploaded: emitted when file has been successfully uploaded, $event object holds FileData instance
 * - error: emitted when file upload fails, $event object holds UploadFileError instance
 * - fileChange: emitted when file upload status is changing, $event is a boolean value
 */
@Component({
    selector: "upload-file",
    standalone: true,
    imports: [
        CommonModule,
        MatButtonModule,
        BaseUploadFileComponent,
        GetLabelPipe,
    ],
    template: `
        <base-upload-file (selected)="onSelected($event)">
            <button
                (click)="baseUploadFile.openFilePicker()"
                [disabled]="disabled"
                mat-mini-fab
                color="accent"
            >
                <i class="material-icons">file_upload</i>
            </button>
        </base-upload-file>
    `,
    providers: [UploadFileService],
})
export class UploadFileComponent implements OnInit {
    @Input() disabled: boolean = false;
    @Output() selected: EventEmitter<FileData> = new EventEmitter<FileData>();

    @ViewChild(BaseUploadFileComponent)
    public baseUploadFile!: BaseUploadFileComponent;

    public translations: ITranslations | null = null;

    constructor(
        private readonly _translations: TranslationsService,
        private readonly _infoMessage: InfoMessageService
    ) {}

    ngOnInit(): void {
        this._translations
            .getTranslations()
            .subscribe((translations: ITranslations | null) => {
                if (translations) {
                    this.translations = translations;
                }
            });
    }

    public upload(): Observable<FileData> {
        return this.baseUploadFile.upload();
    }

    public onSelected(file: FileData): void {
        this.selected.emit(file);
    }

    public clear(): void {
        this.baseUploadFile.clear();
    }
}
