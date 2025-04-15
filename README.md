# Large Orthomosaic Tiling

Large Orthomosaic Tiling é uma ferramenta em Python para dividir imagens ortomosaico grandes (TIFF) em tiles menores de forma eficiente em memória. Ela utiliza a leitura em janelas (windows) com o [rasterio](https://rasterio.readthedocs.io/) para evitar o carregamento completo da imagem na RAM e o [OpenCV](https://opencv.org/) para salvar os tiles no formato PNG. Essa abordagem é especialmente útil quando se trabalha com imagens georreferenciadas de alta resolução, onde o gerenciamento de memória é crítico.

## Features

- **Memória eficiente:** Lê apenas as partes necessárias da imagem utilizando janelas.
- **Suporte para imagens grandes:** Ideal para orthomosaicos e outras imagens de alta resolução.
- **Dimensões reais:** Define o tamanho do tile em metros e converte automaticamente para pixels.
- **Salva somente tiles com conteúdo:** Ignora tiles que contenham apenas pixels de fundo (valor zero).
- **Saída em PNG:** Gera tiles no formato PNG, preservando a qualidade da imagem.
- **Nomeação personalizada:** Utiliza um nome de projeto para prefixar os arquivos gerados.

## Requisitos

- Python 3.11
- [OpenCV](https://pypi.org/project/opencv-python/) (`cv2`)
- [numpy](https://pypi.org/project/numpy/)
- [termcolor](https://pypi.org/project/termcolor/)
- [rasterio](https://pypi.org/project/rasterio/)

## Instalação das dependências:

   ```bash
   pip install opencv-python numpy termcolor rasterio
   ```

## Uso

Execute o script via linha de comando, passando os seguintes argumentos:

```bash
python split.py <input_image_path> <tile_width_meters> <save_path> <project_name>
```

Onde:

- `input_image_path`: Caminho para a imagem .tif (ortomosaico) de entrada.
- `tile_width_meters`: Largura (e altura, pois os tiles são quadrados) de cada tile em metros.
- `save_path`: Diretório onde os tiles serão salvos. O diretório será criado se não existir.
- `project_name`: Nome do projeto que será utilizado como prefixo nos nomes dos arquivos gerados.

### Exemplo

```bash
python split.py "D:\downloads\ortho.tif" 250 "D:\downloads\tiles" "MyProject"
```

Esse comando dividirá a imagem `ortho.tif` em tiles de 250X250 metros (convertidos automaticamente para pixels com base na resolução da imagem), salvando os arquivos PNG resultantes no diretório `D:\downloads\tiles` com nomes iniciados por `MyProject_tile_`.

