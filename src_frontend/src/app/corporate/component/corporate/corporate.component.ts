import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/observable/forkJoin';

import { News, AuthUser, Space, ITranslations } from '../../../common/model';
import { Lesson } from '../../../my-lessons/model/lesson';
import { EditToken } from "../../../my-lessons/model/edit-token";
import {
    AuthUserService,
    ProjectsService,
    NewsService,
    TranslationsService,
    CookieService
} from '../../../common/service';
import { MyContentService } from '../../../my-lessons/service/my-content.service';


declare var window: any;

@Component({
    templateUrl: './corporate.component.html',
    providers: [MyContentService, NewsService]
})
export class CorporateComponent implements OnInit {
    public error: boolean = false;
    public projects: Space[];
    public editLessonToken: EditToken;
    public areTilesHidden: boolean = false;
    public structure: any;
    public user: AuthUser;
    public isInitialized = false;
    public privateSpace: Space;
    public editedLessons: Lesson[];
    public allNews: News[];
    public assetsUrl: string = window.mAuthorAssetsUrl;
    public translations: ITranslations;


    constructor (
        private _user: AuthUserService,
        private _projects: ProjectsService,
        private _myContent: MyContentService,
        private _news: NewsService,
        private _translations: TranslationsService,
        private _cookie: CookieService
    ) {}

    ngOnInit () {

        this._translations.getTranslations().subscribe(t => this.translations = t);

        this._user.get().subscribe(user => {
            this.user = user;
            this.privateSpace = this.user.privateSpace;
            this.isInitialized = true;
        });

        Observable.forkJoin(
            this._myContent.getRecentlyEditedLessons(),
            this._myContent.getEditLessonToken()
        )
        .subscribe(([editedLessons, editLessonToken]) => {
            this.editLessonToken = editLessonToken;
            this.editedLessons = editedLessons;
        });

        this._news.get().subscribe(news => {
            this.allNews = news;
        });

        this._projects.get().subscribe(projects => {
            this.projects = projects;
            this.projects.forEach((project) => {
                project.publications = undefined;
            });
            this.projects.sort((a: Space, b: Space) => a.title.localeCompare(b.title));

        });

        this.detectTilesVisibility();
    }

    public getLastEditedLessonId () {
        if (this.editedLessons && this.editedLessons.length > 0) {
            return this.editedLessons[0];
        } else {
            return null;
        }
    }

    public detectTilesVisibility() {
        const cookieTiles = this._cookie.get('shouldShowTiles' + this.user.id);
        if (cookieTiles !== undefined) {
            cookieTiles == "true" ? this.showTiles() : this.hideTiles();
        } else {
            this.showTiles();
        }
    }

    public setTilesVisibility (value) {
        let dateYearPlus = new Date();
        dateYearPlus.setTime(dateYearPlus.getTime() + (365 * 24 * 3600 * 1000));
        this._cookie.put('shouldShowTiles' + this.user.id, value, {expires: dateYearPlus});
    }

    public showTiles () {
        this.areTilesHidden = false;
        this.setTilesVisibility(!this.areTilesHidden);
    }

    public hideTiles () {
        this.areTilesHidden = true;
        this.setTilesVisibility(!this.areTilesHidden);
    }
}
