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
    id: number;
    title: string;
    isLocked: boolean;
    isOwner: boolean;
    isTopLevel: boolean;
    parent: string;
    contentsCount: number;

    constructor (category?: ICategoryRaw) {
        if (category) {
            this.id = category.id;
            this.title = category.title;
            this.isLocked = category.is_locked;
            this.isOwner = category.is_owner;
            this.isTopLevel = category.is_top_level;
            this.contentsCount = category.contents_count;
        }
    }
}
