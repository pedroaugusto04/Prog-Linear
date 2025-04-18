import sys

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from sympy import symbols, Eq, solve, Matrix,Le,Ge,Lt,Gt

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


    # monta o sistema de  inequacoes para verificacao das intersecoes
    for i in equacoes_map.keys():
        if i == 0: continue # nao processa a primeira ( a primeira eh o que queremos maximizar )

        lista = equacoes_map[i]

        x,y = symbols('x y')

        op1 = lista[3]

        resultX = lista[0] * x
        resultY = lista[1] * y

        if op1 == "-":
            resultY *= -1

        lhs = resultX + resultY
        rhs = lista[2]

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
                intersections.append([float(sol[x]), float(sol[y]),True])


    # verifica quais intersecoes sao validas ( respeitam as inequacoes e quais nao )
    for inequation in inequations:
        for intersection in intersections:
            value = {x: intersection[0],y: intersection[1]}

            valid = inequation.subs(value)

            if not valid:
                intersection[2] = False


    # recupera funcao que o usuario deseja otimizar
    listaFuncaoOtimiza = equacoes_map[0]
    x,y = symbols("x y")

    resultX = listaFuncaoOtimiza[0] * x
    resultY = listaFuncaoOtimiza [1] * y
    resultZ = listaFuncaoOtimiza [2]
    op1 = listaFuncaoOtimiza [3]
    op2 = listaFuncaoOtimiza [4]

    if op1 == "-":
        resultY *= -1

    if op2 == "-":
        resultZ *= -1

    funcaoOtimiza = resultX + resultY + resultZ
    maxResult = -sys.maxsize
    maxResultX = -sys.maxsize
    maxResultY = -sys.maxsize

    minResult = sys.maxsize
    minResultX = -sys.maxsize
    minResultY = -sys.maxsize


    for intersection in intersections:
        if not intersection[2]: continue
        result = funcaoOtimiza.subs({x: intersection[0], y: intersection[1]})

        if result > maxResult:
            maxResult = result
            maxResultX = intersection[0]
            maxResultY = intersection[1]
        if result < minResult:
            minResult = result
            minResultX = intersection[0]
            minResultY = intersection[1]

    response_data = {
        'points': points,
        'intersections': intersections,
        'maxResult': float(maxResult) if maxResult != sys.maxsize and maxResult != -sys.maxsize else None,
        'maxResultX': float(maxResultX) if maxResultX != sys.maxsize and maxResultX != -sys.maxsize else None,
        'maxResultY': float(maxResultY) if maxResultY != sys.maxsize and maxResultY != -sys.maxsize else None,
        'minResult': float(minResult) if minResult != sys.maxsize and minResult != -sys.maxsize else None,
        'minResultX': float(minResultX) if minResultX != sys.maxsize and minResultX != -sys.maxsize else None,
        'minResultY': float(minResultY) if minResultY != sys.maxsize and minResultY != -sys.maxsize else None
    }

    return JsonResponse(response_data, safe=False)