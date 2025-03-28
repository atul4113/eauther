import { Component, OnInit } from '@angular/core';
import { CreateLessonService } from "../../service/create-lesson.service";
import { ILessonRaw, Lesson, SimpleLesson } from "../../model/lesson";
import { ActivatedRoute, Router } from "@angular/router";
import { PathsService } from "../../../common/service/paths.service";
import { InfoMessageService } from "../../../common/service/info-message.service";
import { TranslationsService } from "../../../common/service/translations.service";
import { ITranslations } from "../../../common/model/translations";

interface CreateLessonParams {
    title: string;
    tags: string;
    short_description: string;
    description: string;
    passing_score: number;
    score_type: "last" | "best";
    template_id: number;
}

@Component({
    selector: 'app-create-lesson',
    templateUrl: './create-lesson.component.html',
    providers: [CreateLessonService]
})
export class CreateLessonComponent implements OnInit {
    public templates: SimpleLesson[] = [];
    public publicTemplates: SimpleLesson[] = [];
    public privateTemplates: SimpleLesson[] = [];
    public scoreType: "last" | "best" = "last";
    public selectedTemplate: SimpleLesson | null = null;
    public spaceId: number = 0;
    public backUrl: string = "";
    public title: string = "";
    public tags: string = "";
    public shortDescription: string = "";
    public description: string = "";
    public passingScore: number = 0;
    public isError: boolean = false;
    public translations: ITranslations | null = null;
    public isButtonActive: boolean = true;
    public templatesLoaded: boolean = false;

    constructor(
        private _createLessonService: CreateLessonService,
        private _route: ActivatedRoute,
        private _router: Router,
        private _paths: PathsService,
        private _info: InfoMessageService,
        private _translations: TranslationsService
    ) {}

    ngOnInit(): void {
        this._translations.getTranslations().subscribe((translations: ITranslations | null) => {
            if (translations) {
                this.translations = translations;
            }
        });

        this._createLessonService.getSimpleTemplates().subscribe((templates: SimpleLesson[]) => {
            this.templates = templates;
            this.publicTemplates = this.templates.filter(template => template.category !== "Private");
            this.privateTemplates = this.templates.filter(template => template.category === "Private");
            this.templatesLoaded = true;
        });

        let prevUrl = this._route.snapshot.params['next'];
        this.spaceId = this._route.snapshot.params['id'];
        if (prevUrl) {
            this.backUrl = this._paths.decodeNextUrl(prevUrl) || '';
        }
    }

    public createLesson(): void {
        if (!this.selectedTemplate) {
            this.isError = true;
            return;
        }

        const lesson: CreateLessonParams = {
            title: this.title,
            tags: this.tags,
            short_description: this.shortDescription,
            description: this.description,
            passing_score: this.passingScore,
            score_type: this.scoreType,
            template_id: this.selectedTemplate.id
        };

        this.isButtonActive = false;
        this._createLessonService.createLesson(lesson).subscribe(
            (response: unknown) => {
                const newLesson = response as Lesson;
                const successMessage = this.translations?.labels['lesson.create.success'] ?? 'Lesson created successfully';
                this._info.addSuccess(successMessage);
                this._router.navigate(['/mycontent', newLesson.id, 'editor'], {
                    queryParams: {
                        new1: true,
                        next: this.backUrl
                    }
                });
            },
            (error: unknown) => {
                this.isError = true;
                this.isButtonActive = true;
                const errorMessage = this.translations?.labels['lesson.create.error'] ?? 'Failed to create lesson';
                this._info.addError(errorMessage);
            }
        );
    }

    public selectTemplate(template: SimpleLesson): void {
        this.selectedTemplate = template;
        this.isError = false;
    }
}
