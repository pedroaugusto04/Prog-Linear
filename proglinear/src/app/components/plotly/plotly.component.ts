import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { PlotlyModule } from 'angular-plotly.js';
import * as PlotlyJS from 'plotly.js-dist-min';

PlotlyModule.plotlyjs = PlotlyJS;

@Component({
  selector: 'app-plotly',
  standalone: true,
  imports: [PlotlyModule, CommonModule],
  templateUrl: './plotly.component.html',
  styleUrl: './plotly.component.scss'
})
export class PlotlyComponent implements OnChanges {
  @Input() points: { x: number; y: number }[] = [];

  public graph: { data: { x: number[], y: number[], mode: string }[]; layout: any } = {
    data: [],
    layout: {
      width: 600,
      height: 600,
      title: { text: 'Resultados: Método Gráfico' },
      xaxis: { title: 'x' },
      yaxis: { title: 'y' }
    }
  };

  ngOnChanges(changes: SimpleChanges) {
    if (changes['points']) {
      this.gerarTracos();
    }
  }

  gerarTracos() {
    this.graph.data = [];
  
    for (let i = 0; i < this.points.length - 1; i += 2) {
      const point1 = this.points[i];    
      const point2 = this.points[i + 1]; 
  
      const point1Values = Object.values(point1); 
      const point2Values = Object.values(point2); 
  
      const trace = {
        x: [point1Values[0], point2Values[0]],  
        y: [point1Values[1], point2Values[1]],  
        mode: 'lines',
      };
      this.graph.data.push(trace);
    }
  

    this.graph.data = this.graph.data.filter(trace => Object.keys(trace).length > 0);
  }
}
