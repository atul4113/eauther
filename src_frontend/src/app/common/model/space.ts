import { Subspace } from "./subspace";
import { RolePermissions } from "./auth-user";
export interface ISpaceRaw {
    id: number;
    title: string;
    is_locked?: boolean;
    is_owner?: boolean;
    is_admin?: boolean;
    number_of_publications?: number;
    publications?: ISpaceRaw[];
    // kanban?: any;
}

export class Space {
    public id: number;
    public title: string;
    public isLocked: boolean = false;
    public isOwner: boolean = false;
    public isAdmin: boolean = false;
    public numberOfPublications: number = 0;
    public roles: string[];
    public userPermissions: RolePermissions;
    // public kanban: any = [];

    public structure?: Subspace;
    public publications?: Space[] = [];

    constructor (space: ISpaceRaw) {
        this.id = space.id;
        this.title = space.title;

        if (space.is_locked) {
            this.isLocked = space.is_locked;
        }
        if (space.is_owner) {
            this.isOwner = space.is_owner;
        }
        if (space.is_admin) {
            this.isAdmin = space.is_admin;
        }
        if (space.number_of_publications) {
            this.numberOfPublications = space.number_of_publications;
        }
        if (space.publications) {
            this.publications = space.publications.map( publication => new Space(publication));
        }
        // if (space.kanban) {
        //     this.kanban = space.kanban;
        // }
    }
}
