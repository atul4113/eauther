import { Injectable } from "@angular/core";
import { ITranslations } from "../model/translations";

@Injectable()
export class UtilsService {
    public generateJson(translations: ITranslations): string {
        const keys = Object.keys(translations.labels);
        const entries = keys.map((key, index) => {
            const value = translations.labels[key]
                .replace(/\\/g, "\\\\") // convert slash \ to escaped slash \\
                .replace(/"/g, '\\"') // convert quote " to escaped quote \"
                .replace(/\n/g, "\\n") // convert \n to escaped \\n
                .replace(/\r/g, "\\r"); // convert \r to escaped \\r
            return `    "${key}": "${value}"${
                index < keys.length - 1 ? "," : ""
            }`;
        });

        return `{\n${entries.join("\n")}\n}`;
    }

    public isJsonValid(json: string): boolean {
        try {
            JSON.parse(json);
            return true;
        } catch {
            return false;
        }
    }
}
