export const INFO_MESSAGE_TYPE = {
    ERROR: 'error',
    INFO: 'info',
    WARNING: 'warning',
    SUCCESS: 'success'
};

export class InfoMessage {
    constructor (
        private type: string,
        public content: string,
        private closeable = true,
        private autoClose = true
    ) {}

    public isError = () => this.type === INFO_MESSAGE_TYPE.ERROR;

    public isInfo = () => this.type === INFO_MESSAGE_TYPE.INFO;

    public isWarning = () => this.type === INFO_MESSAGE_TYPE.WARNING;

    public isSuccess = () => this.type === INFO_MESSAGE_TYPE.SUCCESS;

    public isCloseable = () => this.closeable;

    public isAutoClose = () => this.autoClose;
}
