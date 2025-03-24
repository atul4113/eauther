export interface ILabelRaw {
    language: string;
    key: string;
    value: string;
}

export class UserInterface {
    isEditing: boolean = false;
}

export class Label {
    readonly language: string; // en_EN, pl_PL
    readonly key: string;
    readonly value: string;
    private readonly _ui: UserInterface;

    constructor(labelRaw?: ILabelRaw) {
        this._ui = new UserInterface();
        if (labelRaw) {
            this.language = labelRaw.language;
            this.key = labelRaw.key;
            this.value = labelRaw.value;
        } else {
            this.language = "";
            this.key = "";
            this.value = "";
        }
    }

    get isEditing(): boolean {
        return this._ui.isEditing;
    }

    set isEditing(value: boolean) {
        this._ui.isEditing = value;
    }
}
