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
    @Input("putFooterBottom") paddingAndMargin = 0;

    private native: any;
    private footer: any;
    private windowListenResizeFunc: any;

    constructor(el: ElementRef, private _renderer: Renderer2) {
        this.native = el.nativeElement;
    }

    ngAfterViewInit() {
        this.footer = document.getElementsByTagName("footer")[0];
        this.onResize();
        this.windowListenResizeFunc = this._renderer.listen(
            "window",
            "resize",
            () => this.onResize()
        );
    }

    ngOnDestroy() {
        this.footer = null;
        this.windowListenResizeFunc();
    }

    private hasScrollBar() {
        return document.body.scrollHeight > document.body.clientHeight;
    }

    private onResize() {
        if (this.native && this.footer) {
            let headerHeight = this.native.offsetTop;
            let footerHeight = this.footer.clientHeight;
            let windowHeight = window.innerHeight;

            if (headerHeight === 0 || footerHeight < 265) {
                setTimeout(() => this.onResize(), 100);
            } else {
                let minHeight =
                    windowHeight -
                    headerHeight -
                    footerHeight -
                    this.paddingAndMargin;

                let hasScrollBarBefore = this.hasScrollBar();
                this.native.style.minHeight = minHeight;
                let hasScrollBarAfter = this.hasScrollBar();

                if (!hasScrollBarBefore && hasScrollBarAfter) {
                    setTimeout(() => this.onResize(), 100);
                }
            }
        } else {
            setTimeout(() => this.onResize(), 100);
        }
    }
}
