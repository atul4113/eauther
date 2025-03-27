import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';

import {ITranslations, Subspace} from "../../../common/model";
import {ProjectsService, TranslationsService} from "../../../common/service";
import {Lesson} from "../../model/lesson";


@Component({
    selector: 'app-project-structure',
    templateUrl: './project-structure.component.html'
})
export class ProjectStructureComponent implements OnInit {

    private _projectId!: number;

    @Input() hasLeftPadding!: boolean;
    @Input()
    set projectId(value: number){
        this._projectId = value;
        this.reload();
    }
    get projectId(){
        return this._projectId;
    }
    @Input() currentSpaceId: any;
    @Input() shouldShowAddons!: boolean;
    @Input() lesson!: Lesson;
    @Input() selectable: boolean = false;
    @Output() publicationChanged = new EventEmitter<any>();
    @Output() displayLessons = new EventEmitter<any>();
    @Output() afterSubmodulesDownload = new EventEmitter<any>();
    @Output() onSelect = new EventEmitter<any>();

    public structure!: Subspace;
    public translations!: ITranslations;

    constructor(
        private _translations: TranslationsService,
        private _projects: ProjectsService
    ) {
    }

    ngOnInit() {
        this._translations.getTranslations().subscribe(t => {
            this.translations = t ?? {} as ITranslations;
        });
    }

    reload(){
        this._projects.getStructure(this.projectId.toString()).subscribe((structure) => {
            if (structure) {
                this.structure = structure;
                if(this.structure.subspaces) {
                    this.structure.subspaces.sort(function (a: Subspace, b: Subspace) {
                        return (a.name > b.name) ? 1 : ((b.name > a.name) ? -1 : 0);
                    });
                    this.afterSubmodulesDownload.emit(structure.subspaces);
                }else{
                    this.afterSubmodulesDownload.emit([]);
                }
            }
        });
    }

    public showSubspaces(publication: Subspace) {
        publication._ui.isExpanded = true;
    }

    public hideSubspaces(publication: Subspace) {
        publication._ui.isExpanded = false;
    }

    public changePublication() {
        this.publicationChanged.emit();
    }

    public showLessons() {
        this.displayLessons.emit();
    }

    public select(id: number){
        this.onSelect.emit(id);
    }
}
