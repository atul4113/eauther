import { Component, EventEmitter, Input, OnInit, Output } from "@angular/core";

import { ITranslations, Subspace } from "../../../common/model";
import { ProjectsService, TranslationsService } from "../../../common/service";
import { Lesson } from "../../model/lesson";

@Component({
    selector: "app-project-structure",
    templateUrl: "./project-structure.component.html",
})
export class ProjectStructureComponent implements OnInit {
    private _projectId!: number;

    @Input() hasLeftPadding!: boolean;
    @Input()
    set projectId(value: number) {
        this._projectId = value;
        this.reload();
    }
    get projectId() {
        return this._projectId;
    }
    @Input() currentSpaceId!: number;
    @Input() shouldShowAddons!: boolean;
    @Input() lesson!: Lesson;
    @Input() selectable: boolean = false;
    @Output() publicationChanged = new EventEmitter<void>();
    @Output() displayLessons = new EventEmitter<void>();
    @Output() afterSubmodulesDownload = new EventEmitter<Subspace[]>();
    @Output() onSelect = new EventEmitter<number>();

    public structure!: Subspace;
    public translations!: ITranslations;

    constructor(
        private _translations: TranslationsService,
        private _projects: ProjectsService
    ) {}

    ngOnInit() {
        this._translations.getTranslations().subscribe((t) => {
            this.translations = t ?? ({} as ITranslations);
        });
    }

    reload() {
        this._projects
            .getStructure(this.projectId.toString())
            .subscribe((structure) => {
                this.structure = structure;
                this.afterSubmodulesDownload.emit(structure.subspaces);
            });
    }

    public showSubspaces(publication: Subspace): void {
        publication._ui.isExpanded = true;
    }

    public hideSubspaces(publication: Subspace): void {
        publication._ui.isExpanded = false;
    }

    public changePublication(): void {
        this.publicationChanged.emit();
    }

    public showLessons(): void {
        this.displayLessons.emit();
    }

    public select(id: number): void {
        this.onSelect.emit(id);
    }
}
