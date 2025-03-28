import { Component, Input, OnChanges } from '@angular/core';

import { ITranslations } from "../../../common/model/translations";
import { Lesson } from "../../model/lesson";
import { FileStorage } from "../../model/file-storage";
import { MyContentService } from "../../service/my-content.service";
import { InfoMessageService } from "../../../common/service/info-message.service";
import { RolePermissions } from "../../../common/model/auth-user";


@Component({
    selector: 'app-lesson-details-metadata-base-info',
    templateUrl: './lesson-details-metadata-base-info.component.html'
})
export class LessonDetailsMetadataBaseInfoComponent implements OnChanges {

    @Input() translations!: ITranslations;
    @Input() lesson!: Lesson;
    @Input() versions!: FileStorage[];
    @Input() userPermissions!: RolePermissions;

    public lastModifiedBy: string = '';

    constructor(
        private _myContent: MyContentService,
        private _infoMessage: InfoMessageService
    ) {}

    ngOnChanges() {
        if (this.versions && this.versions.length > 0) {
            this.lastModifiedBy = this.versions[0].owner;
        }
    }

    public publishLesson(contentId: any, event:any) {
        if(this.userPermissions && this.userPermissions.contentPublishLessons) {
            event.stopPropagation();
            this._myContent.publishLesson(contentId).subscribe();
            this._infoMessage.addSuccess("Lesson is now publicly available under the following url: https://www.mauthor.com/present/" + contentId);
            this.lesson.togglePublic();
        }
    }

    public unpublishLesson(contentId: any, event:any) {
        if(this.userPermissions && this.userPermissions.contentPublishLessons) {
            event.stopPropagation();
            this._myContent.unpublicLesson(contentId).subscribe();
            this._infoMessage.addSuccess("Lesson is NOT public");
            this.lesson.togglePublic();
        }
    }

}
