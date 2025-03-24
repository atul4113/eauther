import {
    OnChanges,
    Component,
    Input,
    Output,
    EventEmitter,
    OnInit,
    SimpleChanges,
} from "@angular/core";

@Component({
    selector: "paginator-base",
    template: `
        <div class="paginator">
            <button
                (click)="prevPage()"
                [disabled]="pageIndex === 1"
                class="mdl-button mdl-js-button mdl-button--primary action-button"
            >
                <i class="material-icons">keyboard_arrow_left</i>
            </button>
            <button
                (click)="pageChanged(1)"
                [ngClass]="{ 'mdl-button--accent': pageIndex === 1 }"
                class="mdl-button mdl-js-button mdl-button--primary"
            >
                1
            </button>
            <button
                *ngIf="showLeftMore"
                (click)="setPrevRange()"
                class="mdl-button mdl-js-button mdl-button--primary"
            >
                ...
            </button>
            <button
                *ngFor="let p of pagesRange"
                (click)="pageChanged(p)"
                [ngClass]="{ 'mdl-button--accent': pageIndex === p }"
                class="mdl-button mdl-js-button mdl-button--primary"
            >
                {{ p }}
            </button>
            <button
                *ngIf="showRightMore"
                (click)="setNextRange()"
                class="mdl-button mdl-js-button mdl-button--primary"
            >
                ...
            </button>
            <button
                *ngIf="pagesCount > 1"
                (click)="pageChanged(pagesCount)"
                [ngClass]="{ 'mdl-button--accent': pageIndex === pagesCount }"
                class="mdl-button mdl-js-button mdl-button--primary"
            >
                {{ pagesCount }}
            </button>
            <button
                (click)="nextPage()"
                [disabled]="pageIndex === pagesCount || pagesCount === 0"
                class="mdl-button mdl-js-button mdl-button--primary action-button"
            >
                <i class="material-icons">keyboard_arrow_right</i>
            </button>
        </div>
    `,
})
export class PaginatorBaseComponent implements OnChanges, OnInit {
    @Input() pagesCount: number = 0;
    @Input() buttonsCount: number = 3;
    @Input() set pageIndex(value: number) {
        if (this.pageIndex !== value) {
            this._pageIndex = value;
            this.setPageRange(this._pageIndex);
        }
    }

    get pageIndex(): number {
        return this._pageIndex;
    }

    @Output() pageChange: EventEmitter<number> = new EventEmitter<number>();

    public pagesRange: number[] = [];

    public showLeftMore: boolean = true;
    public showRightMore: boolean = true;

    private _pageIndex: number = 1;

    ngOnInit(): void {
        if (this.buttonsCount % 2 === 0) {
            this.buttonsCount += 1;
        }
        this.init();
        this.pageChanged(1);
    }

    ngOnChanges(changes: SimpleChanges): void {
        this.init();
        this.pageChanged(this.pageIndex);
    }

    public pageChanged(index: number): void {
        this.pageIndex = index;
        this.pageChange.emit(this.pageIndex);
        this.setPageRange(index);
    }

    public nextPage(): void {
        if (this.pageIndex < this.pagesCount) {
            this.pageChanged(this.pageIndex + 1);
        }
    }

    public prevPage(): void {
        if (this.pageIndex > 1) {
            this.pageChanged(this.pageIndex - 1);
        }
    }

    public setPrevRange(): void {
        if (this.pagesRange.length > 0) {
            let first = this.pagesRange[0] - this.buttonsCount - 1;
            first = first > 0 ? first : 1;
            this.pagesRange = this.getRange(first);
        } else {
            this.pagesRange = this.getRange(1);
        }
    }

    public setNextRange(): void {
        if (this.pagesRange.length > 0) {
            let last = this.pagesRange[this.pagesRange.length - 1];
            this.pagesRange = this.getRange(last);
        } else {
            this.pagesRange = this.getRange(1);
        }
    }

    private init(): void {
        if (this.pageIndex > 0 && this.pageIndex > this.pagesCount) {
            this.pageIndex = this.pagesCount > 1 ? this.pagesCount : 1;
        }
    }

    private setPageRange(index: number): void {
        let siblings = (this.buttonsCount - 1) / 2;

        if (index === 1 || index === this.pagesCount) {
            this.pagesRange = this.getRange(index);
        } else if (index - siblings > 1) {
            this.pagesRange = this.getRange(index - siblings - 1);
        } else {
            this.pagesRange = this.getRange(1);
        }
    }

    private getRange(index: number): number[] {
        let range: number[] = [];

        if (this.pagesCount > index + this.buttonsCount) {
            for (let i = 1; i <= this.buttonsCount; i += 1) {
                range.push(index + i);
            }
        } else {
            for (let i = 0; i < this.buttonsCount; i += 1) {
                let index = this.pagesCount - (i + 1);
                if (index > 1) {
                    range.unshift(index);
                } else {
                    break;
                }
            }
        }

        let first = range[0];
        let last = range[range.length - 1];

        this.showLeftMore = first - 1 > 1;
        this.showRightMore = last + 1 < this.pagesCount;

        return range;
    }
}
