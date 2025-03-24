import { Injectable } from "@angular/core";
import { Observable, Subject } from "rxjs";
import { share, filter } from "rxjs/operators";

import { InfoMessage, INFO_MESSAGE_TYPE } from "../model/info-message";

@Injectable()
export class InfoMessageService {
    private messages: InfoMessage[] = [];
    private readonly messageSubject = new Subject<InfoMessage | null>();
    private readonly errorSubject = new Subject<number>();
    private readonly message$: Observable<InfoMessage>;
    private readonly error$: Observable<number>;

    constructor() {
        this.message$ = this.messageSubject.asObservable().pipe(
            filter((message): message is InfoMessage => message !== null),
            share()
        );
        this.error$ = this.errorSubject.asObservable().pipe(share());

        // Subscribe to keep the observables hot
        this.message$.subscribe();
        this.error$.subscribe();
    }

    public init(): void {} // method for forcing service initialization

    public addSuccess(
        message: string,
        closeable = true,
        autoClose = true
    ): void {
        this.addMessage(
            new InfoMessage(
                INFO_MESSAGE_TYPE.SUCCESS,
                message,
                closeable,
                autoClose
            )
        );
    }

    public addError(message: string, closeable = true, autoClose = true): void {
        this.addMessage(
            new InfoMessage(
                INFO_MESSAGE_TYPE.ERROR,
                message,
                closeable,
                autoClose
            )
        );
    }

    public addWarning(
        message: string,
        closeable = true,
        autoClose = true
    ): void {
        this.addMessage(
            new InfoMessage(
                INFO_MESSAGE_TYPE.WARNING,
                message,
                closeable,
                autoClose
            )
        );
    }

    public addInfo(message: string, closeable = true, autoClose = true): void {
        this.addMessage(
            new InfoMessage(
                INFO_MESSAGE_TYPE.INFO,
                message,
                closeable,
                autoClose
            )
        );
    }

    public clear(): void {
        this.messageSubject.next(null);
    }

    public error500(): void {
        this.errorSubject.next(500);
    }

    public error404(): void {
        this.errorSubject.next(404);
    }

    public errors(): Observable<number> {
        return this.error$;
    }

    public get(): Observable<InfoMessage> {
        return this.message$;
    }

    public getAll(): InfoMessage[] {
        return this.messages;
    }

    private addMessage(message: InfoMessage): void {
        this.messages.push(message);
        this.messageSubject.next(message);
    }
}
