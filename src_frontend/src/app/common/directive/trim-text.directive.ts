import {
    Directive,
    AfterViewInit,
    OnDestroy,
    ElementRef,
    Input,
    OnChanges,
    SimpleChanges,
} from "@angular/core";

declare let window: any;

interface TrimTextParams {
    text: string;
    height: number;
}

@Directive({
    selector: "[trim-text]",
})
export class TrimText implements AfterViewInit, OnDestroy, OnChanges {
    @Input("trim-text") params!: TrimTextParams;
    @Input("trim-separator") separator: string = " ";

    private native: HTMLElement;
    private readonly onWindowResize: () => void;

    constructor(private readonly el: ElementRef<HTMLElement>) {
        this.native = el.nativeElement;
        this.onWindowResize = this.trim.bind(this);
    }

    ngAfterViewInit(): void {
        if (this.params && this.params.text.length > 0) {
            this.native.innerHTML = this.params.text;
            this.trim();
            window.addEventListener("resize", this.onWindowResize);
        }
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (this.params && this.params.text.length > 0) {
            this.native.innerHTML = this.params.text;
            this.trim();
        }
    }

    ngOnDestroy(): void {
        window.removeEventListener("resize", this.onWindowResize);
    }

    private trim(): void {
        let text: string = this.params.text;
        while (this.native.clientHeight > this.params.height) {
            text = this.cutLastWord(text);
            this.native.innerHTML = text + "...";
        }
    }

    private cutLastWord(text: string): string {
        const parts: string[] = text.split(this.separator);
        parts.pop();
        return parts.join(this.separator);
    }
}
