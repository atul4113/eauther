import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

import { ITranslations } from "../../../common/model/translations";
import { Lesson } from "../../model/lesson";
import { EditToken } from "../../model/edit-token";
import { TranslationsService } from "../../../common/service";
import { MyContentService } from "../../service/my-content.service";
import { RolePermissions } from "../../../common/model/auth-user";
import { InfoMessageService } from "../../../common/service/info-message.service";


@Component({
    selector: 'app-lesson-card',
    templateUrl: './lesson-card.component.html',
    providers: [MyContentService]
})
export class LessonCardComponent implements OnInit {

    @Input() lesson: Lesson;
    @Input() isSelected: boolean;
    @Input() spaceId: any;
    @Input() editLessonToken: EditToken;
    @Input() isProject: boolean;
    @Input() userPermissions: RolePermissions;
    @Input() isTrash: boolean;

    @Output() select = new EventEmitter<Lesson>();
    @Output() publish = new EventEmitter<Lesson>();
    @Output() edit = new EventEmitter<any>();
    @Output() undeleteLesson = new EventEmitter<Lesson>();
    @Output() preview = new EventEmitter<Lesson>();

    public editEnabled: boolean = true;

    public translations: ITranslations;

    constructor(private _myContent: MyContentService,
                private _infoMessage: InfoMessageService,
                private _translations: TranslationsService) {
    }

    ngOnInit() {
        this._translations.getTranslations().subscribe(t => this.translations = t);
        this.editEnabled = true;
    }

    public selectLesson() {
        this.select.emit(this.lesson);
    }

    public previewLesson(){
        if(this.userPermissions && this.userPermissions.contentViewLessonsAddons) {
            this.preview.emit(this.lesson);
        }
    }

    public publishLesson(contentId: any, event) {
        event.stopPropagation();
        this._myContent.publishLesson(contentId).subscribe();
        this.publish.emit(this.lesson);
    }

    public unpublishLesson(contentId: any, event) {
        event.stopPropagation();
        this._myContent.unpublicLesson(contentId).subscribe();
        this.publish.emit(this.lesson);
    }

    public onEdit(event) {
        event.stopPropagation();
        if(this.editEnabled) {
            this.edit.emit(this.lesson.id);
        }
        this.editEnabled = false;
    }

    /*
    public fireEditor(id) {
        let elementId = id + this.lesson.id;

        setTimeout(function () {
            document.getElementById(elementId).click();
        }, 0);
    }

    public openEditor(editLessonToken: EditToken) {
        if (this.lesson.contentType.isLesson()) {
            if (this.isProject) {
                this.fireEditor("edit-lesson-is-project");
            } else {
                this.fireEditor("edit-lesson-is-not-project");
            }
        } else {
            if (this.isProject) {
                this.fireEditor("edit-addon-is-project");
            } else {
                this.fireEditor("edit-addon-is-not-project");
            }
        }
    }
    */

    public openEditor(editLessonToken: EditToken){
        let redirectUrl = "";
        if (this.lesson.contentType.isLesson()) {
            if (this.isProject) {
                redirectUrl = '/mycontent/' + this.lesson.id + '/editor?next=/corporate/list/' + this.spaceId + '&' + editLessonToken.tokenKey + '=' + editLessonToken.token;
            } else {
                redirectUrl = '/mycontent/' + this.lesson.id + '/editor?next=/mycontent&' + editLessonToken.tokenKey + '=' + editLessonToken.token;
            }
        } else {
            if (this.isProject) {
                redirectUrl = '/mycontent/' + this.lesson.id + '/editaddon?next=/corporate/list/' + this.spaceId + '&' + editLessonToken.tokenKey + '=' + editLessonToken.token;
            } else {
                redirectUrl = '/mycontent/' + this.lesson.id + '/editaddon?next=/mycontent&' + editLessonToken.tokenKey + '=' + editLessonToken.token;
            }
        }
        if(redirectUrl.length > 0) {
            window.location.href = redirectUrl;
        }
    }

    private successUndeleteCallback() {
        if (this.lesson.contentType.isAddon()) {
            this._infoMessage.addSuccess("Addon " + this.lesson.title + " has been undeleted");
        } else {
            this._infoMessage.addSuccess("Lesson " + this.lesson.title + " has been undeleted");
        }
        // this.lessons = this.lessons.filter(les => les.id != lesson.id);
        // this.selectedLessons = this.selectedLessons.filter(l => l.id !== lesson.id);
        this.lesson.isDeleted = false;
        this.undeleteLesson.emit(this.lesson);
    }

    private errorUndeleteCallback() {
        if (this.lesson.contentType.isAddon()) {
            this._infoMessage.addError("Addon " + this.lesson.title + " has NOT been undeleted");
        } else {
            this._infoMessage.addError("Lesson " + this.lesson.title + " has NOT been undeleted");
        }
    }

    public undelete(event) {
        event.stopPropagation();
        if (!this.isProject) {
            this._myContent.undeleteLesson(this.lesson.id).subscribe(
                (success) => {
                    this.successUndeleteCallback();
                },
                (error) => {
                    this.errorUndeleteCallback();
                }
            )
        } else {
            this._myContent.deleteCorporateLesson(this.lesson.id).subscribe(
                (success) => {
                    this.successUndeleteCallback();
                },
                (error) => {
                    this.errorUndeleteCallback();
                }
            )
        }
    }

}
