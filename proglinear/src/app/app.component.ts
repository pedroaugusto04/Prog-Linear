import { Component } from '@angular/core';
import { PlotlyComponent } from './components/plotly/plotly.component';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatInputModule} from '@angular/material/input';
import {MatIconModule} from '@angular/material/icon';
import * as Math from 'mathjs';
import { SympyServiceService } from './services/sympy-service.service';

@Component({
  selector: 'app-root',
  imports: [PlotlyComponent,ReactiveFormsModule,MatFormFieldModule, MatInputModule, MatIconModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'proglinear';

  restritionsForm: FormGroup;
  restritions: any[] = [{ id: 1 }]; 
  points: { x: number; y: number }[][] = [];

  constructor(private fb: FormBuilder, private sympyService: SympyServiceService) {
    this.restritionsForm = this.fb.group({
      restrition_0: ""
    });
  }

  addRestrition() {
    const newEqIndex = this.restritions.length;
    this.restritions.push({ id: newEqIndex });

    this.restritionsForm.addControl(`restrition_${newEqIndex}`, this.fb.control(''));
  }

  removeRestrition(index: number) {
    this.restritions.splice(index, 1);
  
    this.restritionsForm.removeControl(`restrition_${index}`);
  
    this.restritions.forEach((eq, i) => {
      const oldKey = `restrition_${eq.id}`;
      const newKey = `restrition_${i}`;
  
      if (oldKey !== newKey) {
        const control = this.restritionsForm.get(oldKey);
        if (control) {
          this.restritionsForm.removeControl(oldKey);
          this.restritionsForm.addControl(newKey, control);
        }
      }
  
      eq.id = i;
    });
  }

  onSubmit() {
    const equations: string[] = [];

    Object.keys(this.restritionsForm.controls).forEach((key) => {
      const control = this.restritionsForm.get(key);  
      if (control && control.value) {
        let equation: string = control.value;

        equation = this.replaceInequation(equation);

        equations.push(equation);
      }
    });

    this.sympyService.solveEquations(equations).subscribe({
      next:(data) => {
        if (data.respostas) {

          this.points = []; 

          data.respostas.forEach((resposta: string) => {
            try {
              const jsonPart = resposta
                .replace('Pontos: ', '')
                .replace(/'/g, '"') 
                .replace(/\b(\w+)\b(?=\s*:)/g, '"$1"');

              const parsed = JSON.parse(jsonPart);

              this.points.push(...parsed);

            } catch (e) {
              console.error('Erro ao converter resposta:', resposta, e);
            }
          });
        }
      },
    })

  }

  replaceInequation(equation: string): string {
    equation = equation.replace(">=", "=");
    equation = equation.replace("<=", "=");
    equation = equation.replace(">", "=");
    equation = equation.replace("<", "=");
    equation = equation.replace("==", "=");

    // mantem no maximo dois iguais em sequencia
    equation = equation.replace(/={2,}/g, "=");
    
    return equation;
  }
}
