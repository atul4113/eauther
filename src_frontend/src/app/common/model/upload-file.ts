export interface IFileDataRaw {
    filename: string;
    type: string;
    size: number;
    id: number;
}

export class FileData {
    constructor(
        public name: string,
        public type: string,
        public size: number,
        public fileId: number | null = null,
        public isUploaded: boolean = false
    ) {}

    public static fromRaw(fileData: IFileDataRaw): FileData {
        return new FileData(
            fileData.filename,
            fileData.type,
            fileData.size,
            fileData.id,
            true
        );
    }

    public getFormattedSize(): string {
        // code from http://stackoverflow.com/a/18650828
        const sizes = ["B", "KB", "MB", "GB", "TB"];
        if (this.size === 0) return "n/a";
        const i = Math.floor(Math.floor(Math.log(this.size) / Math.log(1024)));
        if (i === 0) return `${this.size} ${sizes[i]}`;
        return `${(this.size / 1024 ** i).toFixed(1)} ${sizes[i]}`;
    }

    public get link(): string {
        return "/file/serve/" + this.fileId;
    }
}

export class UploadFileError {
    constructor(public response: string, public status: number) {}
}
