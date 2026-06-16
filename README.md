# Agente Bancos - Fase 1

Aplicación en Streamlit para subir estados de cuenta PDF, procesarlos con OCR local en la nube y descargar un Excel con movimientos bancarios.

## Objetivo

PDF → Procesar → Vista previa → Descargar Excel

## Pensado para Streamlit Cloud

Este proyecto está diseñado para correr desde GitHub en Streamlit Cloud. No depende de una computadora específica.

Streamlit Cloud instalará Tesseract usando `packages.txt`.

## Archivos importantes

```text
agente_bancos_streamlit/
├── app.py
├── requirements.txt
├── packages.txt
├── .gitignore
├── processors/
│   ├── __init__.py
│   ├── ocr_local.py
│   ├── hsbc_parser.py
│   ├── validator.py
│   └── excel_exporter.py
└── README.md
```

## Subir a GitHub

```bash
git init
git add .
git commit -m "Agente bancos fase 1"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/agente-bancos-streamlit.git
git push -u origin main
```

## Publicar en Streamlit Cloud

1. Entrar a https://share.streamlit.io/
2. New app
3. Elegir el repositorio de GitHub
4. Main file path: `app.py`
5. Deploy

## Uso

1. Abrir la app.
2. Subir PDF.
3. Elegir banco HSBC.
4. Procesar.
5. Descargar Excel.

## Nota

Esta fase no usa Azure ni APIs de pago. Usa OCR local con Tesseract instalado en Streamlit Cloud.
