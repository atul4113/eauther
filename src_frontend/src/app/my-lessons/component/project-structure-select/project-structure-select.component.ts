import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

import { ITranslations, Subspace } from "../../../common/model";
import { TranslationsService } from "../../../common/service";
import { Lesson } from "../../model/lesson";


@Component({
    selector: 'app-project-structure-select',
    templateUrl: './project-structure-select.component.html'
})
export class ProjectStructureSelectComponent implements OnInit {

    @Input() structure: Subspace;
    @Input() hasLeftPadding: boolean;
    @Input() projectId: any;
    @Input() currentSpaceId: any;
    @Input() lesson: Lesson;
    @Input() shouldShowAddons: boolean;
    @Output() publicationChanged = new EventEmitter<any>();
    @Output() displayLessons = new EventEmitter<any>();

    public translations: ITranslations;

    constructor(private _translations: TranslationsService) {
    }

    ngOnInit() {
        this._translations.getTranslations().subscribe(t => this.translations = t);
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
}
