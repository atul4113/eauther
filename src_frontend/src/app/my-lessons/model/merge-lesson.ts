import { UserInterface } from "../../common/model/utility";

export interface IMergeLessonRaw {
  index: string;
  is_page: boolean;
  title: string;
  indent: string;
}

export class MergeLesson {
  public index: string;
  public isPage: any;
  public title: string;
  public indent: string = "";
  public _ui: UserInterface = new UserInterface();

  constructor (mergeLesson: IMergeLessonRaw) {
    this.index = mergeLesson.index;
    this.title = mergeLesson.title;
    if(mergeLesson.is_page) {
        this.isPage = mergeLesson.is_page;
    }
    if(mergeLesson.indent) {
        this.indent = mergeLesson.indent;
    }
  }
}
