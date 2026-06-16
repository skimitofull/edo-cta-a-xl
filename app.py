import pandas as pd
import streamlit as st

from processors.ocr_local import pdf_to_ocr_pages
from processors.hsbc_parser import parse_hsbc_movements
from processors.validator import validate_balances
from processors.excel_exporter import build_excel


st.set_page_config(
    page_title="Agente Bancos - Fase 1",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 Agente Bancos - Fase 1")
st.caption("Subir PDF → Procesar → Descargar Excel")

with st.sidebar:
    st.header("Configuración")
    banco = st.selectbox("Banco", ["HSBC"], index=0)
    dpi = st.slider("Calidad OCR / DPI", min_value=150, max_value=350, value=250, step=50)
    idioma = st.selectbox("Idioma OCR", ["spa", "eng", "spa+eng"], index=0)
    st.info("Esta fase usa OCR local con Tesseract. No usa Azure ni APIs de pago.")

uploaded_file = st.file_uploader(
    "Sube un estado de cuenta PDF",
    type=["pdf"],
    accept_multiple_files=False,
)

if uploaded_file is None:
    st.info("Sube un PDF para comenzar.")
    st.stop()

st.success(f"Archivo cargado: {uploaded_file.name}")

if st.button("Procesar PDF", type="primary"):
    with st.spinner("Procesando PDF con OCR local en Streamlit Cloud..."):
        try:
            pdf_bytes = uploaded_file.read()

            ocr_pages = pdf_to_ocr_pages(pdf_bytes, dpi=dpi, lang=idioma)
            movements = parse_hsbc_movements(ocr_pages)
            movements = validate_balances(movements)

            df = pd.DataFrame(movements)

            if df.empty:
                st.warning(
                    "No se detectaron movimientos con suficiente estructura. "
                    "El Excel incluirá el texto OCR para revisión."
                )
            else:
                st.subheader("Vista previa de movimientos detectados")
                st.dataframe(df, use_container_width=True)

                total_cargos = pd.to_numeric(df.get("Cargo", 0), errors="coerce").fillna(0).sum()
                total_abonos = pd.to_numeric(df.get("Abono", 0), errors="coerce").fillna(0).sum()
                con_observacion = df["Observacion"].astype(str).str.len().gt(0).sum() if "Observacion" in df else 0

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Movimientos", len(df))
                c2.metric("Cargos", f"${total_cargos:,.2f}")
                c3.metric("Abonos", f"${total_abonos:,.2f}")
                c4.metric("Revisar", int(con_observacion))

            excel_bytes = build_excel(
                movements=movements,
                ocr_pages=ocr_pages,
                source_filename=uploaded_file.name,
            )

            st.download_button(
                label="Descargar Excel",
                data=excel_bytes,
                file_name=uploaded_file.name.replace(".pdf", "_movimientos.xlsx"),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            with st.expander("Ver texto OCR por página"):
                for page in ocr_pages:
                    st.markdown(f"### Página {page['page']}")
                    st.text(page["text"][:6000])

        except Exception as e:
            st.error("No se pudo procesar el PDF.")
            st.exception(e)
