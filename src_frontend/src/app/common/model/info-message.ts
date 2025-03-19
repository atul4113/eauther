export const INFO_MESSAGE_TYPE = {
    ERROR: "error",
    INFO: "info",
    WARNING: "warning",
    SUCCESS: "success",
} as const;

type InfoMessageType =
    (typeof INFO_MESSAGE_TYPE)[keyof typeof INFO_MESSAGE_TYPE];

export class InfoMessage {
    constructor(
        private readonly type: InfoMessageType,
        public readonly content: string,
        private readonly closeable: boolean = true,
        private readonly autoClose: boolean = true
    ) {}

    public isError(): boolean {
        return this.type === INFO_MESSAGE_TYPE.ERROR;
    }

    public isInfo(): boolean {
        return this.type === INFO_MESSAGE_TYPE.INFO;
    }

    public isWarning(): boolean {
        return this.type === INFO_MESSAGE_TYPE.WARNING;
    }

    public isSuccess(): boolean {
        return this.type === INFO_MESSAGE_TYPE.SUCCESS;
    }

    public isCloseable(): boolean {
        return this.closeable;
    }

    public isAutoClose(): boolean {
        return this.autoClose;
    }
}
