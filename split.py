import os
import cv2
import argparse
import numpy as np
import rasterio
from rasterio.windows import Window
from termcolor import colored
import math

def split_image(image_path, tile_width_meters, save_path, project_name):
    print(f"Processando {image_path} para cortes de {tile_width_meters}x{tile_width_meters} metros")

    # Verifica se o arquivo de entrada existe
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"O arquivo {image_path} não foi encontrado.")

    # Cria o diretório de saída, se não existir
    if not os.path.exists(save_path):
        print(colored("Aviso: O diretório de salvamento não existe e será criado.", "yellow"))
        os.makedirs(save_path)

    with rasterio.open(image_path) as src:
        img_width = src.width
        img_height = src.height
        count_bands = src.count

        # Obtém a resolução espacial em metros/pixel
        transform = src.transform
        pixel_width_meters = abs(transform[0])  # Resolução X (metros/pixel)
        pixel_height_meters = abs(transform[4])  # Resolução Y (metros/pixel)
        
        # Verificação da resolução
        if pixel_width_meters == 0 or pixel_height_meters == 0:
            raise ValueError("Não foi possível determinar a resolução espacial da imagem. Verifique se o GeoTIFF possui metadados válidos.")

        # Converte o tamanho do tile de metros para pixels
        tile_width_pixels = math.ceil(tile_width_meters / pixel_width_meters)
        
        print("=== Metadados da imagem ===")
        print(f"  Largura x Altura: {img_width} x {img_height}")
        print(f"  Número de bandas: {count_bands}")
        print(f"  Resolução espacial: {pixel_width_meters:.6f} x {pixel_height_meters:.6f} metros/pixel")
        print(f"  Tamanho do tile: {tile_width_meters} metros = {tile_width_pixels} pixels")
        print(f"  Dtypes: {src.dtypes}")
        print(f"  Perfil rasterio: {src.profile}")
        print("===========================")

        # Quantos tiles na horizontal/vertical
        w_tiles = (img_width + tile_width_pixels - 1) // tile_width_pixels
        h_tiles = (img_height + tile_width_pixels - 1) // tile_width_pixels
        n_tiles = w_tiles * h_tiles
        print(f"Criando {n_tiles} tiles ({w_tiles} x {h_tiles}).")

        tile_number = 0
        for i in range(h_tiles):
            for j in range(w_tiles):
                x = j * tile_width_pixels
                y = i * tile_width_pixels
                width = min(tile_width_pixels, img_width - x)
                height = min(tile_width_pixels, img_height - y)

                window = Window(x, y, width, height)
                # Lê dados do tile: shape = (band, height, width)
                tile_data = src.read(window=window)

                # Se for 4 bandas, tratamos como RGBA ou BGRA
                if count_bands == 4:
                    # Transpõe para (H, W, 4)
                    out_img = np.transpose(tile_data, (1, 2, 0))

                    # Muitas vezes, a ordem real é RGBA, mas o OpenCV espera BGRA.
                    # Trocamos R<->B para que apareça corretamente nas ferramentas comuns.
                    # Se ainda sair estranho, tente remover esta linha.
                    out_img = out_img[:, :, [2, 1, 0, 3]]

                    # Verifica se TODO o alpha é 0 => tile totalmente vazio
                    alpha_channel = out_img[:, :, 3]
                    if np.all(alpha_channel == 0):
                        print(f"Tile {tile_number} vazio (alpha=0), ignorado.")
                        tile_number += 1
                        continue

                    # Aqui NÃO vamos preencher alpha=0 com branco!
                    # Mantemos o canal alpha tal como está para obter transparência real.

                    # Salva esse tile em PNG de 4 canais
                    tile_filename = f"{project_name}_tile_{tile_number}.png"
                    output_path = os.path.join(save_path, tile_filename)
                    cv2.imwrite(output_path, out_img)
                    print(f"Tile {tile_number} salvo em {output_path}")
                    tile_number += 1

                elif count_bands == 3:
                    # Caso de 3 bandas (RGB). Simples.
                    out_img = np.transpose(tile_data, (1, 2, 0))
                    # Se precisar trocar B<->R, descomente:
                    # out_img = out_img[:, :, [2,1,0]]

                    if not np.any(out_img):
                        print(f"Tile {tile_number} vazio, ignorado.")
                        tile_number += 1
                        continue

                    tile_filename = f"{project_name}_tile_{tile_number}.png"
                    output_path = os.path.join(save_path, tile_filename)
                    cv2.imwrite(output_path, out_img)
                    print(f"Tile {tile_number} salvo em {output_path}")
                    tile_number += 1

                else:
                    # Se for 1 banda ou mais de 4 bandas, trate conforme a necessidade
                    print(f"Tile {tile_number} com {count_bands} bandas não suportado. Ignorando.")
                    tile_number += 1

    print("Processamento concluído.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Divide ortofoto .tif em tiles PNG, mantendo transparência (alpha)."
    )
    parser.add_argument("input_image_path", type=str, help="Caminho do arquivo .tif")
    parser.add_argument("tile_width_meters", type=float, help="Dimensão do tile (em metros)")
    parser.add_argument("save_path", type=str, help="Diretório para salvar os tiles")
    parser.add_argument("project_name", type=str, help="Nome do projeto (prefixo)")

    args = parser.parse_args()
    split_image(args.input_image_path, args.tile_width_meters, args.save_path, args.project_name)
