import { Component, Input, OnInit, Output, EventEmitter } from '@angular/core';

import { ITranslations } from "../../../common/model/translations";
import { LessonToMerge } from "../../model/lesson-to-merge";
import { Lesson } from "../../model/lesson";
import { MyContentService } from "../../service/my-content.service";
import { InfoMessageService, TranslationsService } from "../../../common/service";


@Component({
  selector: 'app-pages-to-merge',
  templateUrl: './pages-to-merge.component.html',
  providers: [MyContentService]
})
export class PagesToMergeComponent implements OnInit {

    @Input() lessonsToMerge: any;
    @Input() spaceId: any;
    @Output() mergeAction = new EventEmitter<Lesson>();
    public translations: any;
    public mergeInProgress: boolean = false;

    constructor(
        private _infoMessage: InfoMessageService,
        private _myContent: MyContentService,
        private _translations: TranslationsService
    ) {}

    ngOnInit() {
        this._translations.getTranslations().subscribe(t => this.translations = t);
    }

    public selectMerge() {
        this.mergeInProgress = true;

        this._myContent.merge(this.spaceId, this.lessonsToMerge).subscribe(
            (success:any) => {
                let lesson = new Lesson(success.content);
                this.mergeAction.emit(lesson);
                this._infoMessage.addSuccess("Success");
                this.mergeInProgress = false;
            },
            (error) => {
                this.mergeAction.emit();
                this._infoMessage.addError("Error");
                this.mergeInProgress = false;
            }
        );
    }

    public cancelMerge() {
        this.mergeAction.emit();
    }
}
