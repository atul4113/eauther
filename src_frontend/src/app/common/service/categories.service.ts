import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { map } from "rxjs/operators";

import { RestClientService } from "./rest-client.service";
import { Category, ICategoryRaw } from "../model/category";

const CATEGORIES_URL = "/my_content/categories";

@Injectable()
export class CategoriesService {
    constructor(private readonly _restClient: RestClientService) {}

    public get(): Observable<Category[]> {
        return this._restClient
            .get<ICategoryRaw[]>(CATEGORIES_URL)
            .pipe(
                map((response) =>
                    response.map((category) => new Category(category))
                )
            );
    }
}
