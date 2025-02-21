import { Component, OnInit } from '@angular/core';

import { AuthUser, Space } from "./common/model";
import { AuthUserService, PathsService, ProjectsService } from "./common/service";


declare let window: any;
declare let document: any;

const HEADER_ROW_HEIGHT = 64;

@Component({
    templateUrl: './base.component.html'
})
export class BaseComponent implements OnInit {
    public isInitialized: boolean = false;

    public isHeaderCompact: boolean = false;
    public assetsUrl: string = window.mInstructorAssetsUrl;
    public isErrorMessageVisible: boolean = false;

    public user: AuthUser = new AuthUser();
    public projects: Space[] = [];

    constructor(
        private _paths: PathsService,
        private _authUser: AuthUserService,
        private _projects: ProjectsService
    ) {}

    ngOnInit () {
        this._authUser.get().subscribe( (user: AuthUser) => {
            this.user = user;
        });

        this._projects.get().subscribe(projects => {
           this.projects = projects;
           this.projects.sort(function(a: Space,b: Space) {return (a.title > b.title) ? 1 : ((b.title > a.title) ? -1 : 0);} );
        });

        this._paths.onChange().subscribe( () => {
            document.body.scrollTop = 0;
        });
    }

    public mainScrolled (event: Event) {
        this.isHeaderCompact = (<any> event.target).body.scrollTop > HEADER_ROW_HEIGHT;
    }

    public onToggleErrorMessage (isVisible: boolean) {
        this.isErrorMessageVisible = isVisible;
    }

}
