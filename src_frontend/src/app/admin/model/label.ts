
export interface ILabelRaw {
    language: string;
    key: string;
    value: string;
}


export class UserInterface {
    public isEditing: boolean = false
}

export class Label {
  language: string;  // en_EN, pl_PL
  key: string;
  value: string;
  _ui: UserInterface;

  constructor() {
      this._ui = new UserInterface();
  }

}
