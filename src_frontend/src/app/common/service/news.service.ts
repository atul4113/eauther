import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { map } from "rxjs/operators";

import { RestClientService } from "./rest-client.service";
import { News } from "../model/news";

const NEWS_URL: string = "/news/";

@Injectable()
export class NewsService {
    constructor(private _restClient: RestClientService) {}

    public get(): Observable<News[]> {
        return this._restClient.get(NEWS_URL).pipe(
            map((response) => {
                return response.map((news) => new News(news));
            })
        );
    }
}
