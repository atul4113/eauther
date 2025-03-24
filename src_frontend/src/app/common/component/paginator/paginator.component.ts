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
    selector: "paginator",
    template: ` <paginator-base
        [pagesCount]="pagesCount"
        [buttonsCount]="buttonsCount"
        (pageChange)="pageChanged($event)"
    >
    </paginator-base>`,
})
export class PaginatorComponent implements OnChanges, OnInit {
    @Input() list: unknown[] = [];
    @Input() pageSize: number = 20;
    @Input() buttonsCount: number = 3;

    @Output() pageChange: EventEmitter<number> = new EventEmitter<number>();

    public pagesCount: number = 0;
    public pageIndex: number = 1;

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
    }

    private init(): void {
        this.pagesCount = Math.ceil(this.list.length / this.pageSize);
    }
}
