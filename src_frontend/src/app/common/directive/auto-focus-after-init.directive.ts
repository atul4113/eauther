import { Directive, AfterViewInit, ElementRef } from "@angular/core";

@Directive({
    selector: "[auto-focus-after-init]",
})
export class AutoFocusAfterInit implements AfterViewInit {
    constructor(private readonly _elementRef: ElementRef<HTMLElement>) {}

    ngAfterViewInit(): void {
        this._elementRef.nativeElement.focus();
    }
}
