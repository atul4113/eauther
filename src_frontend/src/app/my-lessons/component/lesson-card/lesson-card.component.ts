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
    @Input() lesson!: Lesson;
    @Input() isSelected: boolean = false;
    @Input() spaceId: number = 0;
    @Input() editLessonToken: EditToken | null = null;
    @Input() isProject: boolean = false;
    @Input() userPermissions: RolePermissions | null = null;
    @Input() isTrash: boolean = false;

    @Output() select = new EventEmitter<Lesson>();
    @Output() publish = new EventEmitter<Lesson>();
    @Output() edit = new EventEmitter<{ lesson: Lesson; event: Event }>();
    @Output() undeleteLesson = new EventEmitter<Lesson>();
    @Output() preview = new EventEmitter<Lesson>();

    public editEnabled: boolean = true;
    public translations: ITranslations | null = null;

    constructor(
        private _myContent: MyContentService,
        private _infoMessage: InfoMessageService,
        private _translations: TranslationsService
    ) {}

    ngOnInit(): void {
        this._translations.getTranslations().subscribe((translations: ITranslations | null) => {
            if (translations) {
                this.translations = translations;
            }
        });
        this.editEnabled = true;
    }

    public selectLesson(): void {
        this.select.emit(this.lesson);
    }

    public previewLesson(): void {
        this.preview.emit(this.lesson);
    }

    public publishLesson(contentId: number, event: Event): void {
        event.stopPropagation();
        this.publish.emit(this.lesson);
    }

    public unpublishLesson(contentId: number, event: Event): void {
        event.stopPropagation();
        this.publish.emit(this.lesson);
    }

    public onEdit(event: Event): void {
        event.stopPropagation();
        this.edit.emit({ lesson: this.lesson, event });
    }

    public openEditor(editLessonToken: EditToken): void {
        if (!editLessonToken) {
            return;
        }

        const url = `/mycontent/${this.lesson.id}/editor?${editLessonToken.key}=${editLessonToken.token}`;
        window.location.href = url;
    }

    private successUndeleteCallback(): void {
        const successMessage = this.translations?.labels['lesson.undelete.success'] ?? 'Lesson restored successfully';
        this._infoMessage.addSuccess(successMessage);
        this.undeleteLesson.emit(this.lesson);
    }

    private errorUndeleteCallback(): void {
        const errorMessage = this.translations?.labels['lesson.undelete.error'] ?? 'Failed to restore lesson';
        this._infoMessage.addError(errorMessage);
    }

    public undelete(event: Event): void {
        event.stopPropagation();
        this._myContent.undeleteLesson(this.lesson.id).subscribe(
            () => this.successUndeleteCallback(),
            () => this.errorUndeleteCallback()
        );
    }
}
