import {
    CUSTOM_ELEMENTS_SCHEMA,
    NgModule,
    NO_ERRORS_SCHEMA,
} from "@angular/core";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { CommonModule } from "@angular/common";
import { HttpClientModule } from "@angular/common/http";
import { MomentModule } from "ngx-moment";

import { AppCommonModule } from "../common/app.common.module";
import { PaginatorBaseComponent } from "../common/component/paginator-base/paginator-base.component";
import { MyLessonsRoutes } from "./my-lessons.routes";
import { MyLessonsComponent } from "./component/my-lessons/my-lessons.component";
import { CategoriesListComponent } from "./component/categories-list/categories-list.component";
import { LessonCardComponent } from "./component/lesson-card/lesson-card.component";
import { LessonDetailsComponent } from "./component/lesson-details/lesson-details.component";
import { LessonsListComponent } from "./component/lessons-list/lessons-list.component";
import { LessonPagesComponent } from "./component/lesson-pages/lesson-pages.component";
import { PagesListComponent } from "./component/pages-list/pages-list.component";
import { PagesToMergeComponent } from "./component/pages-to-merge/pages-to-merge.component";
import { ProjectStructureComponent } from "./component/project-structure/project-structure.component";
import { LessonDetailsMetadataComponent } from "./component/lesson-details-metadata/lesson-details-metadata.component";
import { LessonDetailsAssetsComponent } from "./component/lesson-details-assets/lesson-details-assets.component";
import { LessonDetailsBugTrackComponent } from "./component/lesson-details-bug-track/lesson-details-bug-track.component";
import { LessonDetailsHistoryComponent } from "./component/lesson-details-history/lesson-details-history.component";
import { LessonDetailsMetadataPropertiesComponent } from "./component/lesson-details-metadata-properties/lesson-details-metadata-properties.component";
import { LessonDetailsMetadataIconComponent } from "./component/lesson-details-metadata-icon/lesson-details-metadata-icon.component";
import { LessonDetailsMetadataBaseFormComponent } from "./component/lesson-details-metadata-base-form/lesson-details-metadata-base-form.component";
import { LessonDetailsMetadataFormComponent } from "./component/lesson-details-metadata-form/lesson-details-metadata-form.component";
import { LessonDetailsMetadataPagesFormComponent } from "./component/lesson-details-metadata-pages-form/lesson-details-metadata-pages-form.component";
import { LessonDetailsMetadataBaseInfoComponent } from "./component/lesson-details-metadata-base-info/lesson-details-metadata-base-info.component";
import { LessonDetailsMetadataTitleComponent } from "./component/lesson-details-metadata-title/lesson-details-metadata-title.component";
import { LessonDetailsMetadataCustomFieldComponent } from "./component/lesson-details-metadata-custom-field/lesson-details-metadata-custom-field.component";
import { LessonDetailsBugCardComponent } from "./component/lesson-details-bug-card/lesson-details-bug-card.component";
import { LessonDetailsBugFormComponent } from "./component/lesson-details-bug-form/lesson-details-bug-form.component";
import { LessonDetailsBugFollowersComponent } from "./component/lesson-details-bug-followers/lesson-details-bug-followers.component";
import { CreateLessonComponent } from "./component/create-lesson/create-lesson.component";
import { ProjectStructureSelectComponent } from "./component/project-structure-select/project-structure-select.component";
import { MatIconModule } from "@angular/material/icon";
import { MatCardModule } from "@angular/material/card";
import { MatDividerModule } from "@angular/material/divider";
import { MatButtonModule } from "@angular/material/button";
import { MatIconRegistry } from "@angular/material/icon";
import { DomSanitizer } from "@angular/platform-browser";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { PlayerComponent } from "./component/lesson-player/lesson-player.component";
import { MatMenuModule } from "@angular/material/menu";

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        RouterModule,
        HttpClientModule,
        AppCommonModule,
        RouterModule.forChild(MyLessonsRoutes),
        MatIconModule,
        MatCardModule,
        MatDividerModule,
        MatButtonModule,
        MatProgressSpinnerModule,
        MatMenuModule,
        MomentModule,
        PaginatorBaseComponent,
    ],
    declarations: [
        MyLessonsComponent,
        CategoriesListComponent,
        LessonCardComponent,
        LessonDetailsComponent,
        LessonsListComponent,
        LessonPagesComponent,
        PagesListComponent,
        PagesToMergeComponent,
        ProjectStructureComponent,
        ProjectStructureSelectComponent,
        LessonDetailsMetadataComponent,
        LessonDetailsAssetsComponent,
        LessonDetailsBugTrackComponent,
        LessonDetailsHistoryComponent,
        LessonDetailsMetadataIconComponent,
        LessonDetailsMetadataBaseInfoComponent,
        LessonDetailsMetadataPropertiesComponent,
        LessonDetailsMetadataBaseFormComponent,
        LessonDetailsMetadataFormComponent,
        LessonDetailsMetadataPagesFormComponent,
        LessonDetailsMetadataTitleComponent,
        LessonDetailsMetadataCustomFieldComponent,
        LessonDetailsBugCardComponent,
        LessonDetailsBugFormComponent,
        LessonDetailsBugFollowersComponent,
        CreateLessonComponent,
        PlayerComponent,
    ],
    providers: [],
    exports: [],
    schemas: [CUSTOM_ELEMENTS_SCHEMA, NO_ERRORS_SCHEMA],
})
export class MyLessonsModule {
    public assetsUrl: string;

    constructor(
        private _matIconRegistry: MatIconRegistry,
        private _domSanitizer: DomSanitizer
    ) {
        this.assetsUrl = (window as any)["mAuthorAssetsUrl"] || "";

        this._matIconRegistry.addSvgIcon(
            "manage_courses",
            this._domSanitizer.bypassSecurityTrustResourceUrl(
                this.assetsUrl + "/images/icon_ManageCourses2.svg"
            )
        );
        this._matIconRegistry.addSvgIcon(
            "export",
            this._domSanitizer.bypassSecurityTrustResourceUrl(
                this.assetsUrl + "/images/icon_Export.svg"
            )
        );
        this._matIconRegistry.addSvgIcon(
            "import",
            this._domSanitizer.bypassSecurityTrustResourceUrl(
                this.assetsUrl + "/images/icon_Import.svg"
            )
        );
        this._matIconRegistry.addSvgIcon(
            "property_change",
            this._domSanitizer.bypassSecurityTrustResourceUrl(
                this.assetsUrl + "/images/icon_PropertyChange.svg"
            )
        );
        this._matIconRegistry.addSvgIcon(
            "update",
            this._domSanitizer.bypassSecurityTrustResourceUrl(
                this.assetsUrl + "/images/icon_Update.svg"
            )
        );
    }
}
