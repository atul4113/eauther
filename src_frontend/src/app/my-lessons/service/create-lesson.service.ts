import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';

import {map} from 'rxjs/operators';
import 'rxjs/add/observable/of';

import {RestClientService} from '../../common/service/rest-client.service';
import { Lesson, SimpleLesson,} from '../model/lesson';

const CREATE_LESSON_URL: string = '/create_lesson/';

@Injectable()
export class CreateLessonService {

    constructor(
        private _restClient: RestClientService
    ) {}

    public getTemplates(): Observable<Lesson[]> {
        return this._restClient.get(CREATE_LESSON_URL + "templates").pipe(
            map(response => {
                return response.content.map((lesson:any) => new Lesson(lesson));
            })
        );
    }

    public getSimpleTemplates(): Observable<SimpleLesson[]> {
        return this._restClient.get(CREATE_LESSON_URL + "simpletemplates").pipe(
            map(response => {
                return response.content.map((simpleTemplate:any) => new SimpleLesson(simpleTemplate))
            })
        );
    }

    public createLesson(parameters: any) {
        return this._restClient.post(CREATE_LESSON_URL + "create", parameters);
    }
}
