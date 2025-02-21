import { Injectable } from '@angular/core';
import { Observable, Observer } from 'rxjs';
import { share } from 'rxjs/operators';

import { InfoMessage, INFO_MESSAGE_TYPE } from '../model/info-message';


@Injectable()
export class InfoMessageService {
    private messages: InfoMessage[] = [];
    private observer: Observer<InfoMessage>;
    private observable: Observable<InfoMessage>;
    private errorObserver: Observer<number>;
    private errorObservable: Observable<number>;

    constructor () {
        this.observable = Observable.create((observer: Observer<InfoMessage>) => {
            this.observer = observer;
        }).pipe(
            share()
        );

        this.errorObservable = Observable.create((observer: Observer<number>) => {
            this.errorObserver = observer;
        }).pipe(
            share()
        );

        this.observable.subscribe();
        this.errorObservable.subscribe();
    }

    public init () {} // method for forcing service initialization

    public addSuccess (message: string, closeable = true, autoClose = true) {
        this.addMessage(new InfoMessage(INFO_MESSAGE_TYPE.SUCCESS, message, closeable, autoClose));
    }

    public addError (message: string, closeable = true, autoClose = true) {
        this.addMessage(new InfoMessage(INFO_MESSAGE_TYPE.ERROR, message, closeable, autoClose));
    }

    public addWarning (message: string, closeable = true, autoClose = true) {
        this.addMessage(new InfoMessage(INFO_MESSAGE_TYPE.WARNING, message, closeable, autoClose));
    }

    public addInfo (message: string, closeable = true, autoClose = true) {
        this.addMessage(new InfoMessage(INFO_MESSAGE_TYPE.INFO, message, closeable, autoClose));
    }

    public clear () {
        this.observer.next(null);
    }

    public error500 () {
        this.errorObserver.next(500);
    }

    public error404 () {
        this.errorObserver.next(404);
    }

    public errors (): Observable<number> {
        return this.errorObservable;
    }

    public get (): Observable<InfoMessage> {
        return this.observable;
    }

    public getAll (): InfoMessage[] {
        return this.messages;
    }

    private addMessage (message: InfoMessage) {
        this.messages.push(message);

        this.observer.next(message);
    }
}
