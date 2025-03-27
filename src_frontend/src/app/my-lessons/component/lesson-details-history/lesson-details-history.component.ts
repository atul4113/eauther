import { Component, Input, OnInit } from '@angular/core';

import { FileStorage } from "../../model/file-storage";
import { Lesson } from "../../model/lesson";
import { TranslationsService } from "../../../common/service";
import { ITranslations } from "../../../common/model/translations";
import { MyContentService } from "../../service/my-content.service";
import { RolePermissions } from "../../../common/model/auth-user";


@Component({
    selector: 'app-lesson-details-history',
    templateUrl: './lesson-details-history.component.html'
})
export class LessonDetailsHistoryComponent implements OnInit {

    @Input() lesson!: Lesson;
    @Input() versions!: FileStorage[];
    @Input() userPermissions!: RolePermissions;

    public paginatedHistory: number = 1;
    public historyPageSize: number = 14;
    public translations!: ITranslations;

    constructor (
        private _myContent: MyContentService,
        private _translations: TranslationsService
    ) {}

 
    ngOnInit() {
        this._translations.getTranslations().subscribe(t => {
            this.translations = t ?? {} as ITranslations;
        });
    }

    public setCurrentVersion(contentId: any, versionId: any) {
        this._myContent.setCurrentVersion(contentId, versionId).subscribe(
            () => {
                this.lesson.fileId = versionId;
            }
        );
    }

}
