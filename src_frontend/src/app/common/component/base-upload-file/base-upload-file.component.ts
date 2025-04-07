import {
    Component,
    Output,
    EventEmitter,
    OnInit,
    ViewChild,
    ElementRef,
    Input,
} from "@angular/core";
import { FileUploader, FileItem, ParsedResponseHeaders } from "ng2-file-upload";
import { Observable, Observer, forkJoin } from "rxjs";
import { FileUploadModule } from "ng2-file-upload";
import { CommonModule } from "@angular/common";

import { FileData, UploadFileError } from "../../model/upload-file";
import { UploadFileService, TokenService } from "../../service";

@Component({
    selector: "base-upload-file",
    standalone: true,
    imports: [CommonModule, FileUploadModule],
    template: `
        <input
            #fileInput
            type="file"
            (change)="onFileChange($event)"
            style="display: none"
        />
        <ng-content></ng-content>
    `,

    providers: [UploadFileService],
})
export class BaseUploadFileComponent implements OnInit {
    @Input() uploader: FileUploader | null = null;
    @Output() selected: EventEmitter<FileData> = new EventEmitter<FileData>();

    public file: FileItem | null = null;

    @ViewChild("fileInput")
    private fileInput!: ElementRef;

    private observer: Observer<FileData> | null = null;

    constructor(
        private _uploadFile: UploadFileService,
        private _token: TokenService
    ) {}

    ngOnInit(): void {
        this.init();
    }

    onFileChange(event: Event): void {
        const input = event.target as HTMLInputElement;
        if (input.files && input.files.length > 0) {
            const selectedFile = input.files[0];

            if (this.uploader) {
                this.uploader.clearQueue();
                this.uploader.addToQueue([selectedFile]);
                this.file = this.uploader.queue[0];

                this.selected.emit(
                    new FileData(
                        selectedFile.name || "",
                        selectedFile.type || "",
                        selectedFile.size
                    )
                );
            }
        }
    }

    public upload(): Observable<FileData> {
        return new Observable((observer: Observer<FileData>) => {
            if (this.observer) {
                observer.error(
                    new UploadFileError("File is already uploading.", 400)
                );
                observer.complete();
            } else {
                this.observer = observer;

                if (this.file && !this.file.isSuccess) {
                    forkJoin({
                        token: this._token.getFreshToken(),
                        uploadUrl: this._uploadFile.getUploadUrl(),
                    }).subscribe({
                        next: ({ token, uploadUrl }) => {
                            if (this.uploader) {
                                this.uploader.setOptions({
                                    url: uploadUrl,
                                    authToken: "JWT " + token,
                                });
                                this.file!.upload();
                            }
                        },
                        error: (error: unknown) => {
                            this.observer!.error(
                                new UploadFileError("Could not get token", 401)
                            );
                            this.observer!.complete();
                        },
                    });
                } else {
                    this.observer.error(
                        new UploadFileError(
                            "File not provided or file already uploaded.",
                            404
                        )
                    );
                    this.observer.complete();
                }
            }
        });
    }

    public openFilePicker(): void {
        if (this.fileInput) {
            this.fileInput.nativeElement.click();
        }
    }

    public clear(): void {
        if (this.uploader) {
            this.uploader.clearQueue();
        }
        this.init();
    }

    private init(): void {
        this.observer = null;
        this.file = null;
        this.initUploader();
    }

    private initUploader(): void {
        this.uploader = new FileUploader({ url: "" });

        this.uploader.onAfterAddingFile = (item: FileItem) => {
            if (this.file && this.uploader) {
                this.uploader.removeFromQueue(this.file);
            }
            this.file = item;
            this.observer = null;
            this.selected.emit(
                new FileData(
                    item.file.name || "",
                    item.file.type || "",
                    item.file.size
                )
            );
        };

        this.uploader.onSuccessItem = (
            item: FileItem,
            response: string,
            status: number,
            headers: ParsedResponseHeaders
        ) => {
            let data: { uploaded_file_id: number } = JSON.parse(response);
            this.uploader!.clearQueue();
            this.observer!.next(
                new FileData(
                    item.file.name || "",
                    item.file.type || "",
                    item.file.size,
                    data.uploaded_file_id,
                    true
                )
            );
            this.observer!.complete();
            this.init();
        };

        this.uploader.onErrorItem = (
            item: FileItem,
            response: string,
            status: number,
            headers: ParsedResponseHeaders
        ) => {
            this.uploader!.clearQueue();
            this.observer!.error(new UploadFileError(response, status));
            this.observer!.complete();
            this.init();
        };
    }
}
