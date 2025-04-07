import { Pipe, PipeTransform } from "@angular/core";

/*
 * Extracts label's value from translations
 * Usage:
 *    translations | getLabel:label
 * Example:
 *   {{  translations | getLabel:"menu.home" }}
 */
@Pipe({
    name: "getLabel",
    standalone: true,
})
export class GetLabelPipe implements PipeTransform {
    transform(translations: any, name: string): string {
        if (translations && translations.labels) {
            if (translations.labels[name]) {
                return translations.labels[name];
            }

            return 'Label "' + name + '" is undefined.';
        }

        return "";
    }
}
