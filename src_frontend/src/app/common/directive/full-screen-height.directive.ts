import {
    AfterViewInit,
    Directive,
    ElementRef,
    OnDestroy,
    Renderer2,
} from "@angular/core";

declare let window: Window;

@Directive({
    selector: "[appFullScreenHeight]",
})
export class FullScreenHeightDirective implements AfterViewInit, OnDestroy {
    private native: HTMLElement;
    private interval: number | null = null;
    private resizeCallback: () => void;

    constructor(
        private readonly el: ElementRef<HTMLElement>,
        private readonly _renderer: Renderer2
    ) {
        this.native = el.nativeElement;
        this.resizeCallback = () => {};
    }

    ngAfterViewInit(): void {
        this.interval = window.setInterval(() => {
            if (this.native && this.native.offsetTop > 0) {
                if (this.interval) {
                    window.clearInterval(this.interval);
                    this.interval = null;
                }
                this.setHeight();
            }
        }, 100);

        this.resizeCallback = this._renderer.listen("window", "resize", () => {
            this.setHeight();
        });
    }

    ngOnDestroy(): void {
        if (this.interval) {
            window.clearInterval(this.interval);
            this.interval = null;
        }
        if (this.resizeCallback) {
            this.resizeCallback();
        }
    }

    private setHeight(): void {
        if (this.native) {
            const nativeOffsetTop: number = this.native.offsetTop;
            const windowHeight: number = window.innerHeight;
            const fullHeight: number = windowHeight - nativeOffsetTop;

            if (fullHeight > 0) {
                this.native.style.height = `${fullHeight}px`;
            }
        }
    }
}
