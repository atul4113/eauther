import { AfterViewInit, Directive, ElementRef, OnDestroy, Renderer2 } from '@angular/core';


declare let window: Window;

@Directive({
    selector: '[appFullScreenHeight]'
})
export class FullScreenHeightDirective implements AfterViewInit, OnDestroy {

    private native: any;
    private interval: any;
    private resizeCallback: any;

    constructor (
        el: ElementRef,
        private _renderer: Renderer2
    ) {
        this.native = el.nativeElement;
    }

    ngAfterViewInit () {
        this.interval = setInterval( () => {
            if (this.native && this.native.offsetTop > 0) {
                clearInterval(this.interval);
                this.interval = null;
                this.setHeight();
            }
        }, 100);

        this.resizeCallback = this._renderer.listen('window', 'resize', (_) => {
            this.setHeight();
        });
    }

    ngOnDestroy () {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
        if (this.resizeCallback) {
            this.resizeCallback();
        }
    }

    private setHeight () {
        if (this.native) {
            const nativeOffsetTop = this.native.offsetTop;
            const windowHeight = window.innerHeight;
            const fullHeight = windowHeight - nativeOffsetTop;

            if (fullHeight > 0) {
                this.native.style.height = fullHeight;
            }
        }
    }

}
