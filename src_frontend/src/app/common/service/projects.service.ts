import { Injectable } from "@angular/core";
import { Observable, Subject, of } from "rxjs";
import { RestClientService } from "./rest-client.service";
import { map, tap, catchError, share } from "rxjs/operators";

import { ISpaceRaw, Space } from "../model/space";
import { Subspace } from "../model/subspace";
import { RolePermissions } from "../model/auth-user";

const PROJECTS_URL = "/projects/";

interface ISubspaceResponse {
    id: number;
    name: string;
    subspaces?: ISubspaceResponse[];
}

type PermissionValue = (typeof PERMISSIONS)[keyof typeof PERMISSIONS];

const PERMISSIONS = {
    assetsBrowseAssets: 1,
    assetsUploadEditAssets: 2,
    assetsRemoveAssets: 3,
    contentViewLessonsAddons: 4,
    contentRemoveLessonsAddons: 5,
    contentEditMetadataOfLessonsAddons: 6,
    contentPublishLessons: 7,
    contentCopyLessons: 8,
    contentCreateEditLessonsAddons: 9,
    contentUploadLessonsAddonsIcon: 10,
    contentShowLessonsHistory: 11,
    contentSetLessonsCurrentVersion: 12,
    contentExportLessons: 13,
    contentImportLessons: 14,
    spaceManageAccessToProjectsPublications: 15,
    spaceCreateEditProjectsPublications: 16,
    spaceRemoveProjectsPublications: 17,
    spaceCreateRestoreProjectsBackup: 18,
    companyUploadCompanyLogo: 19,
    companyViewCompanyDetails: 20,
    companyEditCompanyDetails: 21,
    companyViewCompanyAdministrationPanel: 22,
    bugtruckReportNewBugsInBugtruck: 23,
    narrationExportAudioVideoNarrations: 24,
    localizationCreateLessonsForLocalization: 25,
    localizationLocalizeLessonsPreparedForLocalization: 26,
    localizationResetLocalizationLessonsToOriginalCurrentLesson: 27,
    localizationExportXLIFF: 28,
    localizationImportXLIFF: 29,
    statesManageAvailableStateSets: 30,
    statesSelectStateSetForPublication: 31,
    courseManageCourses: 32,
    spaceBulkTemplateUpdate: 33,
    spaceBulkAssetsUpdate: 34,
    bugtruckViewBugs: 35,
} as const;

@Injectable()
export class ProjectsService {
    private projects: Space[] | null = null;
    private projectsWithPublications: Space[] | null = null;
    private observe: Observable<Space[]> | null = null;
    private readonly changeSubject = new Subject<Space[]>();

    constructor(private readonly _restClient: RestClientService) {
        this.load();
    }

    private mapProjects(response: ISpaceRaw[]): Space[] {
        return response.map((space) => new Space(space));
    }

    private handleError(error: unknown): Observable<Space[]> {
        console.error("ProjectsService ERROR:", error);
        return of([]);
    }

    public get(): Observable<Space[]> {
        if (this.projects !== null) {
            return of(this.projects);
        } else if (this.observe !== null) {
            return this.observe;
        } else {
            this.load();
            return this.observe || of([]);
        }
    }

    public onChange(): Observable<Space[]> {
        return this.changeSubject.asObservable().pipe(share());
    }

    public getPublications(projectId: string): Observable<Space[]> {
        return this._restClient
            .get<ISpaceRaw[]>(PROJECTS_URL + projectId + "/publications")
            .pipe(
                map((response) =>
                    response.map((publication) => new Space(publication))
                )
            );
    }

    public getStructure(
        spaceId: string,
        recursive: boolean = false
    ): Observable<Subspace> {
        const url =
            PROJECTS_URL +
            spaceId +
            "/structure" +
            (recursive ? "?recursive=true" : "");
        return this._restClient
            .get<ISubspaceResponse>(url)
            .pipe(map((response) => new Subspace(response)));
    }

    private load(): void {
        this.observe = this._restClient.get<ISpaceRaw[]>(PROJECTS_URL).pipe(
            map(this.mapProjects),
            tap((projects) => {
                this.projects = projects;
                this.changeSubject.next(projects);
            }),
            catchError(this.handleError),
            share()
        );

        this.observe.subscribe();
    }

    public projectForPublication(spaceId: string): Observable<Space> {
        return this._restClient
            .get<ISpaceRaw>(PROJECTS_URL + spaceId + "/get_project")
            .pipe(map((response) => new Space(response)));
    }

    public getSpacePermissions(spaceId: string): Observable<RolePermissions> {
        return this._restClient
            .get<PermissionValue[]>(PROJECTS_URL + "permissions/" + spaceId)
            .pipe(map((permissions) => new RolePermissions(permissions)));
    }
}
