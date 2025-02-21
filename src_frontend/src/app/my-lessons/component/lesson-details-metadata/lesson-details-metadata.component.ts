import { Component, EventEmitter, Input, OnChanges, Output, ViewChild } from "@angular/core";

import { LessonDetailsMetadataPropertiesComponent } from "../lesson-details-metadata-properties/lesson-details-metadata-properties.component";
import { LessonDetailsMetadataFormComponent } from "../lesson-details-metadata-form/lesson-details-metadata-form.component";
import { LessonDetailsMetadataPagesFormComponent } from "../lesson-details-metadata-pages-form/lesson-details-metadata-pages-form.component";
import { Lesson, LessonPage, LessonProperties, Metadata } from "../../model/lesson";
import { FileData, ITranslations } from "../../../common/model";
import { FileStorage } from "../../model/file-storage";
import { InfoMessageService } from "../../../common/service";
import { MyContentService } from "../../service/my-content.service";
import { RolePermissions } from "../../../common/model/auth-user";


@Component({
    selector: 'app-lesson-details-metadata',
    templateUrl: './lesson-details-metadata.component.html'
})
export class LessonDetailsMetadataComponent implements OnChanges {
    @Input() translations: ITranslations;
    @Input() lesson: Lesson;
    @Input() pages: LessonPage[];
    @Input() versions: FileStorage[];
    @Input() metadata: Metadata;
    @Input() isProject: boolean = true;
    @Input() userPermissions: RolePermissions;

    @Output() pagesChange: EventEmitter<LessonPage[]> = new EventEmitter<LessonPage[]>();
    @Output() iconChange: EventEmitter<FileData> = new EventEmitter<FileData>();
    @Output() metadataChange: EventEmitter<Metadata> = new EventEmitter<Metadata>();
    @Output() LoadPages: EventEmitter<any> = new EventEmitter<any>();
    @Output() reloadLessons = new EventEmitter<any>();

    @ViewChild(LessonDetailsMetadataPropertiesComponent) propertiesComponent: LessonDetailsMetadataPropertiesComponent;
    @ViewChild(LessonDetailsMetadataFormComponent) formComponent: LessonDetailsMetadataFormComponent;
    @ViewChild(LessonDetailsMetadataPagesFormComponent) pagesFormComponent: LessonDetailsMetadataPagesFormComponent;

    public isEditMode: boolean = false;
    public isEditPropertiesMode: boolean = false;
    public isSavingProperties: boolean = false;
    public isSavingMetadata: boolean = false;
    public isMetadataFormValid: boolean = true;
    public isPagesMetadataOpen: boolean = false;
    public isEditPagesMode: boolean = false;
    public isSavingPagesMetadata: boolean = false;
    public isPagesMetadataFormValid: boolean = true;

    constructor (
        private _infoMessage: InfoMessageService,
        private _myContent: MyContentService
    ) {}

    ngOnChanges () {
    }

    public onEditModeChange () {
        this.isEditMode = !this.isEditMode;

        if (this.isEditMode) {
            this.formComponent.edit();
        } else {
            this.formComponent.reset();
        }
    }

    public saveMetadata () {
        this.isSavingMetadata = true;
        this.formComponent.save().subscribe((data: Metadata) => {
                this.lesson.updateMetadata(data);
                this.metadata = data;
                this.metadataChange.emit(this.metadata);
                this._infoMessage.addSuccess('Lesson metadata saved successfully.');
                this.isSavingMetadata = false;
                this.isEditMode = false;
            },
            (error) => {
                console.error(error);
                this._infoMessage.addError('An error occured during saving lesson metadata.');
                this.lesson = this.lesson.copy();
                this.isSavingMetadata = false;
                this.isEditMode = false;
            });
    }

    public editPropertiesModeChange () {
        this.isEditPropertiesMode = !this.isEditPropertiesMode;

        if (this.isEditPropertiesMode) {
            this.propertiesComponent.edit();
        } else {
            this.propertiesComponent.reset();
        }
    }

    public saveProperties () {
        this.isSavingProperties = true;
        this.propertiesComponent.save().subscribe((properties: LessonProperties) => {
                this.lesson.updateProperties(properties);
                this._infoMessage.addSuccess('Lesson properties saved successfully.');
                this.isSavingProperties = false;
                this.isEditPropertiesMode = false;
                this.reloadLessons.emit();
            },
            (error) => {
                console.error(error);
                this._infoMessage.addError('An error occured during saving lesson properties.');
                this.lesson = this.lesson.copy();
                this.isSavingProperties = false;
                this.isEditPropertiesMode = false;
            });
    }

    public onIconChange (icon: FileData) {
        this.iconChange.emit(icon);
    }

    public isMetadataFormValidChanged (isValid: boolean) {
        this.isMetadataFormValid = isValid;
    }

    public onTogglePagesModeChange (isOpen: boolean) {
        this.isPagesMetadataOpen = isOpen;

        if (this.isPagesMetadataOpen) {
            this.LoadPages.emit(null);
        }
    }

    public onEditPagesModeChange () {
        this.isEditPagesMode = !this.isEditPagesMode;

        if (this.isEditPagesMode) {
            this.pagesFormComponent.edit();
        } else {
            this.pagesFormComponent.reset();
        }
    }

    public savePagesMetadata () {
        this.isSavingPagesMetadata = true;
        this.pagesFormComponent.save().subscribe((data) => {
            let pages = this.pages.map(page => page.copy());
            data.forEach(metadata => {
                const page = pages.find(p => p.id === metadata.id);
                if (page) {
                    page.updateMetadata(metadata);
                }
            });

            this._myContent.updateLessonPagesMetadata(this.lesson, pages).subscribe(() => {
                this._infoMessage.addSuccess('Lesson pages metadata saved successfully.');
                this.pages = pages;
                this.isSavingPagesMetadata = false;
                this.isEditPagesMode = false;
            },
            (error) => {
                console.error(error);
                this._infoMessage.addError('An error occured during saving lesson pages metadata.');
                this.pages = this.pages.map(page => page.copy());
                this.isSavingPagesMetadata = false;
                this.isEditPagesMode = false;
            });
        });
    }
}
