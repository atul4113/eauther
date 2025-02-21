import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { map } from "rxjs/operators";

import { RestClientService } from "./rest-client.service";


const FILE_UPLOAD_URL = '/file/upload';

@Injectable()
export class UploadFileService {

    constructor(
        private _restClient: RestClientService
    ) {}

    public getUploadUrl (): Observable<string> {
        return this._restClient.get(FILE_UPLOAD_URL).pipe(
            map(this.mapUploadUrl)
        );
    }

    private mapUploadUrl (response: any): string {
        let data: {upload_url: string} = <{upload_url: string}> response;

        return data.upload_url;
    }

}
