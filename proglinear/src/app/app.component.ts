import { Component, OnInit } from '@angular/core';
import { PlotlyComponent } from './components/plotly/plotly.component';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatInputModule} from '@angular/material/input';
import {MatIconModule} from '@angular/material/icon';
import { SympyServiceService } from './services/sympy-service.service';
import {MatMenuModule} from '@angular/material/menu';
import {MatSnackBar, MatSnackBarModule} from '@angular/material/snack-bar';
import { Calculation } from './models/Calculation';
import { CommonModule } from '@angular/common';
import { ResultsModalService } from './components/results-modal/services/results-modal.service';

@Component({
  selector: 'app-root',
  imports: [PlotlyComponent,ReactiveFormsModule,MatFormFieldModule, MatInputModule, MatIconModule, MatMenuModule, PlotlyComponent,
    MatSnackBarModule,CommonModule
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'proglinear';

  restritionsForm: FormGroup;
  restritions: any[] = [{ id: 0 }, {id: 1}]; 
  xCoef: number[] = [];
  yCoef: number[] = [];
  constCoef: number[] = [];
  op1Coef: string[] = [];
  op2Coef: string[] = [];
  op1Options: string[] = ["+","-"];
  op2Options: string[] = ["==",">","<",">=","<="];

  points: number[][] = [];
  intersections: number[][] = [];
  valuesTested: Calculation[] = [];
  valuesTestedMathematical: Calculation[] = [];

  maxResult: number = -1
  maxResultX: number = -1
  maxResultY: number = -1
  minResult: number = -1
  minResultX: number = -1
  minResultY: number = -1

  isMobile: boolean = false;

  constructor(private fb: FormBuilder, private sympyService: SympyServiceService, private snackBar: MatSnackBar,
    private resultsModalService: ResultsModalService
  ) {
    this.restritionsForm = this.fb.group({
      x_0: 0,
      y_0: 0,
      const_0: 0,
      op1Coef_0: "+",
      op2Coef_0: "+",
      x_1: 0,
      y_1: 0,
      const_1: 0,
      op1Coef_1: "+",
      op2Coef_1: "=",
    });

  }


  addRestrition() {
    const newEqIndex = this.restritions.length;
    
    this.restritions.push({ id: newEqIndex });

    this.restritionsForm.addControl(`x_${newEqIndex}`, this.fb.control(0));
    this.restritionsForm.addControl(`y_${newEqIndex}`, this.fb.control(0));
    this.restritionsForm.addControl(`const_${newEqIndex}`, this.fb.control(0));
    this.restritionsForm.addControl(`op1Coef_${newEqIndex}`, this.fb.control('+'));
    this.restritionsForm.addControl(`op2Coef_${newEqIndex}`, this.fb.control('='));
  }

  removeRestrition(index: number) {

    this.restritions.splice(index, 1);
  
    this.restritionsForm.removeControl(`x_${index}`);
    this.restritionsForm.removeControl(`y_${index}`);
    this.restritionsForm.removeControl(`const_${index}`);
    this.restritionsForm.removeControl(`op1Coef_${index}`);
    this.restritionsForm.removeControl(`op2Coef_${index}`);
  
    this.restritions.forEach((eq, i) => {
      const oldKeyX = `x_${eq.id}`;
      const newKeyX = `x_${i}`;

      const oldKeyY = `y_${eq.id}`;
      const newKeyY = `y_${i}`;

      const oldKeyC = `const_${eq.id}`;
      const newKeyC = `const_${i}`;

      const oldKeyOp1 = `op1Coef_${eq.id}`;
      const newKeyOp1 = `op1Coef_${i}`;

      const oldKeyOp2 = `op2Coef_${eq.id}`;
      const newKeyOp2 = `op2Coef_${i}`;

      if (oldKeyX !== newKeyX) {
        const control = this.restritionsForm.get(oldKeyX);
        if (control) {
          this.restritionsForm.removeControl(oldKeyX);
          this.restritionsForm.addControl(newKeyX, control);
        }
      }

      if (oldKeyY !== newKeyY) {
        const control = this.restritionsForm.get(oldKeyY);
        if (control) {
          this.restritionsForm.removeControl(oldKeyY);
          this.restritionsForm.addControl(newKeyY, control);
        }
      }

      if (oldKeyC !== newKeyC) {
        const control = this.restritionsForm.get(oldKeyC);
        if (control) {
          this.restritionsForm.removeControl(oldKeyC);
          this.restritionsForm.addControl(newKeyC, control);
        }
      }

      if (oldKeyOp1 !== newKeyOp1) {
        const control = this.restritionsForm.get(oldKeyOp1);
        if (control) {
          this.restritionsForm.removeControl(oldKeyOp1);
          this.restritionsForm.addControl(newKeyOp1, control);
        }
      }

      if (oldKeyOp2 !== newKeyOp2) {
        const control = this.restritionsForm.get(oldKeyOp2);
        if (control) {
          this.restritionsForm.removeControl(oldKeyOp2);
          this.restritionsForm.addControl(newKeyOp2, control);
        }
      }

      eq.id = i;
    });
  }

  onSubmit() {
    this.xCoef = [];
    this.yCoef = [];
    this.constCoef = [];
    this.op1Coef = [];
    this.op2Coef = [];

    const filteredX = Object.entries(this.restritionsForm.value)
    .filter(([key, value]) => key.startsWith('x_'))  
    .map(([key, value]) => Number(value));

    this.xCoef.push(...filteredX);

    const filteredY = Object.entries(this.restritionsForm.value)
    .filter(([key, value]) => key.startsWith('y_'))  
    .map(([key, value]) => Number(value));

    this.yCoef.push(...filteredY);

    const filteredC = Object.entries(this.restritionsForm.value)
    .filter(([key, value]) => key.startsWith('const_'))  
    .map(([key, value]) => Number(value));

    this.constCoef.push(...filteredC);

    const filteredOp1 = Object.entries(this.restritionsForm.value)
    .filter(([key, value]) => key.startsWith('op1Coef_'))  
    .map(([key, value]) => String(value));

    this.op1Coef.push(...filteredOp1);

    const filteredOp2 = Object.entries(this.restritionsForm.value)
    .filter(([key, value]) => key.startsWith('op2Coef_'))  
    .map(([key, value]) => String(value));

    this.op2Coef.push(...filteredOp2);


    const equations: string[][] | number[][] = [];

    equations[0] = this.xCoef;
    equations[1] = this.yCoef;
    equations[2] = this.constCoef;
    equations[3] = this.op1Coef;
    equations[4] = this.op2Coef;

    this.sympyService.findPoints(equations).subscribe({
      next: (data) => {

        this.snackBar.open("Processamento realizado com sucesso", "X", {
          duration: 1000,
          verticalPosition: "top",
          panelClass: ["success-snackbar"],
        });

        this.points = data.points;
        this.intersections = data.intersections;
        this.valuesTested = data.valuesTested;
        this.valuesTestedMathematical = data.valuesTestedMathematical;

        this.maxResult = -1;
        this.maxResultX = -1;
        this.maxResultY = -1;

        this.minResult = -1;
        this.minResultX = -1;
        this.minResultY = -1;

        if (data.maxResult !== null) this.maxResult = data.maxResult;
        if (data.maxResultX !== null) this.maxResultX = data.maxResultX;
        if (data.maxResultY !== null) this.maxResultY = data.maxResultY;

        if (data.minResult !== null) this.minResult = data.minResult;
        if (data.minResultX !== null) this.minResultX = data.minResultX;
        if (data.minResultY !== null) this.minResultY = data.minResultY;

      },
      error: () => {
        this.snackBar.open("Erro ao processar. Verifique as variáveis inseridas", "X", {
          duration: 1000,
          verticalPosition: "top",
          panelClass: ["error-snackbar"],
        });
      }
    })
  }
      

  setOp1Coef(index: number, value: string): void {
    this.restritionsForm.get('op1Coef_' + index)?.setValue(value);
  }

  setOp2Coef(index: number, value: string): void {
    this.restritionsForm.get('op2Coef_' + index)?.setValue(value);
  }

  openResultsModal() {
    this.resultsModalService.openDialog(this.valuesTested,true);
  }

  openResultsModalMathematical() {
    this.resultsModalService.openDialog(this.valuesTestedMathematical,false);
  }
}
