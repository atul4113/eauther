// import { Injectable } from '@angular/core';
// import { HttpClient } from '@angular/common/http';
// import { Observable } from 'rxjs';
//
// @Injectable({
//   providedIn: 'root', // This allows the service to be used throughout the application
// })
// export class UserService {
//   private apiUrl = 'http://127.0.0.1:8000/api/v2/user/';
//
//   constructor(private http: HttpClient) {}
//
//   getUser(): Observable<any> {
//     return this.http.get(this.apiUrl, {
//       withCredentials: true,  // This is important to include session cookies
//     });
//   }
// }
