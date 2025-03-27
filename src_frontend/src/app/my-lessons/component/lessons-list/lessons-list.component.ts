import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

import { ITranslations } from "../../../common/model/translations";
import { Lesson } from "../../model/lesson";
import { TranslationsService } from "../../../common/service";

@Component({
  selector: 'app-lessons-list',
  templateUrl: './lessons-list.component.html'
})
export class LessonsListComponent implements OnInit {

    @Input() lessons!: Lesson[];

    @Output() cancel = new EventEmitter<any>();
    @Output() select = new EventEmitter<any>();

    public translations!: ITranslations;

    constructor(
        private _translations: TranslationsService
    ) {}

    ngOnInit() {
        this._translations.getTranslations().subscribe(t => {
            this.translations = t ?? {} as ITranslations;
        });
    }
    public cancelMerge() {
        this.cancel.emit();
    }

    public selectMerge() {
        this.select.emit();
    }
}
