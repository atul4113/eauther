import { Component, EventEmitter, Input, OnInit, Output } from "@angular/core";

import { Language } from "../../../admin/model/language";
import { Label, ILabelRaw } from "../../../admin/model/label";
import { ITranslations } from "../../../common/model/translations";
import {
    TranslationsService,
    InfoMessageService,
    TranslationsAdminService,
} from "../../service";

interface TranslationError {
    code: number;
    additional_message?: string;
}

@Component({
    selector: "add-label",
    templateUrl: "./add-label.component.html",
})
export class AddLabelComponent implements OnInit {
    @Input() languages: Language[] = [];
    @Output() addNewLabels: EventEmitter<Label[]> = new EventEmitter<Label[]>();

    public newLabelKey: string = "";
    public newLabelValue: string = "";
    public translations: ITranslations | null = null;
    public selectedLanguage: Language | null = null;

    constructor(
        private _infoMessage: InfoMessageService,
        private _translationsAdmin: TranslationsAdminService,
        private _translations: TranslationsService
    ) {}

    ngOnInit(): void {
        this._translations
            .getTranslations()
            .subscribe((t: ITranslations | null) => {
                if (t) {
                    this.translations = t;
                }
            });
    }

    public addNewLabel(): void {
        if (
            !this._translationsAdmin.isLabelKeyValid(this.newLabelKey) ||
            this.newLabelValue.trim() === ""
        ) {
            this._infoMessage.addWarning(
                "Incorrect label key, use only letters, digits and dot."
            );
            return;
        }

        const newLabels: Label[] = [];
        let wasError: boolean = false;

        for (const lang of this.languages) {
            const labelRaw: ILabelRaw = {
                language: lang.key,
                key: this.newLabelKey,
                value: this.newLabelValue
            };
            const label = new Label(labelRaw);
            newLabels.push(label);
        }

        this._translationsAdmin.addLabel(false, newLabels[0]).subscribe(
            (result) => {
                this._infoMessage.addSuccess("Added label to languages");
                this.addNewLabels.emit(newLabels);
                this.newLabelKey = "";
                this.newLabelValue = "";
            },
            (error: TranslationError) => {
                switch (error.code) {
                    case 0:
                        this._infoMessage.addError(
                            "Translation conflict for key %s. You have to edit this label."
                        );
                        break;
                    case 1:
                        this._infoMessage.addError(
                            "Translation malformed: " + error.additional_message
                        );
                        break;
                    case 2:
                        this._infoMessage.addError(
                            "Translation label already exists"
                        );
                        break;
                    case 3:
                        this._infoMessage.addError(
                            "Translation language not exist"
                        );
                        break;
                    default:
                        this._infoMessage.addError("Unknown error");
                }
            }
        );
    }
}
