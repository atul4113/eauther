import {
    Component,
    EventEmitter,
    Input,
    OnInit,
    Output,
    ViewChild,
} from "@angular/core";
import { Observable } from "rxjs";

import { FileData } from "../../model";
import { BaseUploadFileComponent } from "../base-upload-file/base-upload-file.component";
import { UploadFileService } from "../../service";
import { TranslationsService } from "../../service/translations.service";
import { InfoMessageService } from "../../service/info-message.service";
import { ITranslations } from "../../model/translations";

@Component({
    selector: "simple-upload-file",
    template: `
        <base-upload-file (selected)="onSelected($event)">
            <button
                (click)="baseUploadFile.openFilePicker()"
                [disabled]="disabled"
                mat-raised-button
                color="accent"
            >
                {{ translations | getLabel : "common.file_upload.upload" }}
            </button>
        </base-upload-file>
    `,
    providers: [UploadFileService],
})
export class SimpleUploadFileComponent implements OnInit {
    @Input() disabled: boolean = false;

    @Output() startingUpload: EventEmitter<void> = new EventEmitter<void>();
    @Output() uploaded: EventEmitter<FileData> = new EventEmitter<FileData>();

    @ViewChild(BaseUploadFileComponent)
    public baseUploadFile!: BaseUploadFileComponent;

    public translations!: ITranslations;

    constructor(
        private readonly _translations: TranslationsService,
        private readonly _infoMessage: InfoMessageService
    ) {}

    ngOnInit(): void {
        this._translations
            .getTranslations()
            .subscribe((translations: ITranslations) => {
                this.translations = translations;
            });
    }

    public upload(): void {
        this.startingUpload.emit();
        this.baseUploadFile.upload().subscribe({
            next: (uploadedFile: FileData) => {
                this.uploaded.emit(uploadedFile);
            },
            error: (error: unknown) => {
                this._infoMessage.addError(
                    this.translations.labels["common.file_upload.error"]
                );
                console.error("File upload error:", error);
            },
        });
    }

    public onSelected(file: File): void {
        this.upload();
    }
}
