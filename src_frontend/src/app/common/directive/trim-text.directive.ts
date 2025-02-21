import {Directive, AfterViewInit, OnDestroy, ElementRef, Input, OnChanges} from '@angular/core';


declare let window: any;

@Directive({
    selector: '[trim-text]'
})
export class TrimText implements AfterViewInit, OnDestroy, OnChanges {
    @Input('trim-text') params: {text: string, height: number};

    @Input('trim-separator') separator: string = ' ';

    private native: any;

    constructor (el: ElementRef) {
        this.native = el.nativeElement;
    }

    ngAfterViewInit() {
        if (this.params && this.params.text.length > 0) {
            this.native.innerHTML = this.params.text;
            this.trim();
            
            window.addEventListener('resize', this.onWindowResize);
        }
    }

    ngOnChanges (changes: any) {
        if (this.params && this.params.text.length > 0) {
            this.native.innerHTML = this.params.text;
            this.trim();
        }
    }
    
    ngOnDestroy () {
        window.removeEventListener('resize', this.onWindowResize);
    }

    private trim () {
        let text = this.params.text;
        while (this.native.clientHeight > this.params.height) {
            text = this.cutLastWord(text);
            this.native.innerHTML = text + '...';
        }
    }

    private cutLastWord (text: string) {
        let parts = text.split(this.separator);
        parts.pop();
        return parts.join(this.separator);
    }

    private onWindowResize = () => this.trim();

}
