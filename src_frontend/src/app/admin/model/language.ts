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

    constructor(lang: ILanguageRaw) {
        if (!lang) {
            throw new Error("Language data is required");
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
}

// used in browse labels view, to allow filtering by all languages
export const ALL_LANGUAGE: Language = new Language({
    id: Language.FAKE_ID,
    lang_key: "all",
    lang_description: "all languages",
    created_date: "",
    modified_date: "",
});
