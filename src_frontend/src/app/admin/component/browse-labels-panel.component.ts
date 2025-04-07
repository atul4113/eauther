import { Component, OnInit } from "@angular/core";
import { forkJoin } from "rxjs";

import { ITranslations } from "../../common/model";
import { Label, ILabelRaw } from "../model/label";
import { ALL_LANGUAGE, Language } from "../model/language";
import {
    TranslationsService,
    InfoMessageService,
    TranslationsAdminService,
} from "../../common/service";
import { GlobalSettings } from "../model/global-settings";

interface SortLabelsBy {
    column: string;
    isDescent: boolean;
}

@Component({
    templateUrl: "../templates/browse-labels-panel.component.html",
})
export class BrowseLabelsPanelComponent implements OnInit {
    public translations: ITranslations | null = null;
    public isInitialized = false;
    public labelTableInitialized = false;
    public settings: GlobalSettings | null = null;
    public languages: Language[] = [];
    public labels: Label[] = [];
    public filteredLabels: Label[] | null = null;
    public labelFilter: string = "";
    public newLabelKey: string = "";
    public newLabelValue: string = "";
    public selectedLanguage: Language | null = null;
    public paginatedLabelsPage = 1;
    public pageSize = 15;
    public pageSizes: number[] = [15, 25, 50, 100, 200];
    public sortLabelsBy: SortLabelsBy = { column: "", isDescent: true };

    public exampleFormatAngular: boolean = true;
    private editedLabelValue: string = "";

    constructor(
        private _translations: TranslationsService,
        private _infoMessage: InfoMessageService,
        private _translationsAdmin: TranslationsAdminService
    ) {}

    ngOnInit() {
        this._translationsAdmin
            .getLanguagesList()
            .subscribe((langList: Language[]) => {
                this.languages = [ALL_LANGUAGE];
                this.languages.push(...langList);

                if (this.languages.length) {
                    this.selectedLanguage = this.languages[0];
                    let left: number = this.realLanguages.length;
                    this.isInitialized = true;

                    for (let lang of this.realLanguages) {
                        this._translationsAdmin
                            .getLabels(lang)
                            .subscribe(
                                (result: {
                                    labels: { [key: string]: string };
                                }) => {
                                    this.addLabelsToList(lang.key, result);
                                    left--;
                                    this.labelTableInitialized = true;
                                    if (left === 0) {
                                        this.labels = this.labels.slice(); // force table refresh
                                    }
                                }
                            );
                    }
                }
            });

        this._translations
            .getTranslations()
            .subscribe((t: ITranslations | null) => {
                if (t) {
                    this.translations = t;
                }
            });
    }

    public addLabelsToList(
        languageKey: string,
        json: { labels: { [key: string]: string } }
    ) {
        for (const labItor of Object.keys(json.labels)) {
            const labelRaw: ILabelRaw = {
                language: languageKey,
                key: labItor,
                value: json.labels[labItor],
            };
            const label = new Label(labelRaw);
            this.labels.push(label);
        }
    }

    public filterLabels(event?: KeyboardEvent) {
        // user submitted empty filter, and there already was filtered list
        if (
            ((event && event.key === "Enter") || event === undefined) &&
            this.labelFilter === "" &&
            this.filteredLabels !== null
        ) {
            this.filteredLabels = null;
            return;
        }
        if ((event && event.key !== "Enter") || this.labelFilter === "") {
            return;
        }

        this.filteredLabels = this.labels.filter(
            (l) =>
                (l.language.localeCompare(this.selectedLanguage?.key || "") ===
                    0 ||
                    this.selectedLanguage?.id === Language.FAKE_ID) &&
                (this.includes(l.value, this.labelFilter) ||
                    this.includes(l.key, this.labelFilter))
        );

        if (this.filteredLabels.length === 0) {
            this._infoMessage.addInfo("No labels matches your search criteria");
            this.filteredLabels = null;
        }
    }

    public clearLabelFilters() {
        this.labelFilter = "";
        this.filteredLabels = null;
    }

    public addNewLabels(labels: Label[]) {
        // this also forces table refresh
        this.labels = this.labels.concat(labels);
    }

    public deleteLabel(label: Label) {
        this.labels = this.labels.filter(
            (lab) => !this.areLabelsSame(lab, label)
        );
        // remove them also from the filtered array
        if (this.filteredLabels) {
            this.filteredLabels = this.filteredLabels.filter(
                (lab) => !this.areLabelsSame(lab, label)
            );
        }

        this._translationsAdmin.removeLabel(label).subscribe();
    }

    public changeSessionLanguage() {
        // todo call API
    }

    public clickInsideTextarea(label: Label) {
        label.isEditing = true;
        this.editedLabelValue = label.value;
    }

    public clickOutsideTextarea(label: Label) {
        label.isEditing = false;

        if (this.editedLabelValue.localeCompare(label.value) === 0) {
            return; // no change
        }

        let foundLang: Language | undefined = this.languages.find(
            (lang) => lang.key.localeCompare(label.language) === 0
        );
        if (!foundLang) {
            this._infoMessage.addError(
                "No language matches that in label value"
            );
            return;
        }

        this._translationsAdmin
            .modifyLabel(foundLang, label, label.value)
            .subscribe();
    }

    public sortLabels(column: string) {
        if (this.sortLabelsBy.column === column) {
            this.sortLabelsBy.isDescent = !this.sortLabelsBy.isDescent;
        } else {
            this.sortLabelsBy.column = column;
            this.sortLabelsBy.isDescent = true;
        }

        let labels: Label[] = this.filteredLabels || this.labels;

        if (this.sortLabelsBy.isDescent)
            labels.sort((a, b) =>
                this.compareLabelsField(this.sortLabelsBy, a, b)
            );
        else
            labels.sort((a, b) =>
                this.compareLabelsField(this.sortLabelsBy, b, a)
            );

        labels = labels.slice(); // force table refresh

        if (this.filteredLabels) this.filteredLabels = labels;
        else this.labels = labels;
    }

    public getSortIcon(column: string): string {
        if (this.sortLabelsBy.column === column) {
            return this.sortLabelsBy.isDescent ? "&#xE313;" : "&#xE316;";
        }
        return "&#xE15B;";
    }

    public getTranslationExample(key: string): string {
        if (this.exampleFormatAngular)
            return '{{ translations | getLabel:"' + key + '" }}';
        else return 'this.translations.labels["' + key + '"]';
    }

    private compareLabelsField(
        sortObject: SortLabelsBy,
        a: Label,
        b: Label
    ): number {
        switch (sortObject.column) {
            case "lang":
                return a.language.localeCompare(b.language);
            case "key":
                return a.key.localeCompare(b.key);
            case "value":
                return a.value.localeCompare(b.value);
            default:
                return 0;
        }
    }

    private areLabelsSame(lab: Label, label: Label): boolean {
        return lab.key.localeCompare(label.key) === 0;
    }

    get realLanguages(): Language[] {
        if (this.languages) {
            return this.languages.filter((lang) => lang.isReal);
        }
        return [];
    }

    private includes = (str: string, expr: string): boolean =>
        (str || "").toLowerCase().indexOf(expr.toLowerCase()) !== -1;
}
