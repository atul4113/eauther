import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { map } from "rxjs/operators";

import { RestClientService } from "./rest-client.service";
import { News, INewsRaw } from "../model/news";

const NEWS_URL = "/news/";

@Injectable()
export class NewsService {
    constructor(private readonly _restClient: RestClientService) {}

    public get(): Observable<News[]> {
        return this._restClient.get<INewsRaw[]>(NEWS_URL).pipe(
            map((response) =>
                response.map((news) => {
                    return new News(news);
                })
            )
        );
    }
}
