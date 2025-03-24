export interface ICategoryRaw {
    id: number;
    title: string;
    is_locked: boolean;
    is_owner: boolean;
    is_top_level: boolean;
    parent: string;
    contents_count: number;
}

export class Category {
    public id: number = 0;
    public title: string = "";
    public isLocked: boolean = false;
    public isOwner: boolean = false;
    public isTopLevel: boolean = false;
    public parent: string = "";
    public contentsCount: number = 0;

    constructor(category?: ICategoryRaw) {
        if (category) {
            this.id = category.id;
            this.title = category.title;
            this.isLocked = category.is_locked;
            this.isOwner = category.is_owner;
            this.isTopLevel = category.is_top_level;
            this.parent = category.parent;
            this.contentsCount = category.contents_count;
        }
    }
}
