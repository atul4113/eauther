import { UserInterface } from "../../common/model/utility";
import { FileStorage } from "./file-storage";
import { MergeLesson } from "./merge-lesson";
import { Meta } from "@angular/platform-browser";
export interface IMyLessonsRaw {
    cursor: string;
    more_count: number;
    lessons: ILessonRaw[];
}

export interface IMyAddonsRaw {
    cursor: string;
    more_count: number;
    addons: ILessonRaw[];
}

export interface IMyEditedLessonsRaw {
    content: ILessonRaw[];
}

export interface ISimpleLessonRaw {
    id: number;
    is_public: boolean;
    template: string;
    title: string;
    category: string;
}

export interface ILessonRaw {
    id: number;
    title: string;
    author: string;
    state: string;
    modified_date: number;
    version: string;
    icon_href: string;
    is_public: boolean;
    template: string;
    file: number;
    description: string;
    short_description: string;
    tags: string;
    project_name: string;
    project_id: number;
    publication_name: string;
    publication_id: number;
    is_template: boolean;
    enable_page_metadata: boolean;
    score_type: string;
    content_type: number; // 1 - lesson, 2 - template, 3 - addon
    custom_values?: ICustomMetadataRaw[];
    followers: string[];
    is_deleted: boolean;
}

export class LessonContentType {
    public type: number;

    constructor (lesson: ILessonRaw) {
        this.type = lesson.content_type;
    }

    public isLesson (): boolean {
        return this.type === 1 || this.type === 2;
    }

    public isAddon (): boolean {
        return this.type === 3;
    }
}

export class SimpleLesson {
    id: number;
    isPublic: boolean;
    template: string;
    title: string;
    category: string;

    constructor (temaplateLesson: ISimpleLessonRaw) {
        this.id = temaplateLesson.id;
        this.isPublic = temaplateLesson.is_public;
        this.template = temaplateLesson.template;
        this.title = temaplateLesson.title;
        this.category = temaplateLesson.category;
    }
}

export class Lesson {
    public id: number;
    public title: string;
    public author: string;
    public state: string;
    public modifiedDate: Date;
    public version: string;
    public iconHref: string;
    public isPublic: boolean;
    public template: string;
    public fileId: number;
    public description: string;
    public shortDescription: string;
    public tags: string;
    public projectName: string;
    public projectId: number;
    public publicationId: number;
    public publicationName: string;
    public isTemplate: boolean;
    public enablePageMetadata: boolean;
    public scoreType: string;
    public contentType: LessonContentType;
    public customValues: CustomMetadata[];
    public followers: string[] = [];
    public isDeleted: boolean;

    public _ui: UserInterface = new UserInterface();
    public content: {
        pages: MergeLesson[],
        commons: MergeLesson[]
    };

    constructor (lesson: ILessonRaw) {
        this.id = lesson.id;
        this.title = lesson.title;
        this.author = lesson.author;
        this.state = lesson.state;
        if (lesson.modified_date) {
            this.modifiedDate = new Date(lesson.modified_date);
        }
        this.version = lesson.version;
        this.iconHref = lesson.icon_href;
        this.isPublic = lesson.is_public;
        this.template = lesson.template;
        this.fileId = lesson.file;
        this.description = lesson.description;
        this.shortDescription = lesson.short_description;
        this.tags = lesson.tags;
        this.projectName = lesson.project_name;
        this.projectId = lesson.project_id;
        this.publicationName = lesson.publication_name;
        this.publicationId = lesson.publication_id;
        this.isTemplate = lesson.is_template;
        this.enablePageMetadata = lesson.enable_page_metadata;
        this.scoreType = lesson.score_type;
        this.contentType = new LessonContentType(lesson);
        if (lesson.custom_values) {
            this.customValues = lesson.custom_values.map(cv => new CustomMetadata(cv));
        }
        this.followers = lesson.followers;
        this.isDeleted = lesson.is_deleted;
    }

    public copy (): Lesson {
        return new Lesson(this.raw());
    }

    public togglePublic () {
        this.isPublic = !this.isPublic;
    }

    public updateMetadata (data: Metadata) {
        this.title = data.title;
        this.shortDescription = data.shortDescription;
        this.description = data.description;
        this.tags = data.tags;
        this.customValues = data.customValues.map(cv => cv.copy());
    }

    public updateProperties (properties: LessonProperties) {
        this.scoreType = properties.scoreType;
        this.isTemplate = properties.isTemplate;
        this.enablePageMetadata = properties.enablePageMetadata;
    }

    public raw (): ILessonRaw {
        return {
            id: this.id,
            title: this.title,
            author: this.author,
            state: this.state,
            modified_date: this.modifiedDate.getTime(),
            version: this.version,
            icon_href: this.iconHref,
            is_public: this.isPublic,
            template: this.template,
            file: this.fileId,
            description: this.description,
            short_description: this.shortDescription,
            tags: this.tags,
            project_name: this.projectName,
            project_id: this.projectId,
            publication_name: this.publicationName,
            publication_id: this.publicationId,
            is_template: this.isTemplate,
            enable_page_metadata: this.enablePageMetadata,
            score_type: this.scoreType,
            content_type: this.contentType.type,
            followers: this.followers,
            is_deleted: this.isDeleted
        };
    }
}

export interface ILessonPageRaw {
    page_id: string;
    title: string;
    tags: string;
    description: string;
    short_description: string;
    custom_values?: ICustomMetadataRaw[];
}

export class LessonPage {
    public id: string;
    public title: string;
    public tags: string;
    public shortDescription: string;
    public description: string;
    public customValues: CustomMetadata[];

    constructor (page: ILessonPageRaw) {
        this.id = page.page_id;
        this.title = page.title;
        this.tags = page.tags;
        this.shortDescription = page.short_description;
        this.description = page.description;
        if (page.custom_values) {
            this.customValues = page.custom_values.map(cv => new CustomMetadata(cv));
        }
    }

    public copy (): LessonPage {
        return new LessonPage(this.raw());
    }

    public raw (): ILessonPageRaw {
        return {
            page_id: this.id,
            title: this.title,
            tags: this.tags,
            short_description: this.shortDescription,
            description: this.description,
            custom_values: this.customValues ? this.customValues.map(cv => cv.raw()) : null
        };
    }

    public updateMetadata (data: Metadata) {
        this.tags = data.tags;
        this.shortDescription = data.shortDescription;
        this.description = data.description;
        this.customValues = data.customValues.map(cv => cv.copy());
    }
}

export enum LESSONS_ORDERS {
    NAME_UP,
    NAME_DOWN,
    DATE_UP,
    DATE_DOWN,
}

export const LESSONS_ORDER_KEYS = new Map([
    ['nameUp', LESSONS_ORDERS.NAME_UP],
    ['nameDown', LESSONS_ORDERS.NAME_DOWN],
    ['dateUp', LESSONS_ORDERS.DATE_UP],
    ['dateDown', LESSONS_ORDERS.DATE_DOWN],
]);

export class LessonsOrder {
    private order: LESSONS_ORDERS;

    constructor (order: LESSONS_ORDERS = LESSONS_ORDERS.DATE_UP) {
        this.order = order;
    }

    public getOrder (): LESSONS_ORDERS {
        return this.order;
    }

    public isNameUp (): boolean {
        return this.order === LESSONS_ORDERS.NAME_UP;
    }

    public isNameDown (): boolean {
        return this.order === LESSONS_ORDERS.NAME_DOWN;
    }

    public isDateUp (): boolean {
        return this.order === LESSONS_ORDERS.DATE_UP;
    }

    public isDateDown (): boolean {
        return this.order === LESSONS_ORDERS.DATE_DOWN;
    }

}

export class LessonProperties {
    public isTemplate: boolean;
    public enablePageMetadata: boolean;
    public scoreType: string;
    public spaceId: number;

    constructor (isTemplate: boolean, enablePageMetadata: boolean, scoreType: string, spaceId: number) {
        this.isTemplate = isTemplate;
        this.enablePageMetadata = enablePageMetadata;
        this.scoreType = scoreType;
        this.spaceId = spaceId;
    }

    public static fromLesson (lesson: Lesson): LessonProperties {
        const space_id = lesson.publicationId || lesson.projectId;
        return new LessonProperties(lesson.isTemplate || lesson.contentType.type == 2, lesson.enablePageMetadata, lesson.scoreType, space_id);
    }
}

export class Metadata {
    public id: number | string;
    public title: string;
    public tags: string;
    public shortDescription: string;
    public description: string;
    public customValues: CustomMetadata[];

    constructor (title: string, tags: string, shortDescription: string, description: string, customValues: CustomMetadata[], id: number | string = null) {
        this.title = title;
        this.tags = tags;
        this.shortDescription = shortDescription;
        this.description = description;
        this.customValues = customValues;
        this.id = id;
    }

    public static fromLesson (lesson: Lesson): Metadata {
        return new Metadata(
            lesson.title,
            lesson.tags,
            lesson.shortDescription,
            lesson.description,
            lesson.customValues,
            lesson.id
        );
    }

    public static fromLessonPage (page: LessonPage): Metadata {
        return new Metadata(
            page.title,
            page.tags,
            page.shortDescription,
            page.description,
            page.customValues,
            page.id
        );
    }

    public copy (): Metadata {
        return new Metadata(
            this.title,
            this.tags,
            this.shortDescription,
            this.description,
            this.customValues ? this.customValues.map(cv => cv.copy()) : null,
            this.id
        );
    }
}

export const CUSTOM_METADATA_TYPES = {
    SHORT_TEXT: 0,
    LONG_TEXT: 1,
    SELECT: 2,
};

export class CustomMetadataType {
    public type: number;

    constructor (definition: ICustomMetadataRaw) {
        this.type = definition.field_type || CUSTOM_METADATA_TYPES.SHORT_TEXT;
    }

    public isShortText (): boolean {
        return this.type === CUSTOM_METADATA_TYPES.SHORT_TEXT;
    }

    public isLongText (): boolean {
        return this.type === CUSTOM_METADATA_TYPES.LONG_TEXT;
    }

    public isSelect (): boolean {
        return this.type === CUSTOM_METADATA_TYPES.SELECT;
    }
}

export interface ICustomMetadataRaw {
    id: number;
    name: string;
    description: string;
    value: string;
    entered_value: string;
    field_type: number;
    order: number;
    is_enabled: boolean;
}

export class CustomMetadata {
    public id: number;
    public name: string;
    public description: string;
    public definedValue: string;
    public value: string;
    public fieldType: CustomMetadataType;
    public order: number;
    public isEnabled: boolean;

    constructor (data: ICustomMetadataRaw) {
        this.id = data.id;
        this.name = data.name;
        this.description = data.description;
        this.definedValue = data.value;
        this.value = data.entered_value;
        this.fieldType = new CustomMetadataType(data);
        this.order = data.order;
        this.isEnabled = data.is_enabled;
    }

    public copy (): CustomMetadata {
        return new CustomMetadata(this.raw());
    }

    public raw (withoutId: boolean = false): ICustomMetadataRaw {
        return {
            id: withoutId ? undefined : this.id,
            name: this.name,
            description: this.description,
            value: this.definedValue,
            entered_value: this.value,
            field_type: this.fieldType.type,
            order: this.order,
            is_enabled: this.isEnabled,
        };
    }
}
