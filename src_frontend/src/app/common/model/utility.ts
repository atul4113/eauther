export class UserInterface {

    public isSelected: boolean = false;
    public isExpanded: boolean = false;
    public isIndeterminate: boolean = false;

    constructor () {}

    public toggleSelect () {
        this.isSelected = !this.isSelected;
    }

    // FIXME
    public toggleExpand (isExpanded?: boolean) {
        this.isExpanded = isExpanded !== undefined ? isExpanded : !this.isExpanded;
    }

}
