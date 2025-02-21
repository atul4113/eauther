

export interface IUserRaw {
    id: number;
    username: string;
    email: string;
}

export class User {
    public id: number;
    public username: string = '';
    public email: string;

    constructor (user?: IUserRaw) {
        if (user) {
            this.id = user.id;
            this.username = user.username;
            this.email = user.email;
        }
    }
}