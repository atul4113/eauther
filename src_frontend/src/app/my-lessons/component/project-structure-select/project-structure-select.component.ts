import { Component, EventEmitter, Input, OnInit, Output } from "@angular/core";

import { ITranslations, Subspace } from "../../../common/model";
import { TranslationsService } from "../../../common/service";
import { Lesson } from "../../model/lesson";

@Component({
    selector: "app-project-structure-select",
    templateUrl: "./project-structure-select.component.html",
})
export class ProjectStructureSelectComponent implements OnInit {
    @Input() structure!: Subspace[];
    @Input() hasLeftPadding!: boolean;
    @Input() projectId!: number;
    @Input() currentSpaceId!: number;
    @Input() lesson!: Lesson;
    @Input() shouldShowAddons!: boolean;
    @Output() publicationChanged = new EventEmitter<void>();
    @Output() displayLessons = new EventEmitter<void>();

    public translations!: ITranslations;

    constructor(private _translations: TranslationsService) {}

    ngOnInit() {
        this._translations.getTranslations().subscribe((t) => {
            this.translations = t ?? ({} as ITranslations);
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
}
