import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { map } from "rxjs/operators";

import { RestClientService } from "./rest-client.service";
import { Category } from "../model/category";

const CATEGORIES_URL: string = "/my_content/categories";

@Injectable()
export class CategoriesService {
    constructor(private _restClient: RestClientService) {}

    public get(): Observable<Category[]> {
        return this._restClient.get(CATEGORIES_URL).pipe(
            map((response) => {
                return response.map((category) => new Category(category));
            })
        );
    }
}
