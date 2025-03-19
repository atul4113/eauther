export interface ILanguageRaw {
    id: number;
    lang_key: string;
    lang_description: string;
    created_date: string;
    modified_date: string;
}

export class Language {
    public id: number = 0;
    public key: string = ""; // en_EN, pl_PL
    public description: string = ""; // english, polish
    public isDefault: boolean = false;

    constructor(lang: ILanguageRaw) {
        if (lang) {
            this.id = lang.id;
            this.key = lang.lang_key;
            this.description = lang.lang_description;
            this.isDefault = false; // this is taken from a settings api
        }
    }

    public get isReal(): boolean {
        return this.id !== Language.FAKE_ID;
    }

    public static readonly FAKE_ID: number = -1;
}

// used in browse labels view, to allow filtering by all languages
export const ALL_LANGUAGE: Language = new Language({
    id: Language.FAKE_ID,
    lang_key: "all",
    lang_description: "all languages",
    created_date: "",
    modified_date: "",
});
