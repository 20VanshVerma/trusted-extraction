import streamlit as st
from extractor import extract_document


# -----------------------------
# Demo Data
# -----------------------------

DEMO_RESULT = {
    "document_type": "RECEIPT",
    "fields": {
        "Store Name": {
            "value": "East Repair Inc.",
            "trust_signal": "HIGH",
            "evidence": "East Repair Inc."
        },
        "Receipt Date": {
            "value": "11/02/2019",
            "trust_signal": "HIGH",
            "evidence": "Receipt Date 11/02/2019"
        },
        "Receipt Number": {
            "value": "US-001",
            "trust_signal": "HIGH",
            "evidence": "Receipt # US-001"
        },
        "Total Amount": {
            "value": "$154.06",
            "trust_signal": "HIGH",
            "evidence": "TOTAL $154.06"
        },
        "Payment Method": {
            "value": None,
            "trust_signal": "NOT_FOUND",
            "evidence": "No payment method is specified on the document."
        }
    }
}


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="Trusted Extraction",
    page_icon="📄",
    layout="wide"
)


# -----------------------------
# Header
# -----------------------------

st.title("📄 Trusted Extraction")
st.subheader("Document Intelligence with Trust Signals")

st.write(
    "Upload a document and extract structured information "
    "with field-level trust signals and evidence."
)


# -----------------------------
# Demo Mode
# -----------------------------

demo_mode = st.toggle(
    "🧪 Demo Mode",
    value=False,
    help="Use the previously extracted receipt result without calling Gemini."
)


# -----------------------------
# File Upload
# -----------------------------

uploaded_file = st.file_uploader(
    "Upload a document",
    type=["jpg", "jpeg", "png"]
)


# -----------------------------
# Process Document
# -----------------------------

if uploaded_file is not None:

    st.divider()

    col1, col2 = st.columns(2)

    # -----------------------------
    # Uploaded Document
    # -----------------------------

    with col1:

        st.markdown("### 📎 Uploaded Document")

        st.image(
            uploaded_file,
            caption=uploaded_file.name,
            use_container_width=True
        )


    # -----------------------------
    # Extraction
    # -----------------------------

    with col2:

        st.markdown("### 🔍 Extraction")

        if st.button("Extract Information", type="primary"):

            # -----------------------------
            # DEMO MODE
            # -----------------------------

            if demo_mode:

                st.info(
                    "🧪 Demo Mode: Using previously extracted data. "
                    "No Gemini API request was made."
                )

                result = DEMO_RESULT


            # -----------------------------
            # REAL GEMINI MODE
            # -----------------------------

            else:

                with st.spinner(
                    "Analyzing document with Gemini Vision..."
                ):

                    image_bytes = uploaded_file.getvalue()

                    try:

                        result = extract_document(
                            image_bytes=image_bytes,
                            mime_type=uploaded_file.type
                        )

                    except Exception as e:

                        error_message = str(e)

                        if (
                            "429" in error_message
                            or "Rate limit exceeded" in error_message
                        ):

                            st.warning(
                                "⚠️ Daily API limit reached"
                            )

                            st.info(
                                "Gemini's daily request limit has been "
                                "reached. Enable Demo Mode to continue "
                                "testing the interface without using "
                                "the API."
                            )

                            st.stop()

                        else:

                            st.error(
                                "❌ Something went wrong while "
                                "analyzing the document."
                            )

                            st.code(error_message)

                            st.stop()


            # -----------------------------
            # Check Extraction Result
            # -----------------------------

            if "error" in result:

                st.error(result["error"])

                if "raw_response" in result:
                    st.code(result["raw_response"])

            else:

                # -----------------------------
                # Document Type
                # -----------------------------

                document_type = result.get(
                    "document_type",
                    "UNKNOWN"
                )

                st.success(
                    f"📄 Document Type: {document_type}"
                )


                # -----------------------------
                # Extracted Fields
                # -----------------------------

                st.markdown("### 📋 Extracted Fields")

                fields = result.get("fields", {})


                # -----------------------------
                # Display Fields
                # -----------------------------

                for field_name, field_data in fields.items():

                    value = field_data.get("value")

                    trust = field_data.get(
                        "trust_signal",
                        "NOT_FOUND"
                    )

                    evidence = field_data.get(
                        "evidence",
                        ""
                    )


                    # HIGH
                    if trust == "HIGH":

                        st.success(
                            f"🟢 {field_name}: {value}\n\n"
                            f"Confidence Level: HIGH"
                        )


                    # MEDIUM
                    elif trust == "MEDIUM":

                        st.warning(
                            f"🟡 {field_name}: {value}\n\n"
                            f"Confidence Level: MEDIUM"
                        )


                    # LOW
                    elif trust == "LOW":

                        st.error(
                            f"🔴 {field_name}: {value}\n\n"
                            f"Confidence Level: LOW"
                        )


                    # NOT FOUND
                    else:

                        st.info(
                            f"⚪ {field_name}: Not Found\n\n"
                            f"Confidence Level: NOT FOUND"
                        )


                    # Evidence
                    with st.expander("🔎 View evidence"):

                        st.write(evidence)
