import os
from pathlib import Path
from typing import Any, Dict

import requests
import streamlit as st


def _default_api_base() -> str:
    return os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")


def _request(method: str, url: str, **kwargs: Any) -> requests.Response:
    return requests.request(method, url, timeout=180, **kwargs)


def _upload_asset(api_base: str, filename: str, data: bytes, mime: str) -> Dict:
    url = f"{api_base}/knowledge/assets"
    files = {"file": (filename, data, mime)}
    response = _request("POST", url, files=files)
    response.raise_for_status()
    return response.json()


def _asset_base_url(api_base: str) -> str:
    if "/api/" in api_base:
        return api_base.split("/api/")[0].rstrip("/")
    if api_base.endswith("/api"):
        return api_base.rsplit("/api", 1)[0].rstrip("/")
    return api_base.rstrip("/")


def _list_knowledge_files() -> list[Path]:
    knowledge_dir = Path(__file__).resolve().parents[1] / "backend" / "knowledge_base"
    if not knowledge_dir.exists():
        return []
    return sorted(knowledge_dir.glob("*_knowledge.json"))


def _load_knowledge_file(path: Path) -> Dict:
    return __import__("json").loads(path.read_text(encoding="utf-8"))


INSERT_MARKER = "[[INSERT_HERE]]"


def _render_header() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Space Grotesk', sans-serif;
        }
        .app-shell {
            background: linear-gradient(135deg, #f97316 0%, #fb923c 60%, #fdba74 100%);
            padding: 1.5rem 2rem;
            border-radius: 16px;
            border: 1px solid #f97316;
            margin-bottom: 1rem;
            color: #ffffff;
        }
        .app-shell h1, .app-shell p {
            color: #ffffff;
        }
        .pill {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            background: #ffffff;
            color: #9a3412;
            font-size: 0.75rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }
        section[data-testid="stSidebar"] .stButton > button {
            width: 100%;
            text-align: left;
            border: 1px solid #fed7aa;
            border-radius: 12px;
            background: #fff7ed;
            color: #7c2d12;
            padding: 0.6rem 0.8rem;
            height: 3.4rem;
            min-height: 3.4rem;
            max-height: 3.4rem;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            box-shadow: 0 1px 0 rgba(0, 0, 0, 0.04);
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background: #ffedd5;
            border-color: #fb923c;
        }
        section[data-testid="stSidebar"] .stButton > button > div {
            width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        section[data-testid="stSidebar"] .stButton {
            margin: 0.4rem 0;
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 1.1rem;
            padding-bottom: 1.1rem;
            padding-left: 0.9rem;
            padding-right: 0.9rem;
        }
        </style>
        <div class="app-shell">
            <div class="pill">Knowledge Studio</div>
            <h1>Enterprise Knowledge Builder</h1>
            <p>Upload a document, get a structured knowledge base draft, then refine and approve it.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Knowledge Studio", layout="wide")
    _render_header()

    api_base = _default_api_base()

    st.sidebar.header("History")
    knowledge_files = _list_knowledge_files()
    if knowledge_files:
        for file_path in knowledge_files:
            file_name = file_path.name
            if st.sidebar.button(file_name, key=f"history_{file_name}", help=file_name):
                payload = _load_knowledge_file(file_path)
                st.session_state["kb_title"] = payload.get("title", "")
                st.session_state["kb_content"] = payload.get("content", "")
                st.session_state["kb_source"] = payload.get("source", file_name)
                st.session_state["kb_saved_path"] = str(file_path)
                st.session_state["history_loaded"] = file_name
    else:
        st.sidebar.caption("No saved knowledge files yet.")

    if "kb_title" not in st.session_state:
        st.session_state["kb_title"] = ""
    if "kb_content" not in st.session_state:
        st.session_state["kb_content"] = ""
    if "kb_source" not in st.session_state:
        st.session_state["kb_source"] = ""
    if "kb_saved_path" not in st.session_state:
        st.session_state["kb_saved_path"] = ""
    if "kb_pending_insert" not in st.session_state:
        st.session_state["kb_pending_insert"] = None

    if st.session_state.get("kb_pending_insert"):
        insert_text = st.session_state.get("kb_pending_insert")
        content = st.session_state.get("kb_content", "")
        if INSERT_MARKER in content:
            content = content.replace(INSERT_MARKER, insert_text, 1)
        else:
            content = content + "\n" + insert_text + "\n"
        st.session_state["kb_content"] = content
        st.session_state["kb_pending_insert"] = None

    st.subheader("1) Upload a file")
    uploaded = st.file_uploader(
        "Upload any supported document",
        type=["vtt", "docx", "pptx", "pdf", "png", "jpg", "jpeg"],
    )

    if st.button("Generate Knowledge Base", disabled=uploaded is None):
        if uploaded is None:
            st.warning("Please upload a file first.")
        else:
            try:
                with st.spinner("Uploading and extracting..."):
                    upload_url = f"{api_base}/upload"
                    files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
                    upload_response = _request("POST", upload_url, files=files)
                    upload_response.raise_for_status()
                    upload_payload = upload_response.json()

                extracted_name = Path(upload_payload.get("extracted_path", "")).name
                if not extracted_name:
                    st.error("Extraction did not return a stored file name.")
                    return

                with st.spinner("Generating knowledge base..."):
                    knowledge_url = f"{api_base}/knowledge/from-extracted"
                    payload = {
                        "extracted_filename": extracted_name,
                        "chunk_size": 1200,
                        "chunk_overlap": 150,
                        "max_parts": 10,
                        "save_output": True,
                    }
                    knowledge_response = _request("POST", knowledge_url, json=payload)
                    knowledge_response.raise_for_status()
                    knowledge_payload = knowledge_response.json()

                st.session_state["kb_title"] = knowledge_payload.get("title", "")
                st.session_state["kb_content"] = knowledge_payload.get("content", "")
                st.session_state["kb_source"] = knowledge_payload.get("source", uploaded.name)
                st.session_state["kb_saved_path"] = knowledge_payload.get("saved_path", "")

                st.success("Knowledge base draft ready. Scroll down to edit.")
            except requests.RequestException as exc:
                st.error(f"Generation failed: {exc}")

    st.divider()
    st.subheader("2) Review and edit")

    col_editor, col_tools = st.columns([2.2, 1])

    with col_editor:
        st.text_input("Title", key="kb_title")
        st.text_area(
            "Knowledge Base Content (Markdown)",
            key="kb_content",
            height=520,
        )
        st.caption("You can edit freely. Markdown supported.")
        st.caption(f"Tip: Place {INSERT_MARKER} where you want an image or link inserted.")

        if st.session_state.get("kb_content"):
            st.markdown("### Preview")
            preview = st.session_state.get("kb_content", "")
            asset_base = _asset_base_url(api_base)
            preview = preview.replace("](/assets/", f"]({asset_base}/assets/")
            preview = preview.replace("](assets/", f"]({asset_base}/assets/")
            st.markdown(preview)

    with col_tools:
        st.markdown("### Insert Tools")
        if st.button("Insert marker"):
            st.session_state["kb_pending_insert"] = INSERT_MARKER
            st.rerun()

        link_label = st.text_input("Link label", value="Reference")
        link_url = st.text_input("Link URL", value="https://")
        if st.button("Insert Link"):
            link_md = f"[{link_label}]({link_url})"
            st.session_state["kb_pending_insert"] = f"\n{link_md}\n"
            st.rerun()

        image_file = st.file_uploader(
            "Attach image",
            type=["png", "jpg", "jpeg"],
            key="kb_image",
        )
        if image_file is not None:
            st.image(image_file, caption="Preview", use_column_width=True)
            if st.button("Insert Image"):
                try:
                    asset = _upload_asset(
                        api_base,
                        image_file.name,
                        image_file.getvalue(),
                        image_file.type or "image/png",
                    )
                    image_md = f"![{image_file.name}]({asset['asset_path']})"
                    st.session_state["kb_pending_insert"] = f"\n{image_md}\n"
                    st.rerun()
                except requests.RequestException as exc:
                    st.error(f"Image upload failed: {exc}")

        st.markdown("### Approval")
        if st.button("Approve Knowledge Base"):
            title = st.session_state.get("kb_title", "").strip()
            content = st.session_state.get("kb_content", "").strip()
            source = st.session_state.get("kb_source", "document")
            if not title or not content:
                st.warning("Title and content are required before approval.")
            else:
                approve_url = f"{api_base}/knowledge/approve"
                payload = {"source": source, "title": title, "content": content}
                try:
                    response = _request("POST", approve_url, json=payload)
                    response.raise_for_status()
                    result = response.json()
                    st.session_state["kb_saved_path"] = result.get("saved_path", "")
                    st.success("Knowledge base approved and saved.")
                except requests.RequestException as exc:
                    st.error(f"Approval failed: {exc}")

        saved_path = st.session_state.get("kb_saved_path")
        if saved_path:
            st.info(f"Saved to: {saved_path}")


if __name__ == "__main__":
    main()
