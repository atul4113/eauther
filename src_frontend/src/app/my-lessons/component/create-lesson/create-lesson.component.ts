import { Component, OnInit } from '@angular/core';
import { CreateLessonService } from "../../service/create-lesson.service";
import {ILessonRaw, Lesson, SimpleLesson} from "../../model/lesson";
import { ActivatedRoute} from "@angular/router";
import { PathsService } from "../../../common/service/paths.service";
import { InfoMessageService } from "../../../common/service/info-message.service";
import { TranslationsService } from "../../../common/service/translations.service";
import { ITranslations } from "../../../common/model/translations";

@Component({
    selector: 'app-create-lesson',
    templateUrl: './create-lesson.component.html',
    providers: [CreateLessonService]
})
export class CreateLessonComponent implements OnInit {

    public templates: SimpleLesson[];
    public publicTemplates: SimpleLesson[];
    public privateTemplates: SimpleLesson[];
    public scoreType = "last";
    public selectedTemplate: SimpleLesson;
    public spaceId: number;
    public backUrl: string;
    public title: string = "";
    public tags: string = "";
    public shortDescription: string = "";
    public description: string = "";
    public passingScore: number = 0;
    public isError = false;
    public translations: ITranslations;
    public isButtonActive = true;
    public templatesLoaded = false;


    constructor(private _createLessonService: CreateLessonService,
                private _route: ActivatedRoute,
                private _paths: PathsService,
                private _info: InfoMessageService,
                private _translations: TranslationsService) {
    }

    ngOnInit() {
        this._translations.getTranslations().subscribe(t => this.translations = t);

        this._createLessonService.getSimpleTemplates().subscribe(templates => {
            this.templates = templates;
            this.publicTemplates = this.templates.filter(template => template.category != "Private");
            this.privateTemplates = this.templates.filter(template => template.category == "Private");
            this.templatesLoaded = true;
        });

        let prevUrl = this._route.snapshot.params['next'];
        this.spaceId = this._route.snapshot.params['id'];

        if (prevUrl) {
            this.backUrl = this._paths.decodeNextUrl(prevUrl);
        }
    }

    public createLesson() {
        if (!this.title) {
            this.isError = true;
            return;
        } else {
            this.isError = false;
        }

        this.isButtonActive = false;
        let templateId = this.selectedTemplate ? this.selectedTemplate.id : "";

        let createObj = {
            templateId: templateId,
            score_type: this.scoreType,
            title: this.title,
            tags: this.tags,
            short_description: this.shortDescription,
            description: this.description,
            passingScore: this.passingScore,
            space_id: this.spaceId
        };

        this._createLessonService.createLesson(createObj).subscribe(
            (data) => {
                window.location.href = '/mycontent/' + data['content_id'] + '/editor?new1&next=/' + this.backUrl + '&' + data['token_key'] + '=' + data['token'];
            },
            () => {
                this._info.addError("Lesson has NOT been created");
                this.isButtonActive = true;
            }
        )
    }

}
