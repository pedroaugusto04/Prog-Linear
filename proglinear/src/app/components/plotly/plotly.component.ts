import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { PlotlyModule } from 'angular-plotly.js';
import { number } from 'mathjs';
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
  
  @Input() points: number[][] = [];
  @Input() intersections: number[][] = [];

  public graph: { data: { x: number[], y: number[], mode: string }[]; layout: any } = {
    data: [],
    layout: {
      width: 1000,
      height: 600,
      title: { text: 'Resultados: Método Gráfico' },
      xaxis: {
        title: 'x',
        autorange: true
      },
      yaxis: {
        title: 'y',
        autorange: true
      },
    }
  };

  ngOnChanges(changes: SimpleChanges) {

    this.graph.data = [];

    if (changes['points']) {
      this.gerarTracos();
    }

    if (changes['intersections']) {
      this.gerarIntersecoes();
    }
  }

  gerarTracos() {

    // o primeiro conjunto de pontos eh da equacao a ser maximizada, nao deve colocar no grafico 

    for (let i = 1; i < this.points.length; i ++) {

      const [x0, y0, x1, y1] = this.points[i];

      const trace = {
        x: [x0,x1],  
        y: [y0,y1],  
        mode: 'lines',
        name: `Reta ${i}`,
      };

      this.graph.data.push(trace);
    }
  

    this.graph.data = this.graph.data.filter(trace => Object.keys(trace).length > 0);
  }

  gerarIntersecoes() {

    for (let i = 0; i < this.intersections.length; i++) {
        const [x, y] = this.intersections[i];
        
        const trace = {
            x: [x],  
            y: [y],  
            mode: 'markers',  
            type: 'scatter', 
            name: `Interseção ${i+1}`,
            marker: {
                color: 'blue', 
                size: 8       
            }
        };

        this.graph.data.push(trace);
    }

    this.graph.data = this.graph.data.filter(trace => Object.keys(trace).length > 0);
  }
  
}
