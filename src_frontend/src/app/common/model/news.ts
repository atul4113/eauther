export interface INewsRaw {
    published: string;
    link: string;
    summary: string;
    title: string;
}

export class News {
    public published: string = "";
    public link: string = "";
    public summary: string = "";
    public title: string = "";

    constructor(news?: INewsRaw) {
        if (news) {
            this.published = news.published;
            this.link = news.link;
            this.summary = news.summary;
            this.title = news.title;
        }
    }
}
