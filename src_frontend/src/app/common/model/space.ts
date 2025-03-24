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
    public readonly id: number;
    public readonly title: string;
    public readonly isLocked: boolean;
    public readonly isOwner: boolean;
    public readonly isAdmin: boolean;
    public readonly numberOfPublications: number;
    public readonly roles: string[] = [];
    public readonly userPermissions: RolePermissions;
    // public kanban: any = [];

    public readonly structure?: Subspace;
    public readonly publications: Space[] = [];

    constructor(space: ISpaceRaw) {
        this.id = space.id;
        this.title = space.title;
        this.isLocked = space.is_locked ?? false;
        this.isOwner = space.is_owner ?? false;
        this.isAdmin = space.is_admin ?? false;
        this.numberOfPublications = space.number_of_publications ?? 0;
        this.userPermissions = new RolePermissions();

        if (space.publications) {
            this.publications = space.publications.map(
                (publication) => new Space(publication)
            );
        }
        // if (space.kanban) {
        //     this.kanban = space.kanban;
        // }
    }
}
