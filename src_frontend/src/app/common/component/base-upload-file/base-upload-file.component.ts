import {
    Component,
    Output,
    EventEmitter,
    OnInit,
    ViewChild,
    ElementRef,
} from "@angular/core";
import { FileUploader, FileItem, ParsedResponseHeaders } from "ng2-file-upload";
import { Observable, Observer, forkJoin } from "rxjs";

import { FileData, UploadFileError } from "../../model/upload-file";
import { UploadFileService, TokenService } from "../../service";

@Component({
    selector: "base-upload-file",
    template: `
        <input
            *ngIf="uploader"
            #fileInput
            [uploader]="uploader"
            type="file"
            ng2FileSelect
        />
        <ng-content></ng-content>
    `,
    providers: [UploadFileService],
})
export class BaseUploadFileComponent implements OnInit {
    @Output() selected: EventEmitter<FileData> = new EventEmitter<FileData>();

    public uploader: FileUploader | null = null;
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
        this.fileInput.nativeElement.click();
    }

    public clear(): void {
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
