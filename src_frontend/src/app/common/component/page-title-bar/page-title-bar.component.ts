import { Component, Input } from "@angular/core";
import { Router } from "@angular/router";


declare var window: any;

@Component({
    selector: 'page-title-bar',
    template: `<div class="page-title-bar flex-row" [ngClass]="{'with-back': withBack, 'with-dots': withDots}">
        <div class="page-title-bar__header">
            <button *ngIf="withBack" (click)="goBack()" class="mdl-button mdl-js-button mdl-button--fab mdl-button--colored back-button">
               <i class="material-icons">chevron_left</i>
            </button>
        
            <ng-content select=".title"></ng-content>

            <div *ngIf="withNavigation" class="navigation">
                <ng-content select=".navigation-item"></ng-content>
            </div>
        </div>
        <div *ngIf="withDots" class="page-title-bar__menu">
            <button id="dots-menu-button" class="mdl-button mdl-js-button mdl-button--icon">
                <i class="material-icons">more_vert</i>
            </button>

            <ul mdl class="mdl-menu mdl-menu--bottom-right mdl-js-menu mdl-js-ripple-effect" for="dots-menu-button">
                <ng-content select=".dots-menu-item"></ng-content>
            </ul>
        </div>
    </div>`
})
export class PageTitleBarComponent {
    @Input() withDots: boolean = false;
    @Input() withNavigation: boolean = false;
    @Input() withBack: boolean = false;
    @Input() backUrl: string = '/home';
    @Input() isBackUrlInApp: boolean = true;

    constructor (
        private _router: Router
    ) {}

    public goBack () {
        if (this.isBackUrlInApp) {
            this._router.navigateByUrl(this.backUrl);
        } else {
            window.location.href = this.backUrl;
        }
    }
}
