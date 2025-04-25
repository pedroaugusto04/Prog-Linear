import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
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
import { Restriction } from './models/Restriction';
import {MatTooltipModule} from '@angular/material/tooltip';

@Component({
  selector: 'app-root',
  imports: [PlotlyComponent,ReactiveFormsModule,MatFormFieldModule, MatInputModule, MatIconModule, MatMenuModule, PlotlyComponent,
    MatSnackBarModule,CommonModule,MatTooltipModule
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'proglinear';

  restrictionsForm: FormGroup;
  restrictions: Restriction[] = [];

  varCoef: number[][] = [];
  constCoef: number[][] = [];
  opCoef: string[][] = [];
  op1Options: string[] = ["+","-"];
  op2Options: string[] = ["==",">","<",">=","<="];

  points: number[][] = [];
  intersections: number[][] = [];
  axisRange: any;
  valuesTested: Calculation[] = [];

  maxResult: number = -1
  maxResultX: number = -1
  maxResultY: number = -1
  minResult: number = -1
  minResultX: number = -1
  minResultY: number = -1

  isMobile: boolean = false;

  constructor(private fb: FormBuilder, private sympyService: SympyServiceService, private snackBar: MatSnackBar,
    private resultsModalService: ResultsModalService,private cdRef: ChangeDetectorRef
  ) {
    this.restrictionsForm = this.fb.group({
      x1_0: 0,
      x2_0: 0,
      const_0: 0,
      op1Coef_0: "+",
      op2Coef_0: "+",
      x1_1: 0,
      x2_1: 0,
      const_1: 0,
      op1Coef_1: "+",
      op2Coef_1: "=",
    });

    const restriction1: Restriction = {
      id: 0,
      variables: [0,0], 
      constant: 0,
      coefficients: ["+","+"] 
    };

    const restriction2: Restriction = {
      id: 1,
      variables: [0,0], 
      constant: 0,
      coefficients: ["+","="] 
    };

    this.restrictions.push(restriction1);

    this.restrictions.push(restriction2);

  }


  addRestriction() {
    const newEqIndex = this.restrictions.length;

    const restriction: Restriction = {
      id: this.restrictions[this.restrictions.length - 1].id + 1,
      variables: [0,0], 
      constant: 0,
      coefficients: ["+","="] 
    };
    
    this.restrictions.push(restriction);

    this.restrictionsForm.addControl(`x1_${newEqIndex}`, this.fb.control(0));
    this.restrictionsForm.addControl(`x2_${newEqIndex}`, this.fb.control(0));
    this.restrictionsForm.addControl(`const_${newEqIndex}`, this.fb.control(0));
    this.restrictionsForm.addControl(`op1Coef_${newEqIndex}`, this.fb.control('+'));
    this.restrictionsForm.addControl(`op2Coef_${newEqIndex}`, this.fb.control('='));
  }

  removeRestriction(index: number) {

    this.restrictions.splice(index, 1);
  
    this.restrictionsForm.removeControl(`x1_${index}`);
    this.restrictionsForm.removeControl(`x2_${index}`);
    this.restrictionsForm.removeControl(`const_${index}`);
    this.restrictionsForm.removeControl(`op1Coef_${index}`);
    this.restrictionsForm.removeControl(`op2Coef_${index}`);
  
    this.restrictions.forEach((eq, i) => {
      const oldKeyX = `x1_${eq.id}`;
      const newKeyX = `x1_${i}`;

      const oldKeyY = `x2_${eq.id}`;
      const newKeyY = `x2_${i}`;

      const oldKeyC = `const_${eq.id}`;
      const newKeyC = `const_${i}`;

      const oldKeyOp1 = `op1Coef_${eq.id}`;
      const newKeyOp1 = `op1Coef_${i}`;

      const oldKeyOp2 = `op2Coef_${eq.id}`;
      const newKeyOp2 = `op2Coef_${i}`;

      if (oldKeyX !== newKeyX) {
        const control = this.restrictionsForm.get(oldKeyX);
        if (control) {
          this.restrictionsForm.removeControl(oldKeyX);
          this.restrictionsForm.addControl(newKeyX, control);
        }
      }

      if (oldKeyY !== newKeyY) {
        const control = this.restrictionsForm.get(oldKeyY);
        if (control) {
          this.restrictionsForm.removeControl(oldKeyY);
          this.restrictionsForm.addControl(newKeyY, control);
        }
      }

      if (oldKeyC !== newKeyC) {
        const control = this.restrictionsForm.get(oldKeyC);
        if (control) {
          this.restrictionsForm.removeControl(oldKeyC);
          this.restrictionsForm.addControl(newKeyC, control);
        }
      }

      if (oldKeyOp1 !== newKeyOp1) {
        const control = this.restrictionsForm.get(oldKeyOp1);
        if (control) {
          this.restrictionsForm.removeControl(oldKeyOp1);
          this.restrictionsForm.addControl(newKeyOp1, control);
        }
      }

      if (oldKeyOp2 !== newKeyOp2) {
        const control = this.restrictionsForm.get(oldKeyOp2);
        if (control) {
          this.restrictionsForm.removeControl(oldKeyOp2);
          this.restrictionsForm.addControl(newKeyOp2, control);
        }
      }

      eq.id = i;
    });
  }

  onSubmit() {
    this.varCoef = [];
    this.constCoef = [];
    this.opCoef = [];

    this.constCoef[0] = [];
    this.opCoef[0] = [];

    const filteredX = Object.entries(this.restrictionsForm.value)
    .filter(([key, value]) => key.startsWith('x') && /\d+/.test(key))
    .map(([key, value]) => ({ key, value: Number(value) }))
    .sort((a, b) => {
      const opA = parseInt(a.key.match(/op(\d+)/)?.[1] || '0');
      const opB = parseInt(b.key.match(/op(\d+)/)?.[1] || '0');
      return opA - opB;
    });


    filteredX.forEach(({ key, value }) => {

    const coefIndex = parseInt(key.match(/\d+/)?.[0] || '0') - 1;  

    if (!this.varCoef[coefIndex]) {
      this.varCoef[coefIndex] = [];
    }

    this.varCoef[coefIndex].push(value);
    });

    const filteredC = Object.entries(this.restrictionsForm.value)
    .filter(([key, value]) => key.startsWith('const_'))  
    .map(([key, value]) => Number(value));

    this.constCoef[0].push(...filteredC);

    const filteredOp = Object.entries(this.restrictionsForm.value)
    .filter(([key, value]) => key.startsWith('op') && /\d+/.test(key))  
    .map(([key, value]) => ({ key, value: String(value) }));

    filteredOp.forEach(({ key, value }) => {

      const coefIndex = parseInt(key.match(/_(\d+)/)?.[1] || '0');  

      if (!this.opCoef[coefIndex]) {
        this.opCoef[coefIndex] = [];
      }

      this.opCoef[coefIndex].push(value);
    });


    const equations: number[][][] | string[][][] = [];

    equations[0] = this.varCoef;
    equations[1] = this.constCoef;
    equations[2] = this.opCoef;

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
        this.axisRange = data.axisRange;

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

  addNewVariableToRestriction(index: number) {

    let count = this.restrictions[index].variables.length + 1;

    this.restrictionsForm.addControl(`x${count}_${index}`, this.fb.control(0));
    
    const currentStr: string = this.restrictionsForm.get(`op${count-1}Coef_${index}`)?.value;

    this.restrictionsForm.removeControl(`op${count-1}Coef_${index}`);

    this.restrictionsForm.addControl(`op${count-1}Coef_${index}`,this.fb.control("+"));

    this.restrictionsForm.addControl(`op${count}Coef_${index}`,this.fb.control(currentStr));

    this.restrictions[index].variables.push(0);

    this.restrictions[index].coefficients.splice(this.restrictions[index].coefficients.length - 1, 0, "+");
  }

  removeRestrictionVariable(index: number){
    const count = this.restrictions[index].variables.length;

    this.restrictionsForm.removeControl(`x${count}_${index}`);

    this.restrictionsForm.removeControl(`op${count-1}_${index}`);

    this.restrictions[index].variables.pop();

    this.restrictions[index].coefficients.splice(this.restrictions[index].coefficients.length -2,1);
  }
      

  setOpCoef(index: number, indexJ: number, value: string): void {
    indexJ++;
    this.restrictionsForm.get(`op${indexJ}Coef_` + index)?.setValue(value);
  }

  openResultsModal() {
    this.resultsModalService.openDialog(this.valuesTested);
  }
}
