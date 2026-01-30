import matplotlib.pyplot as plt

def plot_circulo(comprimento_pista,diametro,quantidade):

    distancia = (comprimento_pista-(diametro*quantidade))/(quantidade-1)

    raio = diametro / 2
    passo = diametro + distancia

    centros_x = []
    x = raio
    centros_x2 = []
    valor_atual=comprimento_pista-raio 

    while valor_atual >= x:
        centros_x2.append(valor_atual)
        valor_atual -= passo
        if valor_atual < x:
            break
        centros_x.append(x)
        x += passo 

    for x in reversed(centros_x2):
        centros_x.append(x)
    
    fig, ax = plt.subplots(figsize=(12, 4))

    for cx in centros_x:
        circulo = plt.Circle((cx, 0), raio, color='red', alpha=0.6)
        ax.add_patch(circulo)


    for i in range(len(centros_x) - 1):
        x1 = centros_x[i] + raio
        x2 = centros_x[i + 1] - raio

        ax.plot([x1, x2], [0, 0], color='black', linestyle='-')
        ax.plot([x1, x1], [-1, 1], color='black', linestyle='-')
        ax.plot([x2, x2], [-1, 1], color='black', linestyle='-')

        xm = (x1 + x2) / 2
        ax.text(xm, 0.5, f'{centros_x[i+1] - centros_x[i] - diametro:.2f}', ha='center', va='bottom', fontsize=10)

        x3=centros_x[i]-raio
        x4=centros_x[i]+raio
        ax.plot([x3, x3], [diametro-1, diametro+1], color='black', linestyle="-")
        ax.plot([x4, x4], [diametro-1, diametro+1], color='black', linestyle="-")
        ax.plot([x3, x4], [diametro, diametro], color='black', linestyle="-")
        xm = (x3 + x4) / 2
        ax.text(xm, diametro+1, f'{diametro}', ha='center', va='bottom', fontsize=10)

    x3=centros_x[-1]-raio
    x4=centros_x[-1]+raio
    ax.plot([x3, x4], [diametro, diametro], color='black', linestyle="-")
    ax.plot([x3, x3], [diametro-1, diametro+1], color='black', linestyle="-")
    ax.plot([x4, x4], [diametro-1, diametro+1], color='black', linestyle="-")
    xm = (x3 + x4) / 2
    ax.text(xm, diametro+1, f'{diametro}', ha='center', va='bottom', fontsize=10)

    ax.plot([0, comprimento_pista], [-diametro-2, -diametro-2], color='black', linestyle='-')
    ax.plot([0, 0], [-diametro-3, -diametro-1], color='black', linestyle='-')
    ax.plot([comprimento_pista, comprimento_pista], [-diametro-3, -diametro-1], color='black', linestyle='-')
    xm = comprimento_pista / 2
    ax.text(xm, -diametro-3, f'{comprimento_pista}', ha='center', va='top', fontsize=10)

    ax.set_aspect('equal')
    ax.set_xlim(-10, comprimento_pista+10)
    ax.set_ylim(-diametro-10, diametro+10)
    ax.relim()
    ax.autoscale_view()

    if centros_x[-1] + raio < comprimento_pista:
        ax.plot([centros_x[-1] + raio, centros_x[-1] + raio], [-1, 1], color='black', linestyle='-')
        ax.plot([centros_x[-1] + raio, comprimento_pista], [0, 0], color='black', linestyle='-')
        ax.plot([comprimento_pista, comprimento_pista], [-1, 1], color='black', linestyle='-')
        ax.text((centros_x[-1] + raio + comprimento_pista) / 2, 0.5, f'{comprimento_pista - (centros_x[-1] + raio)}', ha='center', va='bottom', fontsize=10)

    plt.show()

def plot_quadrado(comprimento_pista, altura, esp, quantidade):
    distancia = (altura * quantidade) + (esp * (quantidade - 1))
    y_positions = []
    y = 0
    while y + altura <= distancia:
        y_positions.append(y)
        y += altura + esp

    fig, ax = plt.subplots(figsize=(6, 10))

    for y in y_positions:
        rect = plt.Rectangle(
            (0, y),
            comprimento_pista,
            altura,
            color='#DEB887',
            alpha=0.6
        )
        ax.add_patch(rect)

    x_esp = comprimento_pista + 5
    for i in range(len(y_positions) - 1):
        y1 = y_positions[i] + altura
        y2 = y_positions[i + 1]

        ax.plot([x_esp, x_esp], [y1, y2], color='black')
        ax.plot([x_esp - 1, x_esp + 1], [y1, y1], color='black')
        ax.plot([x_esp - 1, x_esp + 1], [y2, y2], color='black')

        ax.text(
            x_esp + 2,
            (y1 + y2) / 2,
            f'{esp}',
            va='center',
            ha='left'
        )

    x_alt = comprimento_pista + 5
    for y in y_positions:
        y1 = y
        y2 = y + altura

        ax.plot([x_alt, x_alt], [y1, y2], color='black')
        ax.plot([x_alt - 1, x_alt + 1], [y1, y1], color='black')
        ax.plot([x_alt - 1, x_alt + 1], [y2, y2], color='black')

        ax.text(
            x_alt + 2,
            (y1 + y2) / 2,
            f'{altura}',
            va='center',
            ha='left'
        )

    ax.plot([0, comprimento_pista], [-5, -5], color='black')
    ax.plot([0, 0], [-6, -4], color='black')
    ax.plot([comprimento_pista, comprimento_pista], [-6, -4], color='black')
    ax.text(
        comprimento_pista / 2,
        -7,
        f'{comprimento_pista}',
        ha='center',
        va='top'
    )

    x_dist = -10
    ax.plot([x_dist, x_dist], [0, distancia], color='black')
    ax.plot([x_dist - 1, x_dist + 1], [0, 0], color='black')
    ax.plot([x_dist - 1, x_dist + 1], [distancia, distancia], color='black')
    ax.text(
        x_dist - 2,
        distancia / 2,
        f'{distancia}',
        rotation=90,
        va='center',
        ha='right'
    )

    ax.set_aspect('equal')
    ax.set_xlim(-20, comprimento_pista + 20)
    ax.set_ylim(-10, distancia + 10)
    ax.axis('off')

    plt.show()


# plot_circulo(
#     comprimento_pista=900, 
#     diametro=30,
#     quantidade=10
# )

plot_quadrado(
    comprimento_pista=100,
    altura=10,
    esp=2,
    quantidade=8
)