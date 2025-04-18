import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';  
import { Observable } from 'rxjs';  
import { environment } from '../../environments/environment.development';

@Injectable({
  providedIn: 'root'
})
export class SympyServiceService {

  constructor(private http: HttpClient) { }

  findPoints(equacoes: string[][] | number[][]): Observable<any> {
    
    const payload = { equacoes };  
    
    const findPointsUrl = new URL(environment.findPointsUrl, environment.baseUrl).toString();
    
    return this.http.post(findPointsUrl, payload); 
  }
}
