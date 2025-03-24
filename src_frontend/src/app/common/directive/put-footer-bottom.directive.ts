import {
    Directive,
    AfterViewInit,
    OnDestroy,
    ElementRef,
    Renderer2,
    Input,
} from "@angular/core";

declare var document: any;
declare var window: any;

@Directive({
    selector: "[putFooterBottom]",
})
export class PutFooterBottom implements AfterViewInit, OnDestroy {
    @Input("putFooterBottom") paddingAndMargin: number = 0;

    private native: HTMLElement;
    private footer: HTMLElement | null = null;
    private windowListenResizeFunc: () => void;

    constructor(
        private readonly el: ElementRef,
        private readonly _renderer: Renderer2
    ) {
        this.native = el.nativeElement;
        this.windowListenResizeFunc = () => {};
    }

    ngAfterViewInit(): void {
        this.footer = document.getElementsByTagName("footer")[0];
        this.onResize();
        this.windowListenResizeFunc = this._renderer.listen(
            "window",
            "resize",
            () => this.onResize()
        );
    }

    ngOnDestroy(): void {
        this.footer = null;
        this.windowListenResizeFunc();
    }

    private hasScrollBar(): boolean {
        return document.body.scrollHeight > document.body.clientHeight;
    }

    private onResize(): void {
        if (this.native && this.footer) {
            const headerHeight: number = this.native.offsetTop;
            const footerHeight: number = this.footer.clientHeight;
            const windowHeight: number = window.innerHeight;

            if (headerHeight === 0 || footerHeight < 265) {
                setTimeout(() => this.onResize(), 100);
            } else {
                const minHeight: number =
                    windowHeight -
                    headerHeight -
                    footerHeight -
                    this.paddingAndMargin;

                const hasScrollBarBefore: boolean = this.hasScrollBar();
                this.native.style.minHeight = `${minHeight}px`;
                const hasScrollBarAfter: boolean = this.hasScrollBar();

                if (!hasScrollBarBefore && hasScrollBarAfter) {
                    setTimeout(() => this.onResize(), 100);
                }
            }
        } else {
            setTimeout(() => this.onResize(), 100);
        }
    }
}
