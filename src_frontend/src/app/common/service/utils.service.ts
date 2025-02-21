import { Injectable } from "@angular/core";
import { ITranslations } from "../model/translations";


@Injectable()
export class UtilsService {

     public generateJson(translations: ITranslations): string {
        let generatedJson: string = '{\n';
        let counter: number = 0;
        let keys = Object.keys(translations.labels);
        for (const labItor of keys)
        {
            // order of conversions is important: first escape all slashes, then deal with special characters that generate slashes
            // (that are already escaped, hence no need to do it again)
            let value: string = translations.labels[labItor].replace(/\\/g, '\\\\')  // convert slash \ to escaped slash \\
                                                            .replace(/"/g,'\\"')     // convert quote " to escaped quote \"
                                                            .replace(/\n/g, "\\n")   // convert \n to escaped \\n
                                                            .replace(/\r/g, "\\r");  // ditto
            let txt: string = `    "${labItor}": "${value}"`;

            ++counter;
            if (counter !== keys.length)
                txt += ',\n';
            generatedJson += txt;
        }
        generatedJson += '\n}';
        return generatedJson;
    }

    public isJsonValid(json: string): boolean {
        try {
            JSON.parse(json);
        } catch (e) {
            return false;
        }
        return true;
    }

}
