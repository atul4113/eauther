import { Component, EventEmitter, Input, OnChanges, OnInit, Output } from '@angular/core';
import { MatTabChangeEvent } from "@angular/material/tabs";

import { Lesson, LessonPage, Metadata } from "../../model/lesson";
import { FileStorage } from "../../model/file-storage";
import { Asset } from "../../model/asset";
import { Bug } from "../../model/bug";
import { AuthUser, FileData, ITranslations } from "../../../common/model";
import { InfoMessageService } from "../../../common/service";
import { MyContentService } from "../../service/my-content.service";
import { RolePermissions } from "../../../common/model/auth-user";

enum TABS { METADATA, ASSETS, BUG_TRACK, HISTORY }

@Component({
    selector: 'app-lesson-details',
    templateUrl: './lesson-details.component.html'
})
export class LessonDetailsComponent implements OnInit, OnChanges {
    @Input() user!: AuthUser;
    @Input() translations!: ITranslations;
    @Input() lesson!: Lesson;
    @Input() isProject!: boolean;
    @Input() publicationName!: string;
    @Input() userPermissions!: RolePermissions;
    @Input() isView: boolean = false;
    @Output() hideDetailsEvent = new EventEmitter<void>();
    @Output() reloadLessons = new EventEmitter<void>();

    public versions: FileStorage[] = [];
    public assets: Asset[] = [];
    public isInitialized: boolean = false;

    public Tabs = TABS;
    public activeTab: TABS = TABS.METADATA;

    public lessonDetails!: Lesson;
    public lessonPages: LessonPage[] = [];
    public metadata: Metadata = {} as Metadata;
    public assetsLoaded: boolean = false;

    public get isMetadataTabActive(): boolean {
        return this.activeTab === this.Tabs.METADATA;
    }
    public get isAssetsTabActive(): boolean {
        return this.activeTab === this.Tabs.ASSETS;
    }
    public get isBugTackTabActive(): boolean {
        return this.activeTab === this.Tabs.BUG_TRACK;
    }
    public get isHistoryTabActive(): boolean {
        return this.activeTab === this.Tabs.HISTORY;
    }

    public bugToDelete: Bug | null = null;
    public isPopupVisible: boolean = false;
    public bugs: Bug[] = [];

    constructor(
        private _myContent: MyContentService,
        private _infoMessage: InfoMessageService,
    ) {}

    ngOnInit(): void {}

    ngOnChanges(): void {
        this.isInitialized = false;
        this.metadata = {} as Metadata;
        this.lessonPages = [];
        this.versions = [];
        this.activeTab = this.Tabs.METADATA;

        if (this.lesson) {
            this._myContent.getLessonDetails(this.lesson.id).subscribe((lesson: Lesson) => {
                this.lessonDetails = lesson;
                this.isInitialized = true;

                this._myContent.getLessonHistory(this.lesson.id).subscribe((versions: FileStorage[]) => {
                    this.versions = versions;
                });

                this._myContent.getLessonMetadata(this.lesson.id).subscribe((metadata: Metadata) => {
                    this.metadata = metadata;
                });
                this._myContent.getLessonBugs(this.lesson.id).subscribe((bugs: Bug[]) => {
                    this.bugs = bugs.sort((a: Bug, b: Bug) => this.findTheNewest(a, b));
                });
            });
        }
    }

    public onTabChange(tab: TABS): void {
        this.activeTab = tab;

        if (this.isHistoryTabActive) {
            this._myContent.getLessonHistory(this.lesson.id).subscribe((versions: FileStorage[]) => {
                this.versions = versions;
            });
        } else if (this.isAssetsTabActive) {
            this._myContent.getLessonAssets(this.lesson.id).subscribe((assets: Asset[]) => {
                this.assets = assets;
                this.assetsLoaded = true;
            });
        }
    }

    public hideDetails(): void {
        this.hideDetailsEvent.emit();
    }

    public onIconChange(icon: FileData): void {
        this.lesson.iconHref = icon.link;
    }

    public onMetadataChange(data: Metadata): void {
        this.lesson.updateMetadata(data);
    }

    public changePublishInfo(): void {
        this.lessonDetails.togglePublic();
    }

    public onLoadPages(): void {
        if (!this.lessonPages.length) {
            this._myContent.getLessonPagesMetadata(this.lesson.id).subscribe((lessonPages: LessonPage[]) => {
                this.lessonPages = lessonPages;
            });
        }
    }

    public reloadLessonsSignal(): void {
        this.reloadLessons.emit();
    }

    public onBugDelete(bug: Bug): void {
        this.bugToDelete = bug;
        this.isPopupVisible = true;
    }

    public onDeleteBugAccept(): void {
        if (!this.bugToDelete) return;
        
        this._infoMessage.addInfo('Deleting comment...', false);
        this._myContent.deleteLessonBug(this.lesson, this.bugToDelete).subscribe(
            () => {
                this.bugs = this.bugs.filter(b => b.id !== this.bugToDelete?.id);
                this.bugToDelete = null;
                this._infoMessage.addSuccess('Lesson comment deleted successfully.');
            },
            (error: unknown) => {
                console.error(error);
                this.bugToDelete = null;
                this._infoMessage.addError('An error occurred during deleting lesson comment.');
            });
    }

    public onDeleteBugReject(): void {
        this.bugToDelete = null;
    }

    public onBugReport(bug: Bug): void {
        this._infoMessage.addInfo('Adding comment...', false);
        this._myContent.reportLessonBug(this.lesson, bug).subscribe(
            (receivedBug: Bug) => {
                receivedBug.createdDate = bug.createdDate;
                this.bugs = [receivedBug, ...this.bugs];
                this._infoMessage.addSuccess('Lesson comment added successfully.');
                setTimeout(() => { this._infoMessage.clear(); }, 3000);
            },
            (error: unknown) => {
                console.error(error);
                this._infoMessage.addError('An error occurred during adding lesson comment.');
            });
    }

    private findTheNewest(a: Bug, b: Bug): number {
        return b.createdDate.getTime() - a.createdDate.getTime();
    }
}
