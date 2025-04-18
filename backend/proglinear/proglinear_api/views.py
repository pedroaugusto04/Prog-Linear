import sys

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from sympy import symbols, Eq, solve, Matrix


@api_view(['POST'])
def findPoints(request):
    equacoes_str = request.data.get("equacoes", [])

    num_colunas = len(equacoes_str[0])

    # associa cada indice aos valores da eq correspondente
    equacoes_map = {i: [] for i in range(num_colunas)}

    for linha in equacoes_str:
        for i, valor in enumerate(linha):
            equacoes_map[i].append(valor)


    # aplica o sinal da operacao

    for i in equacoes_map.keys():
        lista = equacoes_map[i]
        for index,valor in enumerate(lista[1:]):
            indexOp = index + int((len(lista)) / 2) + 1
            if indexOp >= len(lista):  break
            valorOp = lista[indexOp]
            if valorOp == '-':
                lista[index+1] = -valor

    points = []
    intersections = []
    equations = []

    # verifica 2 pontos para cada equacao

    for i in equacoes_map.keys():
        lista = equacoes_map[i]

        x, y = symbols('x y')

        A = Matrix([[lista[0],lista[1]]])
        b = Matrix([lista[2]])

        solution = solve(A * Matrix([x, y]) - b, (x, y))


        if i != 0:
            for var in solution:
                equations.append(Eq(var, solution[var]))

        if lista[0] != 0: # x != 0
            x_expr = solution[x]
            y1 = -100 # first point
            y2 = 100 # second point

            x1 = float(x_expr.subs(y, y1))
            x2 = float(x_expr.subs(y,y2))
            points.append([x1, y1, x2, y2])
        else:
            y_expr = solution[y]
            x1 = -100  # first point
            x2 = 100 # second point

            y1 = float(y_expr.subs(x,x1))
            y2 = float(y_expr.subs(x, x2))
            points.append([x1, y1, x2, y2])

    for i in range(len(equations)):
        for j in range(i + 1, len(equations)):
            sol = solve((equations[i], equations[j]), (x, y))

            if sol:
                intersections.append([float(sol[x]), float(sol[y])])

    response_data = {
        'points': points,
        'intersections': intersections
    }

    return JsonResponse(response_data, safe=False)