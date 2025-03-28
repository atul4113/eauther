export interface IBugRaw {
    id: number;
    title: string;
    description: string;
    username: string;
    created_date: number;
}

export class Bug {
    public id: number;
    public title: string = '';
    public description: string = '';
    public username: any;
    public createdDate: Date;

    constructor (bug?: IBugRaw) {
        if (bug) {
            this.id = bug.id;
            this.title = bug.title;
            this.description = bug.description;
            this.username = bug.username;
            this.createdDate = new Date(bug.created_date);
        } else {
            this.createdDate = new Date();
            this.id = this.createdDate.getTime();
        }
    }

    public copy (): Bug {
        return new Bug(this.raw());
    }

    public raw (): IBugRaw {
        return {
            id: this.id,
            title: this.title,
            description: this.description,
            username: this.username,
            created_date: this.createdDate.getTime()
        }
    }
}
