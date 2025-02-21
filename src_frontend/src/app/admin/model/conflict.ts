
export interface IConflict {
    lang_key: string;
    name: string;
    new_value: string;
    old_value: string;
}

export class Conflict {
    languageKey: string;
    name: string;
    newValue: string;
    oldValue: string;
    replace: boolean;

    constructor(con: IConflict) {
        if (con) {
            this.languageKey = con.lang_key;
            this.name = con.name;
            this.newValue = con.new_value;
            this.oldValue = con.old_value;
        }
        this.replace = true;
    }
}

export class ResolvedConflict {
    lang_key: string;
    name: string;
    value: string;
    checked: boolean;

    constructor(con: Conflict) {
        if (con) {
            this.lang_key = con.languageKey;
            this.name = con.name;
            this.value = con.newValue;
            this.checked = con.replace;
        }
    }
}
