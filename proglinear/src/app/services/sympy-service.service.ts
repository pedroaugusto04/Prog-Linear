import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';  
import { Observable } from 'rxjs';  

@Injectable({
  providedIn: 'root'
})
export class SympyServiceService {

  private apiUrl = 'http://localhost:8000/api/findPoints/'; 

  constructor(private http: HttpClient) { }

  findPoints(equacoes: string[][] | number[][]): Observable<any> {
    
    const payload = { equacoes };  
    
    return this.http.post(this.apiUrl, payload); 
  }
}
