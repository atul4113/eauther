import { Component, Input } from '@angular/core';

import { Space } from "../../../common/model";
import {ProjectsService, TranslationsService} from "../../../common/service";


@Component({
    selector: 'app-corporate-projects-list',
    templateUrl: './corporate-projects-list.component.html'
})
export class CorporateProjectsListComponent {
    @Input() projects: any;

    public translations: any;

    constructor (
        private _translations: TranslationsService,
        private _projects: ProjectsService
    ) {}

    ngOnInit () {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }

    getPublications(project: Space){
        if(!project.publications) {
            this._projects.getPublications(project.id).subscribe((publications) => {
                this.projects.forEach((p: Space) => {
                    if (p.id === project.id) {
                        p.publications = publications;
                    }
                });
            });
        }
    }

}
