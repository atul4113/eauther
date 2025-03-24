export interface ILabelRaw {
    language: string;
    key: string;
    value: string;
}

export class UserInterface {
    public isEditing: boolean = false;
}

export class Label {
    public language: string = ""; // en_EN, pl_PL
    public key: string = "";
    public value: string = "";
    public readonly _ui: UserInterface;

    constructor(label?: ILabelRaw) {
        this._ui = new UserInterface();
        if (label) {
            this.language = label.language;
            this.key = label.key;
            this.value = label.value;
        }
    }
}
