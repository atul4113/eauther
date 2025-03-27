import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { Observer } from "rxjs";
import { map } from "rxjs/operators";
import "rxjs/add/observable/of";

import { RestClientService } from "../../common/service/rest-client.service";
import {
    ILessonRaw,
    IMyAddonsRaw,
    IMyLessonsRaw,
    Lesson,
    LessonPage,
    LessonProperties,
    LessonsOrder,
    Metadata,
} from "../model/lesson";
import { FileStorage } from "../model/file-storage";
import { Asset } from "../model/asset";
import { MergeLesson } from "../model/merge-lesson";
import { EditToken } from "../model/edit-token";
import { FileData } from "../../common/model/upload-file";
import { Bug } from "../model/bug";

const MY_CONTENT_URL: string = "/my_content/";
const LESSONS_URL: string = MY_CONTENT_URL + "lessons";
const TRASH_URL: string = LESSONS_URL + "/trash";
const EDITED_LESSONS_URL: string = LESSONS_URL + "/edited";
const EDIT_LESSON_TOKEN_URL: string = MY_CONTENT_URL + "edit_lesson_token";
const EDIT_ADDON_TOKEN_URL: string = MY_CONTENT_URL + "edit_addon_token";
const LESSONS_PAGINATED_URL_SUFFIX: string = "lessons_paginated";
const TRASH_PAGINATED_URL_SUFFIX: string = "trash_paginated";
const LESSON_METADATA_SUFFIX: string = "/metadata";
const LESSON_BUGS_SUFFIX: string = "/bugs";

type TLessonsPage = { lessons: Lesson[]; moreCount: number };

@Injectable()
export class MyContentService {
    constructor(private _restClient: RestClientService) {}

    public getLessonDetails(id: number): Observable<Lesson> {
        return this._restClient
            .get(`${MY_CONTENT_URL}${id}`)
            .pipe(map((lesson:any) => new Lesson(lesson)));
    }

    public updateLessonIcon(lesson: Lesson, icon: FileData): Observable<any> {
        const data = {
            icon_id: icon.fileId,
        };

        return this._restClient.put(`${MY_CONTENT_URL}${lesson.id}`, data);
    }

    public getLessonMetadata(lessonId: number): Observable<Metadata> {
        const url = `${MY_CONTENT_URL}${lessonId}${LESSON_METADATA_SUFFIX}`;

        return this._restClient
            .get(url)
            .pipe(
                map((response: any) =>
                    Metadata.fromLesson(new Lesson(response))
                )
            );
    }

    public updateLessonMetadata(
        lesson: Lesson,
        metadata: Metadata
    ): Observable<any> {
        const url = `${MY_CONTENT_URL}${lesson.id}${LESSON_METADATA_SUFFIX}`;
        const data = {
            title: metadata.title,
            short_description: metadata.shortDescription,
            description: metadata.description,
            tags: metadata.tags,
            custom_values: metadata.customValues.map((custom) =>
                custom.raw(true)
            ),
        };

        return this._restClient.put(url, data);
    }

    public updateLessonProperties(
        lesson: Lesson,
        properties: LessonProperties
    ): Observable<any> {
        const data = {
            score_type: properties.scoreType,
            is_template: properties.isTemplate,
            enable_page_metadata: properties.enablePageMetadata,
            space_id: properties.spaceId,
            content_type: lesson.contentType.type,
        };

        return this._restClient.put(`${MY_CONTENT_URL}${lesson.id}`, data);
    }

    public getLessonAssets(lessonId: number): Observable<Asset[]> {
        return this._restClient.get(MY_CONTENT_URL + lessonId + "/assets").pipe(
            map((response:any) => {
                return response.assets.map((asset:any) => new Asset(asset));
            })
        );
    }

    public getLessonHistory(lessonId: number): Observable<FileStorage[]> {
        return this._restClient
            .get(MY_CONTENT_URL + lessonId + "/history")
            .pipe(
                map((response:any) => {
                    return response.map(
                        (fileStorage:any) => new FileStorage(fileStorage)
                    );
                })
            );
    }

    public getLessonPagesMetadata(lessonId: number): Observable<LessonPage[]> {
        const url = `${MY_CONTENT_URL}${lessonId}/pages_metadata`;

        return this._restClient
            .get(url)
            .pipe(
                map((response:any) => response.map((page:any) => new LessonPage(page)))
            );
    }

    public updateLessonPagesMetadata(
        lesson: Lesson,
        pages: LessonPage[]
    ): Observable<LessonPage[]> {
        const url = `${MY_CONTENT_URL}${lesson.id}/pages_metadata`;
        const data = pages.map((page) => page.raw());

        return this._restClient
            .put(url, data)
            .pipe(
                map((response:any) => response.map((page:any) => new LessonPage(page)))
            );
    }

    public getLessonBugs(lessonId: number): Observable<Bug[]> {
        const url = `${MY_CONTENT_URL}${lessonId}${LESSON_BUGS_SUFFIX}`;
        return this._restClient
            .get(url)
            .pipe(map((response:any) => response.map((bugRaw:any) => new Bug(bugRaw))));
    }

    public reportLessonBug(lesson: Lesson, bug: Bug): Observable<Bug> {
        const url = `${MY_CONTENT_URL}${lesson.id}${LESSON_BUGS_SUFFIX}`;
        return this._restClient.post(url, bug.raw());
    }

    public deleteLessonBug(lesson: Lesson, bug: Bug): Observable<any> {
        const url = `${MY_CONTENT_URL}${lesson.id}${LESSON_BUGS_SUFFIX}/${bug.id}`;
        return this._restClient.delete(url);
    }

    public getRecentlyEditedLessons(): Observable<Lesson[]> {
        return this._restClient.get(EDITED_LESSONS_URL).pipe(
            map((response:any) => {
                return response.content.map((lesson:any) => new Lesson(lesson));
            })
        );
    }

    public getLessons(
        cursor: any,
        spaceId:any
    ): Observable<{ lessons: Lesson[]; cursor: string; moreCount: number }> {
        const requestUrl = spaceId
            ? MY_CONTENT_URL + spaceId + "/lessons"
            : LESSONS_URL;

        return this._restClient
            .get(requestUrl + (cursor ? `?cursor=${cursor}` : ""))
            .pipe(
                map((response) => {
                    const data = <IMyLessonsRaw>response;
                    const lessons = data.lessons.map(
                        (lesson) => new Lesson(lesson)
                    );

                    return {
                        lessons: lessons,
                        cursor: data.cursor,
                        moreCount: data.more_count,
                    };
                })
            );
    }

    public getTrash(
        cursor: any,
        spaceId:any
    ): Observable<{ lessons: Lesson[]; cursor: string; moreCount: number }> {
        const requestUrl = spaceId
            ? MY_CONTENT_URL + spaceId + "/trash"
            : TRASH_URL;

        return this._restClient
            .get(requestUrl + (cursor ? `?cursor=${cursor}` : ""))
            .pipe(
                map((response) => {
                    const data = <IMyLessonsRaw>response;
                    const lessons = data.lessons.map(
                        (lesson) => new Lesson(lesson)
                    );

                    return {
                        lessons: lessons,
                        cursor: data.cursor,
                        moreCount: data.more_count,
                    };
                })
            );
    }

    public getAddons(
        cursor: any,
        spaceId:any
    ): Observable<{ addons: Lesson[]; cursor: string; moreCount: number }> {
        const requestUrl = spaceId
            ? MY_CONTENT_URL + spaceId + "/addons"
            : LESSONS_URL;

        return this._restClient
            .get(requestUrl + (cursor ? `?cursor=${cursor}` : ""))
            .pipe(
                map((response) => {
                    const data = <IMyAddonsRaw>response;
                    const addons = data.addons.map(
                        (addon) => new Lesson(addon)
                    );

                    return {
                        addons: addons,
                        cursor: data.cursor,
                        moreCount: data.more_count,
                    };
                })
            );
    }

    public getLessonsPage(
        pageNumber: number = 1,
        spaceId:any,
        order: LessonsOrder
    ): Observable<TLessonsPage> {
        const orderString = this.mapLessonsOrder(order);
        let url = `${LESSONS_PAGINATED_URL_SUFFIX}?page=${pageNumber}&${orderString}`;

        if (spaceId) {
            url = `${MY_CONTENT_URL}${spaceId}/${url}`;
        } else {
            url = `${MY_CONTENT_URL}${url}`;
        }

        return this._restClient.get(url).pipe(
            map((response: any) => {
                const lessons = response.lessons.map(
                    (lesson:any) => new Lesson(lesson)
                );
                return { lessons: lessons, moreCount: response.more_count };
            })
        );
    }

    public getAllLessons(spaceId?: any): Observable<Lesson[]> {
        return Observable.create((lessonsObserver: Observer<Lesson[]>) => {
            this.getLessonsInBatches(lessonsObserver, null, spaceId);
        });
    }

    public getAllAddons(spaceId?: any): Observable<Lesson[]> {
        return Observable.create((lessonsObserver: Observer<Lesson[]>) => {
            this.getAddonsInBatches(lessonsObserver, null, spaceId);
        });
    }

    public getLessonsInBatches(
        observer: Observer<Lesson[]>,
        cursor: any,
        spaceId:any
    ) {
        this.getLessons(cursor, spaceId).subscribe((data:any) => {
            observer.next(data.lessons);

            if (data.moreCount > 0) {
                this.getLessonsInBatches(observer, data.cursor, spaceId);
            } else {
                observer.complete();
            }
        });
    }

    public getAddonsInBatches(
        observer: Observer<Lesson[]>,
        cursor: any,
        spaceId:any
    ) {
        this.getAddons(cursor, spaceId).subscribe((data:any) => {
            observer.next(data.addons);

            if (data.moreCount > 0) {
                this.getAddonsInBatches(observer, data.cursor, spaceId);
            } else {
                observer.complete();
            }
        });
    }

    public getTrashPage(
        pageNumber: number = 1,
        spaceId: any
    ): Observable<TLessonsPage> {
        let url = `${TRASH_PAGINATED_URL_SUFFIX}?page=${pageNumber}`;

        if (spaceId) {
            url = `${MY_CONTENT_URL}${spaceId}/${url}`;
        } else {
            url = `${MY_CONTENT_URL}${url}`;
        }

        return this._restClient.get(url).pipe(
            map((response: any) => {
                const lessons = response.lessons.map(
                    (lesson:any) => new Lesson(lesson)
                );
                return { lessons: lessons, moreCount: response.more_count };
            })
        );
    }

    public getAllTrash(spaceId?: any): Observable<Lesson[]> {
        return Observable.create((lessonsObserver: Observer<Lesson[]>) => {
            this.getTrashLessonsInBatches(lessonsObserver, null, spaceId);
        });
    }

    public getTrashLessonsInBatches(
        observer: Observer<Lesson[]>,
        cursor: any,
        spaceId:any
    ) {
        this.getTrash(cursor, spaceId).subscribe((data:any) => {
            observer.next(data.lessons);

            if (data.moreCount > 0) {
                this.getTrashLessonsInBatches(observer, data.cursor, spaceId);
            } else {
                observer.complete();
            }
        });
    }

    public deleteLesson(contentId: any) {
        return this._restClient.delete(MY_CONTENT_URL + contentId + "/delete");
    }

    public undeleteLesson(contentId: any) {
        return this._restClient.post(MY_CONTENT_URL + contentId + "/undelete");
    }

    public deleteCorporateLesson(contentId: any) {
        return this._restClient.delete(
            MY_CONTENT_URL + "corporate/" + contentId + "/delete"
        );
    }

    public copyLesson(contentId: any, spaceId: any) {
        return this._restClient.post(
            MY_CONTENT_URL + contentId + "/" + spaceId + "/copy"
        );
    }

    public exportLesson(contentId: any, version: any) {
        return this._restClient.post(
            MY_CONTENT_URL + contentId + "/" + version + "/export"
        );
    }

    public publishLesson(contentId: any) {
        return this._restClient.post(
            MY_CONTENT_URL + contentId + "/makepublic"
        );
    }

    public unpublicLesson(contentId: any) {
        return this._restClient.delete(
            MY_CONTENT_URL + contentId + "/makepublic"
        );
    }

    public updateAssets(contentId: any) {
        return this._restClient.post(MY_CONTENT_URL + contentId + "/assets");
    }

    public updateTemplate(contentId: any, parameters: any) {
        return this._restClient.post(
            MY_CONTENT_URL + contentId + "/update_template",
            parameters
        );
    }

    public copyToAccount(contentId: any, parameters: any) {
        return this._restClient.post(
            MY_CONTENT_URL + contentId + "/copy_to_account",
            parameters
        );
    }

    public lessonList(
        contentId: any,
        spaceId: any
    ): Observable<{ pages: MergeLesson[]; commons: MergeLesson[] }> {
        return this._restClient
            .get(MY_CONTENT_URL + contentId + "/" + spaceId + "/page_list")
            .pipe(
                map((response:any) => {
                    return {
                        pages: response.pages_chapters.map(
                            (page:any) => new MergeLesson(page)
                        ),
                        commons: response.common_pages.map(
                            (page:any) => new MergeLesson(page)
                        ),
                    };
                })
            );
    }

    public merge(spaceId: any, parameters: any) {
        return this._restClient.post(
            MY_CONTENT_URL + spaceId + "/merge",
            parameters
        );
    }

    public getEditLessonToken(): Observable<EditToken> {
        return this._restClient
            .get(EDIT_LESSON_TOKEN_URL)
            .pipe(map((response:any) => new EditToken(response)));
    }

    public getEditAddonToken(): Observable<EditToken> {
        return this._restClient
            .get(EDIT_ADDON_TOKEN_URL)
            .pipe(map((response:any) => new EditToken(response)));
    }

    private mapLessonsOrder(order: LessonsOrder): string {
        let orderString = "";

        if (order.isNameUp() || order.isNameDown()) {
            orderString += "title=";
        } else if (order.isDateUp() || order.isDateDown()) {
            orderString += "modified_date=";
        }

        if (order.isNameUp() || order.isDateUp()) {
            orderString += "asc";
        } else if (order.isNameDown() || order.isDateDown()) {
            orderString += "desc";
        }

        return orderString;
    }

    public uploadAsset(contentId: any, parameters: any) {
        return this._restClient.post(
            MY_CONTENT_URL + contentId + "/upload_asset",
            parameters
        );
    }

    public uploadAssetPackage(contentId: any, parameters: any) {
        return this._restClient.post(
            MY_CONTENT_URL + contentId + "/upload_asset_package",
            parameters
        );
    }

    public setCurrentVersion(contentId: any, versionId: any) {
        return this._restClient.post(
            MY_CONTENT_URL + "set_version/" + contentId + "/" + versionId
        );
    }
}
