import { Component, EventEmitter, Input, OnChanges, OnInit, Output } from '@angular/core';
import { MatTabChangeEvent } from "@angular/material";

import { Lesson, LessonPage, Metadata } from "../../model/lesson";
import { FileStorage } from "../../model/file-storage";
import { Asset } from "../../model/asset";
import {Bug} from "../../model/bug";
import {AuthUser, FileData, ITranslations} from "../../../common/model";
import {InfoMessageService} from "../../../common/service";
import { MyContentService } from "../../service/my-content.service";
import { RolePermissions } from "../../../common/model/auth-user";

enum TABS { METADATA, ASSETS, BUG_TRACK, HISTORY }

@Component({
    selector: 'app-lesson-details',
    templateUrl: './lesson-details.component.html'
})
export class LessonDetailsComponent implements OnInit, OnChanges {
    @Input() user: AuthUser;
    @Input() translations: ITranslations;
    @Input() lesson: Lesson = null;
    @Input() isProject: boolean;
    @Input() publicationName: string;
    @Input() userPermissions: RolePermissions;
    @Input() isView :boolean = false;
    @Output() hideDetailsEvent = new EventEmitter<any>();
    @Output() reloadLessons = new EventEmitter<any>();

    public versions: FileStorage[] = [];
    public assets: Asset[] = [];
    public isInitialized: boolean = false;

    public Tabs = TABS;
    public activeTab: TABS = TABS.METADATA;

    public lessonDetails: Lesson;
    public lessonPages: LessonPage[];
    public metadata: Metadata;
    public assetsLoaded: boolean = false;

    public get isMetadataTabActive (): boolean {
        return this.activeTab === this.Tabs.METADATA;
    }
    public get isAssetsTabActive (): boolean {
        return this.activeTab === this.Tabs.ASSETS;
    }
    public get isBugTackTabActive (): boolean {
        return this.activeTab === this.Tabs.BUG_TRACK;
    }
    public get isHistoryTabActive (): boolean {
        return this.activeTab === this.Tabs.HISTORY;
    }

    public bugToDelete: Bug = null;
    public isPopupVisible: Boolean = false;

    public bugs: Bug[];

    constructor(
        private _myContent: MyContentService,
        private _infoMessage: InfoMessageService,
    ) {}

    ngOnInit () {}

    ngOnChanges() {
        this.isInitialized = false;
        this.metadata = null;
        this.lessonPages = null;
        this.versions = null;
        this.activeTab = this.Tabs.METADATA;

        if (this.lesson) {
            this._myContent.getLessonDetails(this.lesson.id).subscribe(lesson => {
                this.lessonDetails = lesson;
                this.isInitialized = true;

                this._myContent.getLessonHistory(this.lesson.id).subscribe(versions => {
                    this.versions = versions;
                });

                this._myContent.getLessonMetadata(this.lesson.id).subscribe(metadata => {
                    this.metadata = metadata;
                });
                this._myContent.getLessonBugs(this.lesson.id).subscribe(bugs => {
                    this.bugs = bugs.sort((a,b) => this.findTheNewest(a,b));
                });
            });
        }
    }

    public onTabChange (tab: TABS) {
        this.activeTab =  tab;

        if (this.isHistoryTabActive) {
            this._myContent.getLessonHistory(this.lesson.id).subscribe(versions => {
                this.versions = versions;
            });
        } else if (this.isAssetsTabActive) {
            this._myContent.getLessonAssets(this.lesson.id).subscribe(assets => {
                this.assets = assets;
                this.assetsLoaded = true;
            });
        }
    }

    public hideDetails() {
        this.hideDetailsEvent.emit();
    }

    public onIconChange(icon: FileData) {
        this.lesson.iconHref = icon.link;
    }

    public onMetadataChange(data: Metadata) {
        this.lesson.updateMetadata(data);
    }

    public changePublishInfo() {
        this.lessonDetails.togglePublic();
    }

    public onLoadPages() {
        if (!this.lessonPages) {
            this._myContent.getLessonPagesMetadata(this.lesson.id).subscribe(lessonPages => {
                this.lessonPages = lessonPages;
            });
        }
    }

    public reloadLessonsSignal() {
        this.reloadLessons.emit();
    }

    public onBugDelete (bug: Bug) {
        this.bugToDelete = bug;
        this.isPopupVisible = true;
    }

    public onDeleteBugAccept (event) {
        this._infoMessage.addInfo('Deleting comment...', false);
        this._myContent.deleteLessonBug(this.lesson, this.bugToDelete).subscribe(
            () => {
                this.bugs = this.bugs.filter(b => b.id !== this.bugToDelete.id);
                this.bugToDelete = null;
                this._infoMessage.addSuccess('Lesson comment deleted successfully.');
            },
            (error) => {
                console.error(error);
                this.bugToDelete = null;
                this._infoMessage.addError('An error occurred during deleting lesson comment.');
            });
    }

    public onDeleteBugReject (event) {
        this.bugToDelete = null;
    }

    public onBugReport (bug: Bug) {
        this._infoMessage.addInfo('Adding comment...', false);
        this._myContent.reportLessonBug(this.lesson, bug).subscribe(
            (receivedBug) => {
                receivedBug.createdDate = bug.createdDate;
                this.bugs = [receivedBug, ...this.bugs];
                this._infoMessage.addSuccess('Lesson comment added successfully.');
                setTimeout(() =>{ this._infoMessage.clear(); }, 3000);
            },
            (error) => {
                console.error(error);
                this._infoMessage.addError('An error occurred during adding lesson comment.');
            });
    }

    private findTheNewest (a: Bug,b: Bug) {
        return b.createdDate.getTime() - a.createdDate.getTime();
    }

}
