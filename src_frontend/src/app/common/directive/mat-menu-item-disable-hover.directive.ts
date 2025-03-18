import { Directive, HostListener, OnInit } from "@angular/core";
import { MatMenuItem } from "@angular/material/menu";

@Directive({
    selector: "[mat-menu-item-disable-hover]",
})
export class MatMenuItemDisableHoverDirective implements OnInit {
    constructor(private _element: MatMenuItem) {}

    @HostListener("click", ["$event"]) onClick($event:any) {
        if (!this._element.disabled) {
            this._element._highlighted = false;
            this._element._hovered.next(this._element);
        }
    }

    ngOnInit() {
        // this._element._emitHoverEvent does not exist, so this line is removed
    }
}
