import { Component, Input, OnInit } from "@angular/core";

import { FileStorage } from "../../model/file-storage";
import { Lesson } from "../../model/lesson";
import { TranslationsService } from "../../../common/service";
import { ITranslations } from "../../../common/model/translations";
import { MyContentService } from "../../service/my-content.service";
import { RolePermissions } from "../../../common/model/auth-user";

@Component({
    selector: "app-lesson-details-history",
    templateUrl: "./lesson-details-history.component.html",
})
export class LessonDetailsHistoryComponent implements OnInit {
    @Input() lesson!: Lesson;
    @Input() versions: FileStorage[] = [];
    @Input() userPermissions!: RolePermissions;

    public paginatedHistory: number = 1;
    public historyPageSize: number = 14;
    public translations: ITranslations | null = null;

    constructor(
        private _myContent: MyContentService,
        private _translations: TranslationsService
    ) {}

    ngOnInit(): void {
        this._translations.getTranslations().subscribe((t) => {
            if (t) {
                this.translations = t;
            }
        });
    }

    public setCurrentVersion(contentId: number, versionId: number): void {
        if (!this.lesson) return;

        this._myContent
            .setCurrentVersion(contentId, versionId)
            .subscribe(() => {
                if (this.lesson) {
                    this.lesson.fileId = versionId;
                }
            });
    }
}
