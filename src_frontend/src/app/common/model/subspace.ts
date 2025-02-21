import { UserInterface } from "./utility";

class ISubspaceRaw {
    public id: number;
    public name: string;
    public subspaces: Subspace[];
}

export class Subspace {
    public id: number;
    public name: string;
    public subspaces: Subspace[];
    public _ui: UserInterface = new UserInterface();

    constructor (subspace: ISubspaceRaw) {
        this.id = subspace.id;
        this.name = subspace.name;
        if (subspace.subspaces) {
            this.subspaces = subspace.subspaces.map(s => new Subspace(s));
        }
    }
}
