import { Routes } from '@angular/router';

import { MyLessonsComponent } from "./component/my-lessons/my-lessons.component";
import { AuthGuard } from "../common/guard/auth.guard";
import { CreateLessonComponent } from "./component/create-lesson/create-lesson.component";


export const MyLessonsRoutes: Routes = [
    {
        path: '',
        component: MyLessonsComponent,
        canActivate: [AuthGuard],
        data: { isProject: false }
    },
    {
        path: ':id',
        component: MyLessonsComponent,
        canActivate: [AuthGuard],
        data: { isProject: false }
    },
    {
        path: ':id/trash',
        component: MyLessonsComponent,
        canActivate: [AuthGuard],
        data: { isProject: false, isTrash: true }
    },
    {
        path: 'list/:id',
        component: MyLessonsComponent,
        canActivate: [AuthGuard],
        data: { isProject: true }
    },
    {
        path: 'list/:id/trash',
        component: MyLessonsComponent,
        canActivate: [AuthGuard],
        data: { isProject: true, isTrash: true }
    },
    {
        path: 'addcontent/:id/next/:next',
        component: CreateLessonComponent,
        canActivate: [AuthGuard],
        data: { isProject: true }
    },
    {
        path: 'view/:id',
        component: MyLessonsComponent,
        canActivate: [AuthGuard],
        data: { isView:true }
    },
    {
        path: 'list/:id/addons',
        component: MyLessonsComponent,
        canActivate: [AuthGuard],
        data: { isTrash: false, isAddons: true }
    },
    {
        path: ':id/addons',
        component: MyLessonsComponent,
        canActivate: [AuthGuard],
        data: {  isTrash: false, isAddons: true }
    },
];
