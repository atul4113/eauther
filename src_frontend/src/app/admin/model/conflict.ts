export interface IConflict {
    lang_key: string;
    name: string;
    new_value: string;
    old_value: string;
}

export class Conflict {
    readonly languageKey: string;
    readonly name: string;
    readonly newValue: string;
    readonly oldValue: string;
    replace: boolean;

    constructor(con: IConflict) {
        if (!con) {
            throw new Error("Conflict data is required");
        }
        this.languageKey = con.lang_key;
        this.name = con.name;
        this.newValue = con.new_value;
        this.oldValue = con.old_value;
        this.replace = true;
    }
}

export interface IResolvedConflict {
    lang_key: string;
    name: string;
    value: string;
    checked: boolean;
}

export class ResolvedConflict implements IResolvedConflict {
    readonly lang_key: string;
    readonly name: string;
    readonly value: string;
    checked: boolean;

    constructor(con: Conflict) {
        if (!con) {
            throw new Error("Conflict is required");
        }
        this.lang_key = con.languageKey;
        this.name = con.name;
        this.value = con.newValue;
        this.checked = con.replace;
    }
}
