import { Injectable } from "@angular/core";
import { Observable, Observer } from "rxjs";
import { RestClientService } from "./rest-client.service";
import { map , tap, catchError, share } from 'rxjs/operators';
import "rxjs/add/observable/of";

import { ISpaceRaw, Space } from "../model/space";
import { Subspace } from "../model/subspace";
import { RolePermissions } from "../model/auth-user";

const PROJECTS_URL: string = '/projects/';

@Injectable()
export class ProjectsService {
    private projects: Space[];
    private projectsWithPublications: Space[];
    private observe: Observable<any>;
    private changeObserve: Observable<Space[]>;
    private changeObserver: Observer<Space[]>;

    constructor (private _restClient: RestClientService) {
        this.load();
    }

    private mapProjects (response: any) {
        let spaces = <ISpaceRaw[]> response;
        return spaces.map(space => new Space(space));
    }

    private handleError (error: string): Observable<Space[]> {
        return Observable.of([]);
    }

    public get (): Observable<Space[]> {
        if (this.projects) {
            return Observable.of(this.projects);
        } else if (this.observe){
            return this.observe;
        } else {
            return null;
        }
    }

    public onChange (): Observable<Space[]> {
        return this.changeObserve;
    }

    public getPublications (projectId): Observable<Space[]> {
        return this._restClient.get(PROJECTS_URL + projectId + '/publications').pipe(
            map(response => {
                return response.map(publication => new Space(publication));
            })
        );
    }

    public getStructure (spaceId, recursive: boolean = false): Observable<Subspace> {
        if(recursive) {
            return this._restClient.get(PROJECTS_URL + spaceId + '/structure?recursive=true').pipe(
                map(response => new Subspace(response))
            );
        }else{
            return this._restClient.get(PROJECTS_URL + spaceId + '/structure').pipe(
                map(response => new Subspace(response))
            );
        }
    }

    private load () {
        this.observe =
            this._restClient
                .get(PROJECTS_URL)
                .pipe(
                    map(this.mapProjects),
                    catchError(this.handleError),
                    share()
                );

        this.observe
            .subscribe(projects => this.projects = projects);

        this.changeObserve =
            Observable.create( (observer: Observer<Space[]>) => {
                this.changeObserver = observer;
            }).pipe(
                share()
            );
    }


    public projectForPublication(spaceId: any) {
        return this._restClient.get(PROJECTS_URL + spaceId + '/get_project').pipe(
            map(response => new Space(response))
        );
    }

    public getSpacePermissions(spaceId: any) {
        return this._restClient.get(PROJECTS_URL + "permissions/" + spaceId).pipe(
            map(permissions => new RolePermissions(permissions))
        );
    }
}
