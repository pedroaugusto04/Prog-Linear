import os
import sys

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from sympy import symbols, Eq, solve, Matrix,Le,Ge,Lt,Gt,oo
from dotenv import load_dotenv
from pathlib import Path


if os.getenv("ENV") != "production":
    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')

@api_view(['GET'])
def ping(request):
    return Response("API Online")

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
    inequations = []
    valuesTested = []

    # monta o sistema de  inequacoes para verificacao das intersecoes
    for i in equacoes_map.keys():
        if i == 0: continue # nao processa a primeira ( a primeira eh o que queremos maximizar )

        lista = equacoes_map[i]

        vars = symbols(f'x1:{len(lista)-2}')

        lhs = 0
        for index,var in enumerate(vars):
            lhs += lista[index] * var

        rhs = lista[len(lista)-3]

        op2 = lista[4]

        if op2 == '=':
            inequations.append(Eq(lhs, rhs))
        elif op2 == '<=':
            inequations.append(Le(lhs, rhs))
        elif op2 == '>=':
            inequations.append(Ge(lhs, rhs))
        elif op2 == '<':
            inequations.append(Lt(lhs, rhs))
        elif op2 == '>':
            inequations.append(Gt(lhs, rhs))

    # verifica 2 pontos para cada equacao ( no caso de ate 2 variaveis )

    for i in equacoes_map.keys():
        lista = equacoes_map[i]

        x1, x2 = symbols('x1 x2')

        A = Matrix([[lista[0],lista[1]]])
        b = Matrix([lista[2]])

        solution = solve(A * Matrix([x1, x2]) - b, (x1, x2))


        if i != 0:
            for var in solution:
                equations.append(Eq(var, solution[var]))

        if lista[0] != 0: # x != 0
            if not solution: continue

            x_expr = solution[x1]
            y1v = float(os.getenv("MIN_VAR", "-100")) # first point
            y2v = float(os.getenv("MAX_VAR", "100")) # second point

            x1v = float(x_expr.subs(x2, y1v))
            x2v = float(x_expr.subs(x2,y2v))
            points.append([x1v, y1v, x2v, y2v])
        else:
            if not solution: continue

            y_expr = solution[x2]
            x1v = float(os.getenv("MIN_VAR", "-100")) # first point
            x2v = float(os.getenv("MAX_VAR", "100")) # second point

            y1v = float(y_expr.subs(x1,x1v))
            y2v = float(y_expr.subs(x1, x2v))
            points.append([x1v, y1v, x2v, y2v])

    for i in range(len(equations)):
        for j in range(i + 1, len(equations)):
            if equations[i] == equations[j]: continue
            sol = solve((equations[i], equations[j]), (x1, x2))
            if sol:
                intersections.append([float(sol[x1]), float(sol[x2]),True])


    # verifica quais intersecoes sao validas ( respeitam as inequacoes e quais nao )
    for inequation in inequations:
        for intersection in intersections:
            value = {x1: intersection[0],x2: intersection[1]}

            valid = inequation.subs(value)

            if not valid:
                intersection[2] = False


    # recupera funcao que o usuario deseja otimizar
    listaFuncaoOtimiza = equacoes_map[0]

    vars = symbols(f'x1:{len(listaFuncaoOtimiza)-2}')

    funcaoOtimiza = 0

    for index,var in enumerate(vars):
        funcaoOtimiza += listaFuncaoOtimiza[index] * var

    maxResult = -sys.maxsize
    maxResultX = -sys.maxsize
    maxResultY = -sys.maxsize

    minResult = sys.maxsize
    minResultX = -sys.maxsize
    minResultY = -sys.maxsize

    minAxisX = sys.maxsize
    maxAxisX = -sys.maxsize

    minAxisY = sys.maxsize
    maxAxisY = -sys.maxsize


    # percorre as intersecoes ( metodo grafico )
    for intersection in intersections:
        result = funcaoOtimiza.subs({x1: intersection[0], x2: intersection[1]})

        if not intersection[2]:
            valuesTested.append({'x': float(intersection[0]), 'y': float(intersection[1]), 'result': float(result), 'isValid': False})
            continue

        minAxisX = min(minAxisX,float(intersection[0]))
        maxAxisX = max(maxAxisX, float(intersection[0]))

        minAxisY = min(minAxisY, float(intersection[1]))
        maxAxisY = max(maxAxisY, float(intersection[1]))


        if result > maxResult:
            maxResult = result
            maxResultX = intersection[0]
            maxResultY = intersection[1]
        if result < minResult:
            minResult = result
            minResultX = intersection[0]
            minResultY = intersection[1]

        valuesTested.append({'x': float(intersection[0]), 'y': float(intersection[1]), 'result': float(result), 'isValid': True})

    axisRange = {
        'minX': float(os.getenv("DEFAULT_MIN_RANGE", "-100")) if minAxisX == sys.maxsize or minAxisX == -sys.maxsize else minAxisX,
        'maxX': float(os.getenv("DEFAULT_MAX_RANGE", "100")) if maxAxisX == sys.maxsize or maxAxisX == -sys.maxsize else maxAxisX,
        'minY': float(os.getenv("DEFAULT_MIN_RANGE", "-100")) if minAxisY == sys.maxsize or minAxisY == -sys.maxsize else minAxisY,
        'maxY': float(os.getenv("DEFAULT_MAX_RANGE", "100")) if maxAxisY == sys.maxsize or maxAxisY == -sys.maxsize else maxAxisY,
    }

    response_data = {
        'points': points,
        'intersections': intersections,
        'valuesTested': valuesTested,
        'maxResult': float(maxResult) if maxResult != -sys.maxsize else None,
        'maxResultX': float(maxResultX)  if maxResultX != -sys.maxsize else None,
        'maxResultY': float(maxResultY) if maxResultY != -sys.maxsize else None,
        'minResult': float(minResult) if minResult != sys.maxsize and minResult != -sys.maxsize else None,
        'minResultX': float(minResultX) if minResultX != sys.maxsize and minResultX != -sys.maxsize else None,
        'minResultY': float(minResultY) if minResultY != sys.maxsize and minResultY != -sys.maxsize else None,
        'axisRange': axisRange
    }

    return JsonResponse(response_data, safe=False)