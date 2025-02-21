export interface IFileStorage {
    id: number;
    created_date: string;
    modified_date: string;
    owner: string;
    version: string;
    meta: string;
}

export class FileStorage {
    public id: number;
    public createdDate: string;
    public modifiedDate: string;
    public owner: string;
    public version: string;
    public meta: string;

    constructor (file: IFileStorage) {
        this.id = file.id;
        this.createdDate = file.created_date;
        this.modifiedDate = file.modified_date;
        this.owner = file.owner;
        this.version = file.version;
        this.meta = file.meta;
    }
}
