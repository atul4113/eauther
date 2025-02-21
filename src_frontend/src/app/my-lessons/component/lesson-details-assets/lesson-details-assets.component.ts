import { Component, Input, OnChanges, ViewChild } from '@angular/core';

import { UploadFileComponent } from "../../../common/component/upload-file/upload-file.component";
import { Asset } from "../../model/asset";
import { Lesson, LESSONS_ORDER_KEYS, LessonsOrder } from "../../model/lesson";
import { FileData, UploadFileError, ITranslations } from "../../../common/model";
import { InfoMessageService, TranslationsService } from "../../../common/service";
import { MyContentService } from "../../service/my-content.service";
import { CookieService } from "../../../common/service/cookie/cookies.service";
import { RolePermissions } from "../../../common/model/auth-user";

@Component({
    selector: 'app-lesson-details-assets',
    templateUrl: './lesson-details-assets.component.html'
})
export class LessonDetailsAssetsComponent implements OnChanges {
    @ViewChild('uploadFileUniqueId') uploadFile: UploadFileComponent;

    @Input() lesson: Lesson;
    @Input() assets: Asset[];
    @Input() assetsLoaded: boolean;
    @Input() userPermissions: RolePermissions;

    public paginatedAssets: number = 1;
    public assetsPageSize: number = 5;
    public file: FileData;
    public isFileUploading: boolean = false;
    public sortedNameUp: boolean = false;
    private _assets: Asset[] = [];
    private _searchPhrase: string = '';
    public translations: ITranslations;
    public assetsOrder: LessonsOrder = new LessonsOrder();
    public isUploadDisabled = false;


    constructor(
        private _myContent: MyContentService,
        private _infoMessage: InfoMessageService,
        private _translations: TranslationsService,
        private _cookie: CookieService
    ) {}

    ngOnInit() {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }

    ngOnChanges() {
        this.detectSort();
        this._assets = this.assets;
    }

    public get searchPhrase(): string {
        return this._searchPhrase;
    }

    public set searchPhrase(value: string) {
        this._searchPhrase = value;
        this.search();
    }

    public search() {
        const phrase = this.searchPhrase.trim().toLowerCase();

        this.assets = this._assets
            .filter(asset =>
                asset.fileName.toLowerCase().indexOf(phrase) > -1 ||
                asset.title.toLowerCase().indexOf(phrase) > -1 ||
                asset.contentType.toLowerCase().indexOf(phrase) > -1 ||
                asset.href.toLowerCase().indexOf(phrase) > -1);
    }

    public onFileSelected(file: FileData) {
        this.file = file;
        this.doUpload();
    }

    public doUpload() {
        this.isFileUploading = true;

        if (!this.file.isUploaded) {
            this._infoMessage.addInfo("Uploading file: " + this.file.name, true);
            this.isUploadDisabled = true;
            this.uploadFile.upload().subscribe((uploadedFile: FileData) => {
                this.file = uploadedFile;
                if(this.file.type.indexOf("zip") > -1) {
                    this.savePackage();
                } else {
                    this.saveFile();
                }
            }, (error: UploadFileError) => {
                this._infoMessage.addError("File has NOT been uploaded");
            }, () => {
                this.isFileUploading = false;
            });
        }
    }

    private savePackage() {
        this._myContent.uploadAssetPackage(this.lesson.id, {fileId: this.file.fileId}).subscribe((data) => {
            this._infoMessage.addSuccess(this.translations.labels['plain.my_lessons.lesson_details_assets.package_uploaded']);
            this._myContent.getLessonAssets(this.lesson.id).subscribe(assets => {
                this.assets = assets;
                this.detectSort();
                this.file = null;
                this.isUploadDisabled = false;
            });
            this.detectSort();
        }, (error) => {
            this._infoMessage.addError("plain.my_lessons.lesson_details_assets.package_upload_error");
            this.file = null;
        });
    }

    private saveFile() {
        this._myContent.uploadAsset(this.lesson.id, {fileId: this.file.fileId}).subscribe((data) => {
            this._infoMessage.addSuccess("File saved");
            this.assets = [Asset.fromFile(this.file), ...this.assets];
            this.detectSort();
            this.file = null;
            this.isUploadDisabled = false;
        }, (error) => {
            this._infoMessage.addError("File has NOT been saved");
            this.file = null;
        });
    }

    public getAssetType(asset: Asset) {
        if(asset.contentType) {
            return asset.contentType.split("/")[0];
        } else {
            return "Unknown";
        }
    }

    public getAssetFormat(asset: Asset) {
        if(asset.contentType) {
            return asset.contentType.split("/")[1];
        } else {
            return "Unknown";
        }
    }

    public getAssetImage(asset: Asset) {
        if(asset.contentType.indexOf("image") !== -1) {
            return asset.href
        } else if (asset.contentType.indexOf("audio") !== -1){
            return "/media/images/default_audio_resource_icon.png";
        } else if (asset.contentType.indexOf("video") !== -1){
            return "/media/images/default_video_resource_icon.png";
        } else {
            return "/media/images/default_binary_resource_icon.png"
        }
    }

    public sortAssetsBy(sortBy: string) {
        if (LESSONS_ORDER_KEYS.has(sortBy)) {
            const order = LESSONS_ORDER_KEYS.get(sortBy);
            this.assetsOrder = new LessonsOrder(order);
            this.setCookieSortBy(sortBy);
            this.assets = this.assets.filter(asset => asset.size !== 0);
            this._assets = this.assets;

            if(this.assetsOrder.isDateDown()) {
                this.assets.sort(function(a: Asset,b: Asset) {return (a.createdDate > b.createdDate) ? 1 : ((b.createdDate > a.createdDate) ? -1 : 0);});
            } else if(this.assetsOrder.isDateUp()) {
                this.assets.sort(function(a: Asset,b: Asset) {return (a.createdDate < b.createdDate) ? 1 : ((b.createdDate < a.createdDate) ? -1 : 0);});
            } else if(this.assetsOrder.isNameDown()) {
                this.assets.sort(function(a: Asset,b: Asset) {return (a.fileName > b.fileName) ? 1 : ((b.fileName > a.fileName) ? -1 : 0);});
            } else if(this.assetsOrder.isNameUp()) {
                this.assets.sort(function(a: Asset,b: Asset) {return (a.fileName < b.fileName) ? 1 : ((b.fileName < a.fileName) ? -1 : 0);});
            }
        }
    }

    public sortAssetsByNameDown() {
        this.sortAssetsBy('nameDown');
    }

    public sortAssetsByNameUp() {
        this.sortAssetsBy('nameUp');
    }

    public sortAssetsByDateDown() {
        this.sortAssetsBy('dateDown');
    }

    public sortAssetsByDateUp() {
        this.sortAssetsBy('dateUp');
    }

    public setCookieSortBy(value: string) {
        let dateYearPlus = new Date();
        dateYearPlus.setTime(dateYearPlus.getTime() + (365*24*3600*1000));
        this._cookie.put('assetsOrderBy' + this.lesson.id, value, {expires: dateYearPlus});
    }

    public detectSort () {
        const cookieOrder = this._cookie.get('assetsOrderBy' + this.lesson.id);
        if (cookieOrder !== undefined) {
            this.sortAssetsBy(cookieOrder);
        } else {
            this.sortAssetsBy('dateUp');
        }
    }
}
