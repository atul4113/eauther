import { User, IUserRaw } from "./user";
import { ISpaceRaw, Space } from "./space";

const PERMISSIONS = {
    assetsBrowseAssets: 1,
    assetsUploadEditAssets: 2,
    assetsRemoveAssets: 3,
    contentViewLessonsAddons: 4,
    contentRemoveLessonsAddons: 5,
    contentEditMetadataOfLessonsAddons: 6,
    contentPublishLessons: 7,
    contentCopyLessons: 8,
    contentCreateEditLessonsAddons: 9,
    contentUploadLessonsAddonsIcon: 10,
    contentShowLessonsHistory: 11,
    contentSetLessonsCurrentVersion: 12,
    contentExportLessons: 13,
    contentImportLessons: 14,
    spaceManageAccessToProjectsPublications: 15,
    spaceCreateEditProjectsPublications: 16,
    spaceRemoveProjectsPublications: 17,
    spaceCreateRestoreProjectsBackup: 18,
    companyUploadCompanyLogo: 19,
    companyViewCompanyDetails: 20,
    companyEditCOmpanyDetails: 21,
    companyViewCompanyAdministrationPanel: 22,
    bugtruckReportNewBugsInBugtruck: 23,
    narrationExportAudioVideoNarrations: 24,
    localizationCreateLessonsForLocalization: 25,
    localizationLocalizeLessonsPreparedForLocalization: 26,
    localizationResetLocalizationLessonsToOriginalCurrentLesson: 27,
    localizationExportXLIFF: 28,
    localizationImportXLIFF: 29,
    statesManageAvailableStateSets: 30,
    statesSelectStateSetForPublication: 31,
    courseManageCourses: 32,
    spaceBulkTemplateUpdate: 33,
    spaceBulkAssetsUpdate: 34,
    bugtruckViewBugs: 35
};

export class RolePermissions {
    public assetsBrowseAssets: boolean = false;
    public assetsUploadEditAssets: boolean = false;
    public assetsRemoveAssets: boolean = false;
    public contentViewLessonsAddons: boolean = false;
    public contentRemoveLessonsAddons: boolean = false;
    public contentEditMetadataOfLessonsAddons: boolean = false;
    public contentPublishLessons: boolean = false;
    public contentCopyLessons: boolean = false;
    public contentCreateEditLessonsAddons: boolean = false;
    public contentUploadLessonsAddonsIcon: boolean = false;
    public contentShowLessonsHistory: boolean = false;
    public contentSetLessonsCurrentVersion: boolean = false;
    public contentExportLessons: boolean = false;
    public contentImportLessons: boolean = false;
    public spaceManageAccessToProjectsPublications: boolean = false;
    public spaceCreateEditProjectsPublications: boolean = false;
    public spaceRemoveProjectsPublications: boolean = false;
    public spaceCreateRestoreProjectsBackup: boolean = false;
    public companyUploadCompanyLogo: boolean = false;
    public companyViewCompanyDetails: boolean = false;
    public companyEditCompanyDetails: boolean = false;
    public companyViewCompanyAdministrationPanel: boolean = false;
    public bugtruckReportNewBugsInBugtruck: boolean = false;
    public narrationExportAudioVideoNarrations: boolean = false;
    public localizationCreateLessonsForLocalization: boolean = false;
    public localizationLocalizeLessonsPreparedForLocalization: boolean = false;
    public localizationResetLocalizationLessonsToOriginalCurrentLesson: boolean = false;
    public localizationExportXLIFF: boolean = false;
    public localizationImportXLIFF: boolean = false;
    public statesManageAvailableStateSets: boolean = false;
    public statesSelectStateSetForPublication: boolean = false;
    public courseManageCourses: boolean = false;
    public spaceBulkTemplateUpdate: boolean = false;
    public spaceBulkAssetsUpdate: boolean = false;
    public bugtruckViewBugs: boolean = false;


    constructor (permissions?: number[]) {
        if (permissions) {
            this.assetsBrowseAssets = permissions.includes(PERMISSIONS.assetsBrowseAssets);
            this.assetsUploadEditAssets = permissions.includes(PERMISSIONS.assetsUploadEditAssets);
            this.assetsRemoveAssets = permissions.includes(PERMISSIONS.assetsRemoveAssets);
            this.contentViewLessonsAddons = permissions.includes(PERMISSIONS.contentViewLessonsAddons);
            this.contentRemoveLessonsAddons = permissions.includes(PERMISSIONS.contentRemoveLessonsAddons);
            this.contentEditMetadataOfLessonsAddons = permissions.includes(PERMISSIONS.contentEditMetadataOfLessonsAddons);
            this.contentPublishLessons = permissions.includes(PERMISSIONS.contentPublishLessons);
            this.contentCopyLessons = permissions.includes(PERMISSIONS.contentCopyLessons);
            this.contentCreateEditLessonsAddons = permissions.includes(PERMISSIONS.contentCreateEditLessonsAddons);
            this.contentUploadLessonsAddonsIcon = permissions.includes(PERMISSIONS.contentUploadLessonsAddonsIcon);
            this.contentShowLessonsHistory = permissions.includes(PERMISSIONS.contentShowLessonsHistory);
            this.contentSetLessonsCurrentVersion = permissions.includes(PERMISSIONS.contentSetLessonsCurrentVersion);
            this.contentExportLessons = permissions.includes(PERMISSIONS.contentExportLessons);
            this.contentImportLessons = permissions.includes(PERMISSIONS.contentImportLessons);
            this.spaceManageAccessToProjectsPublications = permissions.includes(PERMISSIONS.spaceManageAccessToProjectsPublications);
            this.spaceCreateEditProjectsPublications = permissions.includes(PERMISSIONS.spaceCreateEditProjectsPublications);
            this.spaceRemoveProjectsPublications = permissions.includes(PERMISSIONS.spaceRemoveProjectsPublications);
            this.spaceCreateRestoreProjectsBackup = permissions.includes(PERMISSIONS.spaceCreateRestoreProjectsBackup);
            this.companyUploadCompanyLogo = permissions.includes(PERMISSIONS.companyUploadCompanyLogo);
            this.companyViewCompanyDetails = permissions.includes(PERMISSIONS.companyViewCompanyDetails);
            this.companyEditCompanyDetails = permissions.includes(PERMISSIONS.companyViewCompanyDetails);
            this.companyViewCompanyAdministrationPanel = permissions.includes(PERMISSIONS.companyViewCompanyAdministrationPanel);
            this.bugtruckReportNewBugsInBugtruck = permissions.includes(PERMISSIONS.bugtruckReportNewBugsInBugtruck);
            this.narrationExportAudioVideoNarrations = permissions.includes(PERMISSIONS.narrationExportAudioVideoNarrations);
            this.localizationCreateLessonsForLocalization = permissions.includes(PERMISSIONS.localizationCreateLessonsForLocalization);
            this.localizationLocalizeLessonsPreparedForLocalization = permissions.includes(PERMISSIONS.localizationLocalizeLessonsPreparedForLocalization);
            this.localizationResetLocalizationLessonsToOriginalCurrentLesson = permissions.includes(PERMISSIONS.localizationResetLocalizationLessonsToOriginalCurrentLesson);
            this.localizationExportXLIFF = permissions.includes(PERMISSIONS.localizationExportXLIFF);
            this.localizationImportXLIFF = permissions.includes(PERMISSIONS.localizationImportXLIFF);
            this.statesManageAvailableStateSets = permissions.includes(PERMISSIONS.statesManageAvailableStateSets);
            this.statesSelectStateSetForPublication = permissions.includes(PERMISSIONS.statesSelectStateSetForPublication);
            this.courseManageCourses = permissions.includes(PERMISSIONS.courseManageCourses);
            this.spaceBulkTemplateUpdate = permissions.includes(PERMISSIONS.spaceBulkTemplateUpdate);
            this.spaceBulkAssetsUpdate = permissions.includes(PERMISSIONS.spaceBulkAssetsUpdate);
            this.bugtruckViewBugs = permissions.includes(PERMISSIONS.bugtruckViewBugs);
        }
    }
}

export interface IAuthUserRaw extends IUserRaw {
    is_superuser: boolean;
    language_code: string;
    is_staff: boolean;
    company?: ISpaceRaw;
    private_space?: ISpaceRaw;
    is_any_division_admin: boolean;
    // public_category?: ISpaceRaw;
    // divisions?: ISpaceRaw[];
}

export class UserPermissions {
    public isSuperUser: boolean = false;
    public isStaff: boolean = false;
    public isAnyDivisionAdmin: boolean = false;

    constructor (user?: IAuthUserRaw) {
        if (user) {
            this.isSuperUser = user.is_superuser;
            this.isStaff = user.is_staff;
            this.isAnyDivisionAdmin = user.is_any_division_admin;
        }
    }
}

export class AuthUser extends User {
    public isAuthenticated: boolean = false;
    public permissions: UserPermissions;
    public languageCode: string;
    public company: Space;
    public privateSpace: Space;
    // public publicCategory: Space;
    // public divisions: Space[];

    constructor (user?: IAuthUserRaw) {
        super(user);
        this.permissions = new UserPermissions(user);

        if (user) {
            this.isAuthenticated = true;
            this.languageCode = user.language_code;

            if (user.company) {
                this.company = new Space(user.company);
            }

            if (user.private_space) {
                this.privateSpace = new Space(user.private_space);
            }

            // if (user.public_category) {
            //     this.publicCategory = new Space(user.public_category);
            // }
            // if (user.divisions) {
            //     this.divisions = user.divisions.map( (division: ISpaceRaw) => new Space(division));
            // }
        }
    }

}
