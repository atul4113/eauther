/**
 * angular2-cookie - Implementation of Angular 1.x $cookies service to Angular 2
 * @version v1.2.5
 * @link https://github.com/salemdar/angular2-cookie#readme
 * @license MIT
 */
/**
 * @name CookieOptionsArgs
 * @description
 *
 * Object containing default options to pass when setting cookies.
 *
 * The object may have following properties:
 *
 * - **path** - {string} - The cookie will be available only for this path and its
 *   sub-paths. By default, this is the URL that appears in your `<base>` tag.
 * - **domain** - {string} - The cookie will be available only for this domain and
 *   its sub-domains. For security reasons the user agent will not accept the cookie
 *   if the current domain is not a sub-domain of this domain or equal to it.
 * - **expires** - {string|Date} - String of the form "Wdy, DD Mon YYYY HH:MM:SS GMT"
 *   or a Date object indicating the exact date/time this cookie will expire.
 * - **secure** - {boolean} - If `true`, then the cookie will only be available through a
 *   secured connection.
 */
export interface CookieOptionsArgs {
  path?: string;
  domain?: string;
  expires?: string|Date;
  secure?: boolean;
}
