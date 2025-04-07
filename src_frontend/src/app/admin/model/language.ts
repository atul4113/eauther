export interface ILanguageRaw {
    id: number;
    lang_key: string;
    lang_description: string;
    created_date: string;
    modified_date: string;
}

export class Language {
    readonly id: number;
    readonly key: string; // en_EN, pl_PL
    readonly description: string; // english, polish
    readonly isDefault: boolean;

    constructor(lang: ILanguageRaw | null) {
        if (!lang) {
            this.id = 0;
            this.key = "";
            this.description = "";
            this.isDefault = false;
            return;
        }
        this.id = lang.id;
        this.key = lang.lang_key;
        this.description = lang.lang_description;
        this.isDefault = false; // this is taken from a settings api
    }

    get isReal(): boolean {
        return this.id !== Language.FAKE_ID;
    }

    static readonly FAKE_ID: number = -1;

    static createNew(key: string, description: string): Language {
        return new Language({
            id: 0,
            lang_key: key,
            lang_description: description,
            created_date: "",
            modified_date: "",
        });
    }
}

// used in browse labels view, to allow filtering by all languages
export const ALL_LANGUAGE: Language = new Language({
    id: Language.FAKE_ID,
    lang_key: "all",
    lang_description: "all languages",
    created_date: "",
    modified_date: "",
});
