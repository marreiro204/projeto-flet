import flet as ft
import requests
import matplotlib.pyplot as plt  
import matplotlib
import io
import base64
import os

matplotlib.use("Agg")

API_URL = "https://api-vercel2.vercel.app/api/jogadores"  # coloque sua URL  aqui

port = int(os.environ.get("PORT", 8550))

def main(page: ft.Page):
    page.title = "Análise de jogadores - Brasileirão 2024"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    page.scroll = "auto"

    # Buscar dados da API
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        jogadores_data = data
    else:
        jogadores_data = data

    # lista dos nomes dos jogadores
    nomes_jogadores = [j["nome"] for j in jogadores_data]

    # imagem do jogador (inicial)
    imagem_jogador = ft.Image( 
        src="https://via.placeholder.com/200x300",
        width=200,
        height=300,
        fit=ft.ImageFit.CONTAIN
    )

    # título
    titulo = ft.Text(
        "📊 Estatísticas dos Jogadores - Brasileirão 2024",
        size=26,
        weight=ft.FontWeight.BOLD,
        text_align="center"
    )
    
    dropdown = ft.Dropdown(
        label="selecione um jogador",
        options=[ft.dropdown.Option(nome) for nome in nomes_jogadores],
        width=300
    )

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Jogador")),
            ft.DataColumn(ft.Text("Gols")),
            ft.DataColumn(ft.Text("Assistências")),
            ft.DataColumn(ft.Text("Partidas"))
        ],
        rows=[],
        heading_row_color=ft.Colors.BLUE_100
    )

    estatisticas_texto = ft.Text(
        value="",
        size=16,
        weight=ft.FontWeight.W_500,
        text_align="center"
    )

    grafico_imagem = ft.Image(
        src="https://via.placeholder.com/400x300", 
        width=400,
        height=300,
        fit=ft.ImageFit.CONTAIN
    )

    def atualizar_tabela(e):
        jogador = dropdown.value
        table.rows.clear()

        if jogador:
            # buscar dados do jogador selecionado
            linha = next((j for j in jogadores_data if j["nome"] == jogador), None)

            if linha:
                table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(linha["nome"])),
                        ft.DataCell(ft.Text(str(linha["gols"]))),
                        ft.DataCell(ft.Text(str(linha["assistencias"]))),
                        ft.DataCell(ft.Text(str(linha["partidas"]))),
                    ])
                )

                gols = linha["gols"]
                assist = linha["assistencias"]
                partidas = linha["partidas"]
                media_gols = gols / partidas if partidas else 0
                media_assist = assist / partidas if partidas else 0
                participacao = (gols + assist) / partidas if partidas else 0

                estatisticas_texto.value = (
                    f"Média de gols {media_gols:.2f} | "
                    f"Média de Assistências: {media_assist:.2f} | "
                    f"Participação em gols por jogo: {participacao:.2f} |"
                )

                categorias = ["Gols", "Assistências", "Partidas"]
                valores = [gols, assist, partidas]

                fig, ax = plt.subplots()
                ax.bar(categorias, valores, color=["blue", "green", "orange"])
                ax.set_title(f"Desempenho de {linha['nome']}")
                ax.set_ylabel("Quantidade")

                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                plt.close(fig)
                buffer.seek(0)

                imagem_base64 = base64.b64encode(buffer.read()).decode()
                grafico_imagem.src_base64 = imagem_base64

                # Imagem do jogador (usa URL absoluto se possível)
                # Sua API tem "imagem": "imagens/hulk.png"
                # Então, monte a URL completa para a imagem na internet,
                # ou altere o campo para ter URL completa
                # Exemplo simples:
                imagem_jogador.src = f"https://api-vercel2.vercel.app/{linha['imagem']}"

            else:
                estatisticas_texto.value = "Jogador não encontrado."

        else:
            estatisticas_texto.value = "Por favor, selecione um jogador para ver os dados."

        page.update()

    dropdown.on_change = atualizar_tabela

    page.controls.append(
        ft.Column(
            [
                titulo,
                ft.Container(dropdown, alignment=ft.alignment.center),
                ft.Container(table, margin=10),
                estatisticas_texto,
                ft.Row(
                    [grafico_imagem, imagem_jogador],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=30
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=25
        )
    )

    page.update()

ft.app(target=main, port=port)
