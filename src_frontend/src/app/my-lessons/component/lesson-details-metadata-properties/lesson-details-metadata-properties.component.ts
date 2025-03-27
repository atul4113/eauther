import { Component, EventEmitter, Input, OnChanges, OnInit, Output } from '@angular/core';
import { map, tap } from "rxjs/operators";

import { ITranslations } from "../../../common/model/translations";
import { Lesson, LessonProperties } from "../../model/lesson";
import { MyContentService } from "../../service/my-content.service";
import { ProjectsService } from "../../../common/service/projects.service";
import { Space } from "../../../common/model/space";
import { Subspace } from "../../../common/model/subspace";
import { CategoriesService } from "../../../common/service/categories.service";
import { Category } from "../../../common/model/category";


@Component({
    selector: 'app-lesson-details-metadata-properties',
    templateUrl: './lesson-details-metadata-properties.component.html'
})
export class LessonDetailsMetadataPropertiesComponent implements OnChanges, OnInit {

    @Input() lesson!: Lesson;
    @Input() translations!: ITranslations;
    @Input() isProject!: boolean;

    public isEditMode: boolean = false;

    public properties!: LessonProperties;
    public projects!: Space[];
    public selectedProject!: Space;
    public projectStructure!: Subspace;
    public publicationId!: number;
    public categories!: Category[];
    public selectedCategory!: Category;
    private selectedProjectId!: number;

    constructor (
        private _myContent: MyContentService,
        private _projects: ProjectsService,
        private _categories: CategoriesService
    ) {}

    ngOnInit() {
        this._projects.get().subscribe(projects =>  {
            this.projects = projects;
            this.selectedProject = this.projects.filter(cat => cat.id == this.lesson.projectId)[0];
        });
    }

    ngOnChanges () {
        if (this.lesson) {
            this.reset();
        }
    }

    public edit () {
        this.isEditMode = true;

        if(this.isProject) {
            this.selectedProjectId = this.selectedProject.id;
            this.getProjectStructure();
        } else {
            this._categories.get().subscribe(categories => {
                this.categories = categories;
                this.selectedCategory = this.categories.filter(cat => cat.id == this.lesson.projectId)[0];
            });
        }
    }

    public save () {
        this.properties.isTemplate ? this.lesson.contentType.type = 2 : this.lesson.contentType.type = 1;

        return this._myContent.updateLessonProperties(this.lesson, this.properties).pipe(
            tap( () => { this.isEditMode = false; }),
            map( () => { return this.properties; })
        );
    }

    public reset () {
        this.properties = LessonProperties.fromLesson(this.lesson);
        this.isEditMode = false;
    }

    public getProjectStructure() {
        this._projects.getStructure(this.selectedProjectId.toString(), false).subscribe(structure => {
            this.projectStructure = structure;
            if (this.projectStructure.subspaces) {
                this.projectStructure.subspaces.sort(function (a: Subspace, b: Subspace) {
                    return (a.name > b.name) ? 1 : ((b.name > a.name) ? -1 : 0);
                });
            }
        });
    }

    public changeProject(project:any) {
        this.selectedProjectId = project.value.id;
        this.getProjectStructure();
    }

    public publicatonChange(space:any) {
        if(this.isProject) {
            this.publicationId = space.value;
            this.properties.spaceId = space.value;
        } else {
            this.publicationId = space.value.id;
            this.properties.spaceId = space.value.id;
        }
    }

}
