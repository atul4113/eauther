import { async } from '@angular/core/testing';
import { UtilsService } from "../../common/service/utils.service";
import { ITranslations } from "../../common/model/translations";


describe('Json generator', () => {

    let utils: UtilsService;
    let iTranslations: ITranslations;

    beforeEach(async(() => {
         utils = new UtilsService();
         iTranslations = { labels: null, images: null };
    }));

    it('empty', () => {
        let json = { };
        iTranslations.labels = json;
        let str: string = utils.generateJson(iTranslations);

        expect(str).toBe('{\n\n}');
    });

    it('one label', () => {
        let json = { abc: "123" };
        iTranslations.labels = json;
        let str: string = utils.generateJson(iTranslations);

        expect(str).toBe('{\n    "abc": "123"\n}');
    });

    it('two labels', () => {
        let json = { abc: "123", foo: "bar" };
        iTranslations.labels = json;
        let str: string = utils.generateJson(iTranslations);

        expect(str).toBe('{\n    "abc": "123",\n    "foo": "bar"\n}');
    });

    it('\\n line breaks inside', () => {
        let json = { abc: "123\n456\n789" };
        iTranslations.labels = json;
        let str: string = utils.generateJson(iTranslations);

        expect(str).toBe('{\n    "abc": "123\\n456\\n789"\n}');
    });

    it('\\n line breaks inside and at end', () => {
        let json = { abc: "123\n" };
        iTranslations.labels = json;
        let str: string = utils.generateJson(iTranslations);

        expect(str).toBe('{\n    "abc": "123\\n"\n}');
    });

    it('\\r line breaks inside', () => {
        let json = { abc: "123\r456\r789" };
        iTranslations.labels = json;
        let str: string = utils.generateJson(iTranslations);

        expect(str).toBe('{\n    "abc": "123\\r456\\r789"\n}');
    });

    it('double quotes', () => {
        let json = { abc: '"quote"' };
        iTranslations.labels = json;
        let str: string = utils.generateJson(iTranslations);

        expect(str).toBe('{\n    "abc": "\\\"quote\\\""\n}');    });

    it('incorrect characters', () => {
        let json = { abc: "shouldn\\t" };
        iTranslations.labels = json;
        let str: string = utils.generateJson(iTranslations);

        expect(str).toBe('{\n    "abc": "shouldn\\\\t"\n}');    });

    it('slashes', () => {
        let json = { abc: "slash\\slash" };
        iTranslations.labels = json;
        let str: string = utils.generateJson(iTranslations);

        expect(str).toBe('{\n    "abc": "slash\\\\slash"\n}');    });
});
