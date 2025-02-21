export interface IEditTokenRaw {
  token: string;
  token_key: string;
}

export class EditToken {
  public token: string;
  public tokenKey: string;

  constructor (editToken: IEditTokenRaw) {
    this.token = editToken.token;
    this.tokenKey = editToken.token_key;
  }
}
