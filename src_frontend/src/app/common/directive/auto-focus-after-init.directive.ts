
import { Directive, AfterViewInit, ElementRef } from '@angular/core';

@Directive({
    selector: '[auto-focus-after-init]',
})
export class AutoFocusAfterInit implements AfterViewInit {
 
    constructor (private _elementRef: ElementRef) {
    }
 
    ngAfterViewInit () {
        this._elementRef.nativeElement.focus();
    }
}
