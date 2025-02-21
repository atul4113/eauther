import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { IUserRaw, User } from "../model/user";


describe('Common user', () => {
    const RAW_USER: IUserRaw = {
        id: 1,
        username: 'John',
        email: 'john@gmail.com'
    };

    beforeEach(async(() => {

    }));

    it('User should parse', () => {
        let newUser: User = new User(RAW_USER);

        expect(newUser.id).toBe(1);
        expect(newUser.username).toBe('John');
        expect(newUser.email).toBe('john@gmail.com');
    });
});
