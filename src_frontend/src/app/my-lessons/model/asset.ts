import { FileData } from "../../common/model/upload-file";

export interface IAssetRaw {
    href: string;
    content_type: string;
    title: string;
    file_name: string;
    created_date: number;
    size: number;
}

export class Asset {
    public href: string;
    public contentType: string;
    public title: string;
    public fileName: string;
    public createdDate: number;
    public size: number;

    constructor(asset: IAssetRaw) {
        this.href = asset.href;
        this.contentType = asset.content_type;
        this.title = asset.title;
        this.fileName = asset.file_name;
        this.createdDate = asset.created_date;
        this.size = asset.size;
    }

    public getFormattedSize(): string { // code from http://stackoverflow.com/a/18650828
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        if (this.size === 0) return 'n/a';
        const i = Math.floor(Math.floor(Math.log(this.size) / Math.log(1024)));
        if (i === 0) return `${this.size} ${sizes[i]}`;
        return `${(this.size / (1024 ** i)).toFixed(1)} ${sizes[i]}`;
    }

    public static fromFile(file: FileData) {
        return new Asset({
            href: file.link,
            content_type: file.type,
            title: file.name,
            file_name: file.name,
            size: file.size,
            created_date: (new Date()).getTime()
        });
    }
}
