import {Component, ElementRef, HostListener, OnInit, QueryList, ViewChild, ViewChildren} from '@angular/core';
import {ActivatedRoute, Router} from "@angular/router";

import {ITranslations, Category, Space, Subspace, CheckboxOption, AuthUser} from "../../../common/model";
import {Lesson, LESSONS_ORDER_KEYS, LessonsOrder} from "../../model/lesson";
import {MergeLesson} from "../../model/merge-lesson";
import {LessonToMerge} from "../../model/lesson-to-merge";
import {EditToken} from "../../model/edit-token";
import {MyContentService} from "../../service/my-content.service";
import {
    InfoMessageService, TranslationsService, AuthUserService, CookieService, CategoriesService, ProjectsService
} from "../../../common/service";
import {LessonDetailsComponent} from "../lesson-details/lesson-details.component";
import {RolePermissions} from "../../../common/model/auth-user";
import {LessonCardComponent} from "../lesson-card/lesson-card.component";
import {Observer} from "rxjs/Observer";
import {NOT_FOUND_CHECK_ONLY_ELEMENT_INJECTOR} from "@angular/core/src/view/provider";
import {MatMenu} from "@angular/material";


declare let document: any;
declare let window: any;

@Component({
    templateUrl: './my-lessons.component.html',
    providers: [MyContentService, CategoriesService]
})
export class MyLessonsComponent implements OnInit {
    @ViewChild(LessonDetailsComponent) lessonDetailsComponent!: LessonDetailsComponent;
    @ViewChildren(LessonCardComponent) lessonCardComponent!: QueryList<LessonCardComponent>;
    @ViewChild('contentmain') contentmain!: ElementRef;


    public projects: any;
    public lessons!: Lesson[];
    public categories!: Category[];
    public user!: AuthUser;
    public selectedLessons: Lesson[] = [];
    public originalSpaceId!: number;
    public lessonsPageSize = 16;
    public lessonsPagesCount: number = 1;
    public trashPagesCount: number = 1;
    public lessonsPageIndex: number = 1;
    public trashPageIndex: number = 1;
    public lessonsOrder: LessonsOrder = new LessonsOrder();
    public userPermissions!: RolePermissions;

    public isListLessonsShow = true;
    public selectedLessonId!: number;

    public isCtrlPressed = false;


    public checkOptions = [
        {value: false, content: 'use_grid', displayName: 'Use grid'},
        {value: false, content: 'grid_size', displayName: 'Grid size'},
        {value: false, content: 'static_header', displayName: 'Static header'},
        {value: false, content: 'static_footer', displayName: 'Static footer'}
    ];

    public templatePopupTitle = 'Preferences that will be propagated with template:';
    public copyToAnotherUserPopupTitle = 'Copy content to account';
    public isUpdateTemplatePopupVisible = false;

    public lessonsToMerge = [];
    public pagesToMerge = [];

    public projectName: string = "";
    public isProject: boolean = false;
    public isView: boolean = false;
    public projectStructure: Subspace = null;
    public publicationName: string = "";
    public currentProject!: Space;
    public detailsVisible = false;

    public editLessonToken!: EditToken;
    public editAddonToken!: EditToken;
    public isDeleteLessonPopupVisible: boolean = false;
    public isCopyToAnotherUserPopupVisible: boolean = false;
    public lessonsToDelete!: Lesson[];
    public translations!: ITranslations;
    public lessonsToShow: Lesson[] = [];
    public addonsToShow!: Lesson[];
    public trashToShow!: Lesson[];
    public allLessons: Lesson[] = [];
    public shouldShowAddons = false;
    public shouldShowTrash = false;
    public mainCategory!: Category = null;

    public assetsUrl = window['mAuthorAssetsUrl'];

    public selectedLesson!: Lesson;

    constructor(private _infoMessage: InfoMessageService,
                private _user: AuthUserService,
                private _myContent: MyContentService,
                private _categories: CategoriesService,
                private _route: ActivatedRoute,
                private _projects: ProjectsService,
                private _cookie: CookieService,
                private _translations: TranslationsService,
                private _router: Router,
    ) {
    }

    public get spaceId(): number {
        return this.originalSpaceId || (this.user ? this.user.privateSpace.id : null);
    }

    public get privateSpaceId(): number {
        return this.user.privateSpace.id;
    }


    public getMainContent() {
        return this.contentmain.nativeElement;
    }

    ngOnInit() {
        this._translations.getTranslations().subscribe(t => {
            this.translations = t ?? {} as ITranslations;
        });

        this._route.data.subscribe(data => {
            this.isProject = data.isProject || false;
            this.shouldShowTrash = data.isTrash || false;
            this.isView = data.isView || false;
            this.shouldShowAddons = data.isAddons || false;
        });

        this._route.params.subscribe(params => {
            if (this.isView && !this.shouldShowAddons) {
                this.selectedLessonId = params['id'];
                this._myContent.getLessonDetails(this.selectedLessonId).subscribe(lesson => {
                    this.selectedLesson = lesson;
                    this.init(params);
                    this.onLessonPreview(lesson);
                });
            } else {
                this.init(params);
            }
        });

        this._user.get().subscribe(user => {
            this.user = user;
        });

        this._categories.get().subscribe(categories => {
            this.categories = categories;
            this.mainCategory = this.categories.filter(cat => cat.isTopLevel)[0];

            if (!this.isProject) {
                this.getAddons(this.mainCategory.id);
            }
            if (!this.isProject && this.shouldShowTrash) {
                this.getTrash(1, this.mainCategory.id);
            }
        });

        this._projects.get().subscribe(projects => {
            this.projects = projects;
            this.projects.forEach((project) => {
                project.publications = undefined;
            });
            this.projects.sort(function (a: Space, b: Space) {
                return (a.title > b.title) ? 1 : ((b.title > a.title) ? -1 : 0);
            });
        });

        this.getEditorToken();
    }

    @HostListener('document:keydown', ['$event'])
    handleKeyboarddownEvent(event: KeyboardEvent) {
        if (event.key == "Control" || event.metaKey) {
            this.isCtrlPressed = true;
        }
    }

    @HostListener('document:keyup', ['$event'])
    handleKeyboardupEvent(event: KeyboardEvent) {
        if (event.key == "Control" || !event.metaKey) {
            this.isCtrlPressed = false;
        }
    }

    get shouldShowDetails() {
        return this.selectedLessons.length === 1;
    }

    get lessonToShow() {
        return this.selectedLessons[0];
    }

    get areLessonsSelected() {
        return this.selectedLessons.length > 0;
    }

    get areAddonsSelected() {
        if (this.selectedLessons.length > 0) {
            let result = false;
            this.selectedLessons.forEach(lesson => {
                if (lesson.contentType.isAddon()) {
                    result = true;
                }
            });
            return result;
        } else {
            return false;
        }
    }

    get shouldDisplayList() {
        return this.selectedLessons.length > 1;
    }

    get showMergeOptions() {
        return this.lessonsToMerge.length > 0;
    }

    get currentProjectPublications(): Array<Space> {
        let publications: Array<Space> = [];
        if (this.currentProject && this.projects) {
            this.projects.forEach(project => {
                if (this.currentProject.id === project.id) {
                    this.downloadPublications(project);
                    publications = project.publications;
                }
            });
        }
        return publications;
    }

    private init(params) {
        if (!this.isView) {
            this.originalSpaceId = params['id'] || null;
        } else {
            this.originalSpaceId = this.selectedLesson.publicationId;
        }

        this.hideDetails();

        if (this.isProject) {
            this._projects.getSpacePermissions(this.originalSpaceId).subscribe(permissions => {
                this.userPermissions = permissions;
                if (this.userPermissions.contentViewLessonsAddons) {
                    this.detectSort();
                }
            });

            this._projects.projectForPublication(this.originalSpaceId.toString()).subscribe(project => {
                const fetch = !this.currentProject || this.currentProject.id !== project.id;
                this.currentProject = project;
                this.projectName = project.title;
                if (fetch) {
                    this.projectStructure = null;
                    this._projects.getStructure(this.currentProject.id.toString(), false).subscribe(structure => {
                        this.projectStructure = structure;
                        this.projectStructure.subspaces.sort(function (a: Subspace, b: Subspace) {
                            return (a.name > b.name) ? 1 : ((b.name > a.name) ? -1 : 0);
                        });
                    });
                }

                this._projects.getStructure(this.originalSpaceId.toString(), false).subscribe(structure => {
                    this.publicationName = structure.name;
                });

                this.getAddons(this.currentProject.id);

                if (this.shouldShowTrash) {
                    this.getTrash(1, this.currentProject.id);
                }
            });
        } else {
            this.detectSort();
            this.userPermissions = new RolePermissions([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]);
        }
    }

    public getAddons(spaceId) {
        this.addonsToShow = undefined;
        this._myContent.getAllAddons(spaceId).subscribe(lessons => {

            this.addonsToShow = lessons;
        });
    }

    public loadTrashPage(pageIndex: number) {
        if (this.trashPageIndex !== pageIndex) {
            this.trashPageIndex = pageIndex;
            this.getTrash(pageIndex, this.originalSpaceId);
        }
    }

    public getTrash(pageIndex, spaceId) {
        this.trashToShow = undefined;
        this.trashPageIndex = pageIndex;
        this._myContent.getTrashPage(pageIndex, spaceId).subscribe(trashPage => {
                this.trashPagesCount = pageIndex;
                if (trashPage.moreCount > 0) {
                    this.trashPagesCount += Math.ceil(trashPage.moreCount / this.lessonsPageSize);
                }

                this.trashToShow = trashPage.lessons;
            },
            (error) => {
                console.error(error);
        });
    }

    public getEditorToken() {
        this._myContent.getEditLessonToken().subscribe(editToken => {
            this.editLessonToken = editToken;
        });
        this._myContent.getEditAddonToken().subscribe(editToken => {
            this.editAddonToken = editToken;
        });
    }

    public loadLessonsPage(pageIndex: number) {
        if (this.lessonsPageIndex !== pageIndex) {
            this.lessonsPageIndex = pageIndex;
            this._loadLessonsPage(pageIndex, this.originalSpaceId, this.lessonsOrder);
        }
    }

    private _loadLessonsPage(pageIndex: number, spaceId: number = null, order: LessonsOrder = new LessonsOrder()) {
        if (!this.isView) {
            this.lessons = undefined;
            this.lessonsPageIndex = pageIndex;
            this._myContent.getLessonsPage(pageIndex, spaceId, order).subscribe(lessonsPage => {
                    this.lessonsPagesCount = pageIndex;
                    if (lessonsPage.moreCount > 0) {
                        this.lessonsPagesCount += Math.ceil(lessonsPage.moreCount / this.lessonsPageSize);
                    }

                    this.lessons = lessonsPage.lessons;
                    this.lessonsToShow = this.lessons.filter(lesson => lesson.contentType.isLesson());
                    this.lessons = this.lessonsToShow;
                    this._markSelectedLessons(this.lessons, this.selectedLessons);
                },
                (error) => {
                    console.error(error);
                });
        }
    }

    public switchToAddons() {
        this.shouldShowAddons = true;
        this.shouldShowTrash = false;
        this.isView = false;
        this.isListLessonsShow = true;
        this.selectedLessons = [];
    }

    public switchToLessons() {
        if (this.addonsToShow != undefined) {
            this.addonsToShow.forEach(addon => {
                addon._ui.isSelected = false
            });
        }
        this.shouldShowAddons = false;
        this.shouldShowTrash = false;
        this.isView = false;
        this.isListLessonsShow = true;
    }

    public switchToTrash() {
        this.shouldShowTrash = true;
        this.shouldShowAddons = false;
        this.isView = false;
        this.isListLessonsShow = true;
    }

    public reloadLessons() {
        this._loadLessonsPage(this.lessonsPageIndex, this.spaceId, this.lessonsOrder);
    }

    public detectSort() {
        const cookieOrder = this._cookie.get('lessonsOrderBy' + this.originalSpaceId);
        if (cookieOrder !== undefined) {
            this.sortLessonsBy(cookieOrder);
        } else {
            this.sortLessonsBy('dateDown');
        }
    }

    public sortLessonsBy(sortBy: string) {
        if (LESSONS_ORDER_KEYS.has(sortBy)) {
            const order = LESSONS_ORDER_KEYS.get(sortBy);
            this.lessonsOrder = new LessonsOrder(order);
            this.setCookieSortBy(sortBy);

            this._loadLessonsPage(1, this.originalSpaceId, this.lessonsOrder);
        }
    }

    public onLessonSelect(lesson: Lesson) {
        if (!this.isCtrlPressed) {
            this.deselectAllLessons(lesson);
        }
        lesson._ui.toggleSelect();

        if (lesson._ui.isSelected) {
            this.selectedLessons.push(lesson);
        } else {
            this.selectedLessons = this.selectedLessons.filter(l => l.id !== lesson.id);
        }

        if (this.areLessonsSelected) {
            this.showDetails();
        } else {
            this.hideDetails();
        }
    }

    public deselectAllLessons(selectedLesson: Lesson) {
        if (this.lessons != undefined) {
            this.lessons.forEach(lesson => {
                if (lesson.id !== selectedLesson.id) {
                    lesson._ui.isSelected = false
                }
            });
        }

        if (this.addonsToShow != undefined) {
            this.addonsToShow.forEach(lesson => {
                if (lesson.id !== selectedLesson.id) {
                    lesson._ui.isSelected = false
                }
            });
        }

        if (this.trashToShow != undefined) {
            this.trashToShow.forEach(lesson => {
                if (lesson.id !== selectedLesson.id) {
                    lesson._ui.isSelected = false
                }
            });
        }

        this.selectedLessons = [];
    }


    private _redirectEdit(lesson: Lesson, editLessonToken: EditToken) {
        let redirectUrl;
        if (lesson.contentType.isLesson()) {
            if (this.isProject) {
                redirectUrl = '/mycontent/' + lesson.id + '/editor?next=/corporate/list/' + this.spaceId + '&' + editLessonToken.tokenKey + '=' + editLessonToken.token;
            } else {
                redirectUrl = '/mycontent/' + lesson.id + '/editor?next=/mycontent&' + editLessonToken.tokenKey + '=' + editLessonToken.token;
            }
        } else {
            if (this.isProject) {
                redirectUrl = '/mycontent/' + lesson.id + '/editaddon?next=/corporate/list/' + this.spaceId + '&' + editLessonToken.tokenKey + '=' + editLessonToken.token;
            } else {
                redirectUrl = '/mycontent/' + lesson.id + '/editaddon?next=/mycontent&' + editLessonToken.tokenKey + '=' + editLessonToken.token;
            }
        }
        if (redirectUrl.length > 0) {
            window.location.href = redirectUrl;
        }
    }

    onContactSupport() {
        let redirectUrl = "/support/addticket?lesson_url=" + window.location.origin + "/embed/" + this.selectedLesson.id;
        window.location.href = redirectUrl;
    }

    public onSelectedLessonEdit() {
        if (this.selectedLesson.contentType.isLesson()) {
            this._myContent.getEditLessonToken().subscribe(editToken => {
                this.editLessonToken = editToken;
                this._redirectEdit(this.selectedLesson, editToken);
            });
        } else if (this.selectedLesson.contentType.isAddon()) {
            this._myContent.getEditAddonToken().subscribe(editToken => {
                this.editAddonToken = editToken;
                this._redirectEdit(this.selectedLesson, editToken);
            });
        }
    }

    public onLessonEdit(lessonId) {
        let cardComponent = this.lessonCardComponent.filter(lessonCard => lessonCard.lesson.id == lessonId);
        if (cardComponent[0].lesson.contentType.isLesson()) {
            this._myContent.getEditLessonToken().subscribe(editToken => {
                this.editLessonToken = editToken;
                cardComponent[0].openEditor(editToken);
            });
        } else if (cardComponent[0].lesson.contentType.isAddon()) {
            this._myContent.getEditAddonToken().subscribe(editToken => {
                this.editAddonToken = editToken;
                cardComponent[0].openEditor(editToken);
            });
        }
    }

    public onLessonPreview(lesson) {
        let redirectUrl;
        if (this.isProject) {
            redirectUrl = '/corporate/view/' + lesson.id;
        } else {
            redirectUrl = '/mycontent/view/' + lesson.id;
        }
        this._router.navigate([redirectUrl]);
        this.selectedLessons = [];
        if (lesson.contentType.isLesson()) {
            if (lesson.isDeleted) {
                this.shouldShowTrash = true;
            }
            this.selectedLessonId = lesson.id;
            this.isListLessonsShow = false;
            this.selectedLessons.push(lesson);
            this.showDetails();
        }
    }

    public closeLessonPreview() {
        this.isListLessonsShow = true;
        if (this.isView) {
            this._backToList();
        }
    }

    private _backToList() {
        let redirectUrl;
        if (this.isProject) {
            redirectUrl = '/corporate/list/' + this.selectedLesson.publicationId;
        } else {
            redirectUrl = '/mycontent/' + this.selectedLesson.publicationId;
        }
        this._router.navigate([redirectUrl]);
    }

    public isLessonSelected(lesson: Lesson): boolean {
        return lesson._ui.isSelected;
    }

    public copyLesson(spaceId: any) {
        this.selectedLessons.forEach(lesson => {
            let type: string = lesson.contentType.isAddon() ? "Addon" : "Lesson";
            this._myContent.copyLesson(lesson.id, spaceId).subscribe(
                (success) => {
                    this._infoMessage.addSuccess(type + " has been copied");
                    if (spaceId == this.spaceId) {
                        if (lesson.contentType.isLesson()) {
                            this._loadLessonsPage(this.lessonsPageIndex, this.spaceId, this.lessonsOrder);
                        } else if (lesson.contentType.isAddon()) {

                            this.getAddons(this.currentProject ? this.currentProject.id : this.categories[0].id);
                        }
                    }
                },
                (error) => {
                    this._infoMessage.addError(type + " has NOT been copied");
                }
            )
        });
    }

    public copyLessonToAnotherAccount() {
        this.isCopyToAnotherUserPopupVisible = true;
    }

    public copyToAnotherUserAccept(username: string) {
        this.selectedLessons.forEach(lesson => {
            this._myContent.copyToAccount(lesson.id, {user: username}).subscribe(
                (success) => {
                    this._infoMessage.addSuccess("Lesson copied to account " + username);
                },
                (error) => {
                    this._infoMessage.addError(this.translations.labels[error.body] ? this.translations.labels[error.body] : error.body);
                }
            )
        });
        this.isCopyToAnotherUserPopupVisible = false;
    }

    public exportLesson(version: any) {
        this.selectedLessons.forEach(lesson => {
            this._myContent.exportLesson(lesson.id, version).subscribe(
                (success) => {
                    this._infoMessage.addSuccess("Presentation export will now run in background. Once it is completed you will be notified by email");
                },
                (error) => {
                    this._infoMessage.addError("Lesson has NOT been exported");
                }
            )
        });
    }

    public sortLessonsByNameDown() {
        this.sortLessonsBy('nameDown');
    }

    public sortLessonsByNameUp() {
        this.sortLessonsBy('nameUp');
    }

    public sortLessonByDateDown() {
        this.sortLessonsBy('dateDown');
    }

    public sortLessonByDateUp() {
        this.sortLessonsBy('dateUp');
    }

    public setCookieSortBy(value: string) {
        let dateYearPlus = new Date();
        dateYearPlus.setTime(dateYearPlus.getTime() + (365 * 24 * 3600 * 1000));
        this._cookie.put('lessonsOrderBy' + this.originalSpaceId, value, {expires: dateYearPlus});
    }

    public onLessonPublish(lesson: Lesson) {
        this.lessons.forEach(les => {
            if (les.id === lesson.id) {
                les.togglePublic();

                if (lesson.isPublic) {
                    this._infoMessage.addSuccess("Lesson is now publicly available under the following url: https://www.mauthor.com/present/" + lesson.id);
                } else {
                    this._infoMessage.addSuccess("Lesson is NOT public");
                }
            }
        });

        this.lessonDetailsComponent.changePublishInfo();
    }

    public updateAssets() {
        this.selectedLessons.forEach(lesson => {
            this._myContent.updateAssets(lesson.id).subscribe(
                (success) => {
                    this._infoMessage.addSuccess("Assets for lesson will be updated in background. You will be notified via email when it is finished.");
                },
                (error) => {
                    this._infoMessage.addError("Assets has NOT been updated");
                }
            )
        });
    }

    public updateTemplateAccept(checkOptions: CheckboxOption) {
        this.selectedLessons.forEach(lesson => {
            this._myContent.updateTemplate(lesson.id, checkOptions).subscribe(
                (success) => {
                    this._infoMessage.addSuccess("Template for lesson has been updated");
                },
                (error) => {
                    this._infoMessage.addError(error.body);
                }
            )
        });
        this.isUpdateTemplatePopupVisible = false;
    }

    public updateTemplate() {
        this.checkOptions.map(option => option.value = false);
        this.isUpdateTemplatePopupVisible = true;
    }

    public listPage() {
        this.clearMergedPages();
        this.lessonsToMerge = [];
        this.selectedLessons.forEach(lesson => {
            if (lesson.content) {
                this.lessonsToMerge.push(lesson);
            } else {
                this._myContent.lessonList(lesson.id, this.spaceId).subscribe(
                    (pages) => {
                        lesson.content = pages;
                        this.lessonsToMerge = this.lessonsToMerge.concat([lesson]);
                    }
                );
            }
        });
    }

    public onMergeCancel() {
        this.lessonsToMerge = [];
        this.clearMergedPages();
    }

    public onMergeSelect() {
        this.lessonsToMerge.forEach((lesson: Lesson, index) => {
            let lessonObj = new LessonToMerge({
                'common_pages': [],
                'content_id': lesson.id,
                'title': lesson.title,
                'pages': []
            });

            lesson.content.pages.forEach((page: MergeLesson) => {
                if (page._ui.isSelected) {
                    lessonObj.pages.push(page.index);
                }
            });

            lesson.content.commons.forEach((page: MergeLesson) => {
                if (page._ui.isSelected) {
                    lessonObj.common_pages.push(page.index)
                }
            });

            this.pagesToMerge.push(lessonObj);

            if (index + 1 === this.lessonsToMerge.length) {
                this.onMergeCancel();
            }
        })
    }

    public clearMergedPages() {
        if (this.lessons != undefined) {
            this.lessons.forEach((lesson: Lesson) => {
                if (lesson.content) {
                    lesson.content.pages.forEach((page: MergeLesson) => {
                        page._ui.isSelected = false;
                    });

                    lesson.content.commons.forEach((page: MergeLesson) => {
                        page._ui.isSelected = false;
                    });
                }
            });
        }
    }

    public onMergeAction(lesson: Lesson) {
        this.pagesToMerge = [];
        if (lesson) {
            this.lessons.push(lesson);
            this.detectSort();
        }
    }

    public showDetails() {
        this.detailsVisible = true;
    }

    public hideDetails() {
        this.detailsVisible = false;
        if (this.lessons != undefined) {
            this.lessons.forEach(lesson => {
                lesson._ui.isSelected = false
            });
        }

        this.selectedLessons = [];
    }

    public deleteLessons() {
        this.lessonsToDelete = this.selectedLessons;
        this.isDeleteLessonPopupVisible = true;
    }

    public onDeleteLessonAccept() {
        this._deleteLessons();
        this.isDeleteLessonPopupVisible = false;
        this.lessonsToDelete = null;
    }

    public onDeleteLessonReject() {
        this.isDeleteLessonPopupVisible = false;
        this.lessonsToDelete = null;
    }

    public scrollToTop() {
        window.scrollTo(0, 0);
    }

    private succesDeleteCallback(lesson: Lesson) {
        if (this.isView) {
            this._backToList();
        }
        if (lesson.contentType.isAddon()) {
            this._infoMessage.addSuccess("Addon " + lesson.title + " has been deleted");
            this.addonsToShow = this.addonsToShow.filter(addon => addon.id != lesson.id);
            if (this.shouldShowAddons) {
                this.trashToShow.push(lesson);
                lesson._ui.isSelected = false;
            }
        } else {
            this._infoMessage.addSuccess("Lesson " + lesson.title + " has been deleted");
        }
        if (this.lessons) {
            this.lessons = this.lessons.filter(les => les.id != lesson.id);
        }
        this.selectedLessons = this.selectedLessons.filter(l => l.id !== lesson.id);
        lesson.isDeleted = true;
    }

    private errorDeleteCallback(lesson: Lesson) {
        if (lesson.contentType.isAddon()) {
            this._infoMessage.addError("Addon " + lesson.title + " has NOT been deleted");
        } else {
            this._infoMessage.addError("Lesson " + lesson.title + " has NOT been deleted");
        }
    }

    private _deleteMyContentLesson(lesson: Lesson) {
        this._myContent.deleteLesson(lesson.id).subscribe(
            (success) => {
                this.succesDeleteCallback(lesson);
            },
            (error) => {
                this.errorDeleteCallback(lesson);
            })
    }

    private _deleteProjectLesson(lesson: Lesson) {
        this._myContent.deleteCorporateLesson(lesson.id).subscribe(
            (success) => {
                this.succesDeleteCallback(lesson);
            },
            (error) => {
                this.errorDeleteCallback(lesson);
            })
    }

    private _deleteLessons() {
        if (!this.isProject) {
            this.selectedLessons.forEach(lesson => {
                this._deleteMyContentLesson(lesson);
            });
        } else {
            this.selectedLessons.forEach(lesson => {
                this._deleteProjectLesson(lesson);
            });
        }
    }

    private _markSelectedLessons(lessons: Lesson[], selectedLessons: Lesson[]) {
        if (this.lessons != undefined) {
            lessons.forEach(lesson => {
                if (selectedLessons.some(l => l.id === lesson.id)) {
                    lesson._ui.isSelected = true;
                }
            });
        }
    }

    public undeleteLesson(lesson: Lesson) {
        this.trashToShow = this.trashToShow.filter(les => les.id != lesson.id);
        this.addonsToShow.push(lesson);
    }

    public downloadPublications(project: Space) {
        if (!project.publications) {
            this._projects.getPublications(project.id).subscribe((publications) => {
                this.projects.forEach((p: Space) => {
                    if (p.id === project.id) {
                        p.publications = publications;
                    }
                });
            });
        }
    }

    private successUndeleteCallback() {
        if (this.selectedLesson.contentType.isAddon()) {
            this._infoMessage.addSuccess("Addon " + this.selectedLesson.title + " has been undeleted");
        } else {
            this._infoMessage.addSuccess("Lesson " + this.selectedLesson.title + " has been undeleted");
        }
        this.selectedLesson.isDeleted = false;
        this._backToList();
    }

    private errorUndeleteCallback() {
        if (this.selectedLesson.contentType.isAddon()) {
            this._infoMessage.addError("Addon " + this.selectedLesson.title + " has NOT been undeleted");
        } else {
            this._infoMessage.addError("Lesson " + this.selectedLesson.title + " has NOT been undeleted");
        }
    }

    public undelete(event) {
        event.stopPropagation();
        if (this.userPermissions && this.userPermissions.contentRemoveLessonsAddons) {
            if (!this.isProject) {
                this._myContent.undeleteLesson(this.selectedLesson.id).subscribe(
                    (success) => {
                        this.successUndeleteCallback();
                    },
                    (error) => {
                        this.errorUndeleteCallback();
                    }
                )
            } else {
                this._myContent.deleteCorporateLesson(this.selectedLesson.id).subscribe(
                    (success) => {
                        this.successUndeleteCallback();
                    },
                    (error) => {
                        this.errorUndeleteCallback();
                    }
                )
            }
        }
    }
}
