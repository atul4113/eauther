import { UserInterface } from "../../common/model/utility";

export interface ILessonToMergeRaw {
  common_pages: string[];
  content_id: number;
  title: string;
  pages: string[];
}

export class LessonToMerge {
  public common_pages: string[] = [];
  public content_id: number;
  public title: string;
  public pages: string[] = [];

  constructor (mergeLesson: ILessonToMergeRaw) {
    this.common_pages = mergeLesson.common_pages;
    this.title = mergeLesson.title;
    this.content_id = mergeLesson.content_id;
    this.common_pages = mergeLesson.common_pages;
  }
}
