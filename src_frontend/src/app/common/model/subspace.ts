import { UserInterface } from "./utility";

interface ISubspaceRaw {
    id: number;
    name: string;
    subspaces?: ISubspaceRaw[];
}

export class Subspace {
    public readonly id: number;
    public readonly name: string;
    public readonly subspaces: Subspace[];
    public readonly _ui: UserInterface = new UserInterface();

    constructor(subspace: ISubspaceRaw) {
        this.id = subspace.id;
        this.name = subspace.name;
        this.subspaces = subspace.subspaces?.map((s) => new Subspace(s)) ?? [];
    }
}
