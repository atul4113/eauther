import {Injectable} from '@angular/core';
import {Observable} from 'rxjs/Observable';
import {Observer} from 'rxjs/Observer';
import {map} from 'rxjs/operators';
import 'rxjs/add/observable/of';

import {RestClientService} from '../../common/service/rest-client.service';
import {
    ILessonRaw, IMyLessonsRaw, Lesson, LessonPage, LessonProperties,
    LessonsOrder, Metadata, SimpleLesson,
} from '../model/lesson';
import {FileStorage} from '../model/file-storage';
import {Asset} from '../model/asset';
import {MergeLesson} from '../model/merge-lesson';
import {EditToken} from '../model/edit-token';
import {FileData} from "../../common/model/upload-file";
import {Bug} from "../model/bug";

const CREATE_LESSON_URL: string = '/create_lesson/';

@Injectable()
export class CreateLessonService {

    constructor(
        private _restClient: RestClientService
    ) {}

    public getTemplates(): Observable<Lesson[]> {
        return this._restClient.get(CREATE_LESSON_URL + "templates").pipe(
            map(response => {
                return response.content.map(lesson => new Lesson(lesson));
            })
        );
    }

    public getSimpleTemplates(): Observable<SimpleLesson[]> {
        return this._restClient.get(CREATE_LESSON_URL + "simpletemplates").pipe(
            map(response => {
                return response.content.map(simpleTemplate => new SimpleLesson(simpleTemplate))
            })
        );
    }

    public createLesson(parameters: any) {
        return this._restClient.post(CREATE_LESSON_URL + "create", parameters);
    }
}
