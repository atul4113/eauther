import { Pipe, PipeTransform } from '@angular/core';


/*
 * Usage:
 *    *ngFor="let item of items | paginate: pageIndex: pageSize"
*/
@Pipe({
    name: 'paginate'
})
export class PaginatePipe implements PipeTransform {

    transform(list: any[] = [], page: number = 1, pageSize: number = 20): any {
        return this.getPage(list, page, pageSize);
    }

    private getPage (list: any[], index: number, pageSize: number) {
        index = this.checkIndex(list, index, pageSize);
        let i = index - 1;
        let start = i * pageSize;
        let end = (i + 1) * pageSize;

        return list.slice(start, end);
    }

    private checkIndex (list: any[], index: number, pageSize: number) {
        if (index > 0 && index * pageSize <= list.length) {
            return index;
        } else if (index < 1) {
            return 1;
        } else {
            return Math.ceil(list.length / pageSize);
        }
    }
}
