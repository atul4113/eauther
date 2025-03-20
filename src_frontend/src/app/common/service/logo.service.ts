import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { map } from "rxjs/operators";

import { RestClientService } from "./rest-client.service";

const LOGO_URL = "/user/logo";

@Injectable()
export class LogoService {
    constructor(private readonly _restClient: RestClientService) {}

    public get(): Observable<number> {
        return this._restClient.get<number>(LOGO_URL).pipe(map((logo) => logo));
    }
}
