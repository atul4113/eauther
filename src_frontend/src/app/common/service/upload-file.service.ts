import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { map } from "rxjs/operators";

import { RestClientService } from "./rest-client.service";

interface IUploadUrlResponse {
    upload_url: string;
}

const FILE_UPLOAD_URL = "/file/upload";

@Injectable()
export class UploadFileService {
    constructor(private readonly _restClient: RestClientService) {}

    public getUploadUrl(): Observable<string> {
        return this._restClient
            .get<IUploadUrlResponse>(FILE_UPLOAD_URL)
            .pipe(map(this.mapUploadUrl));
    }

    private mapUploadUrl(response: IUploadUrlResponse): string {
        return response.upload_url;
    }
}
