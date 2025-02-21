import { Injectable } from '@angular/core';
import { Http, Response, Headers, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import { Observer } from 'rxjs/Observer';
import { map, catchError } from 'rxjs/operators';
import "rxjs/add/observable/throw";

import { TokenService } from './token.service';
import { InfoMessageService } from './info-message.service';


const API_URL: string = '/api/v2';
export const UNAUTHORIZED_ERROR: string = 'Unauthorized';
const SERVER_RESPONSE_STATUS = {
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,

    INTERNAL_SERVER_ERROR: 500
};
const REQUEST_TYPES = {
    GET: 'get',
    POST: 'post',
    PUT: 'put',
    COPY: 'copy',
    DELETE: 'delete'
};

@Injectable()
export class RestClientService {
    constructor (
        private _http: Http,
        private _token: TokenService,
        private _infoMessage: InfoMessageService
    ) {}

    public get (url: string): Observable<any> {
        return this.requestWithToken(this.getOptions, this.handleError, REQUEST_TYPES.GET, url);
    }

    public getPublic(url: string): Observable<any> {
        return this._http
            .get(API_URL + url, this.getOptions())
            .pipe(
                map(this.extractData),
                catchError(error => this.handleError(error, this))
            );

    }

    public post (url: string, params: any = {}) {
        return this.requestWithToken(this.getPostOptions, this.handlePostError, REQUEST_TYPES.POST, url, params);
    }

    public postPublic (url: string, params: any) {
      return this._http
        .post(API_URL + url, JSON.stringify(params), this.getPostOptions())
        .pipe(
            map(this.extractData),
            catchError(error => this.handlePostError(error, this))
        );
    }

    public put (url: string, params: any) {
        return this.requestWithToken(this.getPostOptions, this.handlePostError, REQUEST_TYPES.PUT, url, params);
    }

    public putPublic (url: string, params: any = {}) {
        return this._http
            .put(API_URL + url, JSON.stringify(params), this.getPostOptions())
            .pipe(
                map(this.extractData),
                catchError(error => this.handlePostError(error, this))
            );
    }

    public delete (url: string) {
        return this.requestWithToken(this.getOptions, this.handlePostError, REQUEST_TYPES.DELETE, url);
    }

    private extractData(res: Response) {
        if (res.status < 200 || res.status >= 300) {
            throw new Error('BAD RESPONSE STATUS: ' + res.status);
        }
        if (res) {
            try {
                return res.json();
            } catch (e) {}
        }
        return null;
    }


    private handleError (error: any, that: RestClientService) {
        let errMsg = error.status || 'Server error';
        console.error("RestClientService ERROR: ", errMsg);
        if (error.status === SERVER_RESPONSE_STATUS.INTERNAL_SERVER_ERROR) {
            that._infoMessage.error500();
        }
        return Observable.throw(error);
    }

    private handlePostError (error: any, that: RestClientService) {
        let errMsg = error.status || 'Server error';
        console.error("RestClientService ERROR: ", errMsg);
        error.body = JSON.parse(error._body);
        if (error.status === SERVER_RESPONSE_STATUS.INTERNAL_SERVER_ERROR) {
            that._infoMessage.error500();
        }
        return Observable.throw(error);
    }

    private getOptions (headers = {}): RequestOptions {
        headers['Accept'] = 'application/json';
        return new RequestOptions({ 'headers': new Headers(headers) });
    }

    private getPostOptions (headers = {}): RequestOptions {
        headers['Accept'] = 'application/json';
        headers['Content-Type'] = 'application/json';
        return new RequestOptions({ 'headers': new Headers(headers) });
    }

    private getTokenHeader (token: string) {
        return {"Authorization": "JWT " + token};
    }

    /*
       1. get token,
       2. if there is no token then throw Unauthorized error,
       3. else do request with header: Authorization: JWT(space)token,
       4. if request fails and error's status is 401 (Unauthorized) then
            clear old token and redo request,
       5. else let error to be raised.
     */
    private requestWithToken (getOptions: ((header: any) => RequestOptions), handleError: ((error: any, that: RestClientService) => Observable<any>), methodName: string, ...params: any[]): Observable<any> {
        return Observable.create( (observer: Observer<any>) => {
            this._token.get().subscribe(
                (token: string) => {
                    if (!token) {
                        observer.error(UNAUTHORIZED_ERROR);
                    } else {
                        let options = this.getRequestOptions(methodName, getOptions(this.getTokenHeader(token)), ...params);
                        this._http
                            .request(API_URL + params[0], options)
                            .pipe(
                                map(this.extractData),
                                catchError(error => handleError(error, this))
                            ).subscribe(data => {
                                observer.next(data);
                                observer.complete();
                            },
                            error => {
                                if (parseInt(error.status) === SERVER_RESPONSE_STATUS.UNAUTHORIZED) {
                                    this._token.clear();
                                    this[methodName](...params).pipe(
                                        catchError(error => handleError(error, this))
                                    ).subscribe(
                                        data => {
                                            observer.next(data);
                                            observer.complete();
                                        },
                                        error => {
                                            observer.error(error);
                                        }
                                    );
                                } else {
                                    observer.error(error);
                                }
                            });
                    }
                }
            );
        });
    }

    private getRequestOptions (methodName: string, options: RequestOptions, ...params: any[]): RequestOptions {
        options.method = methodName;
        if (params.length > 1) {
            options.body = params[1];
        }

        return options;
    }
}
