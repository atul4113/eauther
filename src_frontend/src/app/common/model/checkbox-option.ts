export class CheckboxOption {
    constructor(
        public readonly content: string,
        public value: string | number | boolean,
        public readonly displayName?: string
    ) {}
}
