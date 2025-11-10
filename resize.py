"""
Script para redimensionar imagens que excedem 20MB para dimensões máximas ou tamanho de arquivo.
Utiliza a biblioteca Pillow para manipulação de imagens.
Para usar, execute o script passando o diretório contendo as imagens como argumento.
Exemplo:
    python resize.py /caminho/para/imagens
Exemplo com parâmetros personalizados:
    python resize.py /caminho/para/imagens --max-size 15 --max-width 12000 --max-height 8000 --quality 90
"""

import os
import argparse
from PIL import Image
from termcolor import colored

# Aumenta o limite de pixels para permitir processar imagens muito grandes
# Necessário para ortofotos e imagens de alta resolução
Image.MAX_IMAGE_PIXELS = None


def get_file_size_mb(file_path):
    """Retorna o tamanho do arquivo em MB."""
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb


def resize_image(image_path, max_size_mb=20, max_dimensions=(16400, 10900), quality=95):
    """
    Redimensiona uma imagem se ela exceder o tamanho máximo em MB ou dimensões.
    
    Args:
        image_path: Caminho da imagem a ser processada
        max_size_mb: Tamanho máximo em MB (padrão: 20)
        max_dimensions: Tupla (largura, altura) máximas (padrão: 16400x10900)
        quality: Qualidade de compressão JPEG (padrão: 95)
    """
    file_size_mb = get_file_size_mb(image_path)
    
    # Verifica se precisa processar
    needs_resize = file_size_mb > max_size_mb
    
    if not needs_resize:
        print(f"  {os.path.basename(image_path)}: {file_size_mb:.2f} MB - OK (não precisa redimensionar)")
        return False
    
    print(f"  {os.path.basename(image_path)}: {file_size_mb:.2f} MB - " + colored("REDIMENSIONANDO", "yellow"))
    
    try:
        # Abre a imagem
        with Image.open(image_path) as img:
            original_size = img.size
            print(f"    Dimensões originais: {original_size[0]} x {original_size[1]}")
            
            # Converte para RGB se necessário (para JPEG)
            if img.mode == 'RGBA' or img.mode == 'LA':
                # Mantém transparência para PNG
                save_format = 'PNG'
                save_params = {'optimize': True}
                converted_img = img
            else:
                # Converte para JPEG
                save_format = 'JPEG'
                save_params = {'quality': quality, 'optimize': True}
                converted_img = img.convert('RGB') if img.mode != 'RGB' else img
            
            # Calcula fator de redução baseado no tamanho do arquivo
            # Tamanho do arquivo é aproximadamente proporcional à área (largura × altura)
            # Fator = sqrt(tamanho_alvo / tamanho_atual)
            size_ratio = max_size_mb / file_size_mb
            scale_factor = size_ratio ** 0.5  # Raiz quadrada porque área é 2D
            
            # Aplica um fator de segurança (90%) para garantir que fique abaixo do limite
            scale_factor *= 0.9
            
            # Calcula novas dimensões
            new_width = int(original_size[0] * scale_factor)
            new_height = int(original_size[1] * scale_factor)
            
            # Garante que não exceda as dimensões máximas
            if new_width > max_dimensions[0] or new_height > max_dimensions[1]:
                # Usa thumbnail para respeitar aspect ratio
                aspect_ratio = original_size[0] / original_size[1]
                if new_width > max_dimensions[0]:
                    new_width = max_dimensions[0]
                    new_height = int(new_width / aspect_ratio)
                if new_height > max_dimensions[1]:
                    new_height = max_dimensions[1]
                    new_width = int(new_height * aspect_ratio)
            
            print(f"    Fator de redução calculado: {scale_factor:.2%}")
            print(f"    Novas dimensões: {new_width} x {new_height}")
            
            # Redimensiona
            resized_img = converted_img.copy()
            resized_img.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Salva
            resized_img.save(image_path, save_format, **save_params)
            print(f"    Salvo como {save_format}")
            
            new_size_mb = get_file_size_mb(image_path)
            print(f"    Novo tamanho: {new_size_mb:.2f} MB - " + colored("✓", "green"))
            
            # Se ainda ficou grande (pode acontecer com PNGs complexos), tenta mais uma vez
            if new_size_mb > max_size_mb:
                print(f"    " + colored("Ainda acima do limite, ajustando...", "yellow"))
                # Recalcula com base no novo tamanho
                adjustment = (max_size_mb / new_size_mb) ** 0.5 * 0.85
                final_width = int(resized_img.size[0] * adjustment)
                final_height = int(resized_img.size[1] * adjustment)
                
                resized_img.thumbnail((final_width, final_height), Image.Resampling.LANCZOS)
                resized_img.save(image_path, save_format, **save_params)
                
                final_size_mb = get_file_size_mb(image_path)
                print(f"    Tamanho final: {final_size_mb:.2f} MB - " + colored("✓", "green"))
            
            return True
            
    except Exception as e:
        print(colored(f"    Erro ao processar {image_path}: {str(e)}", "red"))
        return False


def process_directory(directory_path, max_size_mb=20, max_dimensions=(16400, 10900), quality=95):
    """
    Varre um diretório e redimensiona todas as imagens que excedem o tamanho máximo.
    
    Args:
        directory_path: Caminho do diretório a ser processado
        max_size_mb: Tamanho máximo em MB (padrão: 20)
        max_dimensions: Tupla (largura, altura) máximas (padrão: 16400x10900)
        quality: Qualidade de compressão JPEG (padrão: 95)
    """
    print(f"Processando diretório: {directory_path}")
    print(f"Limite de tamanho: {max_size_mb} MB")
    print(f"Dimensões máximas: {max_dimensions[0]} x {max_dimensions[1]} px")
    print(f"Qualidade: {quality}")
    print("=" * 80)
    
    # Verifica se o diretório existe
    if not os.path.isdir(directory_path):
        raise NotADirectoryError(f"O diretório {directory_path} não foi encontrado.")
    
    # Extensões de imagem suportadas
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
    
    # Contadores
    total_images = 0
    resized_images = 0
    
    # Varre o diretório recursivamente
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            # Verifica se é uma imagem
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in image_extensions:
                continue
            
            total_images += 1
            file_path = os.path.join(root, filename)
            
            # Tenta redimensionar
            if resize_image(file_path, max_size_mb, max_dimensions, quality):
                resized_images += 1
    
    # Resumo final
    print("=" * 80)
    print("Processamento concluído.")
    print(f"Total de imagens encontradas: {total_images}")
    print(f"Imagens redimensionadas: {resized_images}")
    print(f"Imagens já dentro do limite: {total_images - resized_images}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Redimensiona imagens que excedem 20MB para dimensões máximas ou tamanho de arquivo."
    )
    parser.add_argument("directory", type=str, help="Diretório contendo as imagens")
    parser.add_argument(
        "--max-size",
        type=float,
        default=20,
        help="Tamanho máximo em MB (padrão: 20)"
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=16400,
        help="Largura máxima em pixels (padrão: 16400)"
    )
    parser.add_argument(
        "--max-height",
        type=int,
        default=10900,
        help="Altura máxima em pixels (padrão: 10900)"
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=95,
        help="Qualidade de compressão JPEG 1-100 (padrão: 95)"
    )
    
    args = parser.parse_args()
    
    max_dimensions = (args.max_width, args.max_height)
    process_directory(args.directory, args.max_size, max_dimensions, args.quality)
