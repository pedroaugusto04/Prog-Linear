import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';  
import { Observable } from 'rxjs';  

@Injectable({
  providedIn: 'root'
})
export class SympyServiceService {

  private apiUrl = 'http://localhost:8000/api/solvelinearequation/'; 

  constructor(private http: HttpClient) { }

  solveEquations(equacoes: string[]): Observable<any> {
    const payload = { equacoes };  
    return this.http.post(this.apiUrl, payload); 
  }
}
