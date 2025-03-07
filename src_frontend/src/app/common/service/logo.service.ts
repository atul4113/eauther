import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { map } from "rxjs/operators";

import { RestClientService } from "./rest-client.service";

const LOGO_URL: string = "/user/logo";

@Injectable()
export class LogoService {
    constructor(private _restClient: RestClientService) {}

    public get(): Observable<number> {
        return this._restClient.get(LOGO_URL).pipe((logo) => {
            return logo;
        });
    }
}
