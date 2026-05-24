import os
from pathlib import Path
from typing import Any, Dict

import requests
import streamlit as st
from streamlit_cookies_controller import CookieController


def _default_api_base() -> str:
    return os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")


def _request(method: str, url: str, **kwargs: Any) -> requests.Response:
    return requests.request(method, url, timeout=180, **kwargs)


def _auth_headers() -> Dict[str, str]:
    token = st.session_state.get("auth_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _api_json(method: str, url: str, payload: Dict | None = None) -> Dict:
    response = _request(method, url, json=payload, headers=_auth_headers())
    response.raise_for_status()
    return response.json()


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


def _process_markdown_assets(markdown_text: str, api_base: str) -> str:
    if not markdown_text:
        return ""
    asset_base = _asset_base_url(api_base)
    text = markdown_text.replace("](/assets/", f"]({asset_base}/assets/")
    text = text.replace("](assets/", f"]({asset_base}/assets/")
    return text


def _list_knowledge_files() -> list[Path]:
    knowledge_dir = Path(__file__).resolve().parents[1] / "backend" / "knowledge_base"
    if not knowledge_dir.exists():
        return []
    return sorted(knowledge_dir.glob("*_knowledge.json"))


def _load_knowledge_file(path: Path) -> Dict:
    return __import__("json").loads(path.read_text(encoding="utf-8"))


INSERT_MARKER = "[[INSERT_HERE]]"


import html

def _render_chat_bubble(role: str, content: str) -> None:
    if role == "user":
        escaped_content = html.escape(content).replace("\n", "<br>")
        st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 1rem;">
                <div style="background: #fff7ed; border: 1px solid #fed7aa; color: #7c2d12; padding: 0.8rem 1.2rem; border-radius: 1.2rem 1.2rem 0 1.2rem; max-width: 80%; box-shadow: 0 1px 2px rgba(0,0,0,0.05); text-align: left; font-size: 0.95rem; line-height: 1.4rem;">
                    {escaped_content}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        with st.chat_message(role):
            st.markdown(content)


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
        .chat-bubble {
            padding: 0.7rem 0.9rem;
            border-radius: 14px;
            margin: 0.35rem 0;
            font-size: 0.95rem;
            line-height: 1.4rem;
        }
        .chat-user {
            background: #fff7ed;
            border: 1px solid #fed7aa;
            color: #7c2d12;
        }
        .chat-assistant {
            background: #0f172a;
            color: #f8fafc;
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


def _status_badge(is_published: bool) -> str:
    color = "#16a34a" if is_published else "#dc2626"
    label = "PUBLISHED" if is_published else "UNPUBLISHED"
    return (
        f"<span style='background:{color};color:#fff;padding:0.15rem 0.5rem;"
        f"border-radius:999px;font-size:0.7rem;'>{label}</span>"
    )


def main() -> None:
    st.set_page_config(page_title="Knowledge Studio", layout="wide")
    cookie_controller = CookieController()

    if st.query_params.get("action") == "login" and st.session_state.get("auth_token"):
        cookie_controller.set("auth_token", st.session_state["auth_token"])
        del st.query_params["action"]

    if st.query_params.get("action") == "logout":
        cookie_controller.remove("auth_token")
        del st.query_params["action"]
    
    _render_header()

    api_base = _default_api_base()

    if "active_view" not in st.session_state:
        st.session_state["active_view"] = "kb"
    if "auth_token" not in st.session_state:
        st.session_state["auth_token"] = st.context.cookies.get("auth_token")
    if "current_user" not in st.session_state:
        if st.session_state["auth_token"]:
            try:
                me = _api_json("GET", f"{api_base}/auth/me")
                st.session_state["current_user"] = me
            except Exception:
                st.session_state["auth_token"] = None
                st.session_state["current_user"] = None
                cookie_controller.remove("auth_token")
        else:
            st.session_state["current_user"] = None
    if "current_kb_id" not in st.session_state:
        st.session_state["current_kb_id"] = None

    user = st.session_state.get("current_user")
    if user:
        st.sidebar.caption(f"Logged in as {user['username']}")
    if st.session_state.get("auth_token"):
        if st.sidebar.button("Logout"):
            st.session_state["auth_token"] = None
            st.session_state["current_user"] = None
            st.session_state["current_kb_id"] = None
            st.session_state.pop("full_chat_history", None)
            st.session_state.pop("chat_messages_loaded", None)
            st.session_state.pop("chat_messages", None)
            st.session_state.pop("chat_session_id", None)
            st.query_params["action"] = "logout"
            st.rerun()

    if not st.session_state.get("auth_token"):
        st.subheader("Login")
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

        with login_tab:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                try:
                    response = _request(
                        "POST",
                        f"{api_base}/auth/login",
                        data={"grant_type": "password", "username": username.strip(), "password": password},
                    )
                    response.raise_for_status()
                    token = response.json()["access_token"]
                    st.session_state["auth_token"] = token
                    me = _api_json("GET", f"{api_base}/auth/me")
                    st.session_state["current_user"] = me
                    st.session_state.pop("full_chat_history", None)
                    st.session_state.pop("chat_messages_loaded", None)
                    st.session_state.pop("chat_messages", None)
                    st.session_state.pop("chat_session_id", None)
                    st.query_params["action"] = "login"
                    st.rerun()
                except requests.RequestException as exc:
                    st.error(f"Login failed: {exc}")

        with signup_tab:
            username = st.text_input("Username", key="signup_username")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            st.caption("Username: min 3 chars · Password: min 6 chars · Email must be valid")
            if st.button("Create Account"):
                username_value = username.strip()
                email_value = email.strip()
                errors = []
                if len(username_value) < 3:
                    errors.append("Username must be at least 3 characters.")
                if not email_value or "@" not in email_value:
                    errors.append("Email must include '@'.")
                elif "." not in email_value.split("@")[-1]:
                    errors.append("Email must include a domain (e.g., user@example.com).")
                if len(password) < 6:
                    errors.append("Password must be at least 6 characters.")

                if errors:
                    for err in errors:
                        st.error(err)
                else:
                    try:
                        response = _request(
                            "POST",
                            f"{api_base}/auth/signup",
                            json={
                                "username": username_value,
                                "email": email_value,
                                "password": password,
                            },
                        )
                        response.raise_for_status()
                        login = _request(
                            "POST",
                            f"{api_base}/auth/login",
                            data={"grant_type": "password", "username": username_value, "password": password},
                        )
                        login.raise_for_status()
                        token = login.json()["access_token"]
                        st.session_state["auth_token"] = token
                        me = _api_json("GET", f"{api_base}/auth/me")
                        st.session_state["current_user"] = me
                        st.session_state.pop("full_chat_history", None)
                        st.session_state.pop("chat_messages_loaded", None)
                        st.session_state.pop("chat_messages", None)
                        st.session_state.pop("chat_session_id", None)
                        st.success("Account created.")
                        st.query_params["action"] = "login"
                        st.rerun()
                    except requests.RequestException as exc:
                        st.error(f"Signup failed: {exc}")
        return

    try:
        kb_list = _api_json("GET", f"{api_base}/kb/my-kbs")
    except requests.RequestException:
        kb_list = []

    is_global_published = st.session_state["active_view"] == "kb_list" and st.session_state.get("kb_list_filter") == "published"
    is_view_only = st.session_state["active_view"] == "kb_view_only"

    if is_global_published or is_view_only:
        pass
    elif st.session_state["active_view"] in ("kb", "kb_list"):
        st.sidebar.header("My KBs")
        if kb_list:
            for kb in kb_list:
                status = "PUBLISHED" if kb["is_published"] else "UNPUBLISHED"
                icon = "🟢" if kb["is_published"] else "🔴"
                label = f"{icon} {kb['title']} · {status}"
                if st.sidebar.button(label, key=f"kb_{kb['id']}", help=kb["title"]):
                    detail = _api_json("GET", f"{api_base}/kb/{kb['id']}")
                    st.session_state["kb_title"] = detail.get("title", "")
                    st.session_state["kb_content"] = detail.get("content_md", "")
                    st.session_state["kb_source"] = detail.get("source_document", detail.get("title", ""))
                    st.session_state["kb_source_url"] = detail.get("source_document_url", "")
                    st.session_state["kb_saved_path"] = ""
                    st.session_state["current_kb_id"] = detail.get("id")
                    st.session_state["active_view"] = "kb"
                    st.rerun()
        else:
            st.sidebar.caption("No KBs yet. Create one below.")
    else:
        st.sidebar.header("Chat History")
        if "chat_messages_loaded" not in st.session_state:
            try:
                history = _api_json("GET", f"{api_base}/chatbot/history")
                st.session_state["full_chat_history"] = history
                st.session_state["chat_messages_loaded"] = True
            except requests.RequestException:
                st.session_state["chat_messages_loaded"] = True
        
        history_items = st.session_state.get("full_chat_history", [])
        if history_items:
            sessions = {}
            for h in history_items:
                sid = h.get("session_id") or str(h.get("id"))
                if sid not in sessions:
                    sessions[sid] = []
                sessions[sid].append(h)
                
            for sid in reversed(list(sessions.keys())):
                items = sessions[sid]
                first_item = items[0]
                snippet = first_item["query"][:35] + "..." if len(first_item["query"]) > 35 else first_item["query"]
                
                scol1, scol2 = st.sidebar.columns([4, 1])
                if scol1.button(f"💭 {snippet}", key=f"hist_btn_{sid}", help=first_item["query"]):
                    st.session_state["chat_session_id"] = sid
                    st.session_state["chat_messages"] = []
                    for msg in items:
                        st.session_state["chat_messages"].append({"role": "user", "content": msg["query"]})
                        st.session_state["chat_messages"].append({"role": "assistant", "content": msg["answer"]})
                    st.session_state["active_view"] = "chat"
                    st.rerun()
                if scol2.button("❌", key=f"hist_del_{sid}", help="Delete chat"):
                    success = False
                    with st.spinner("Deleting..."):
                        try:
                            _request("DELETE", f"{api_base}/chatbot/history/{sid}", headers=_auth_headers())
                            if st.session_state.get("chat_session_id") == sid:
                                st.session_state["chat_session_id"] = None
                                st.session_state["chat_messages"] = []
                            if "chat_messages_loaded" in st.session_state:
                                del st.session_state["chat_messages_loaded"]
                            success = True
                        except requests.RequestException as exc:
                            st.sidebar.error("Failed to delete chat")
                    if success:
                        st.rerun()
        else:
            st.sidebar.caption("No chat history yet.")

    if "kb_title" not in st.session_state:
        st.session_state["kb_title"] = ""
    if "kb_content" not in st.session_state:
        st.session_state["kb_content"] = ""
    if "kb_source" not in st.session_state:
        st.session_state["kb_source"] = ""
    if "kb_source_url" not in st.session_state:
        st.session_state["kb_source_url"] = ""
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

    nav_cols = st.columns([1.2, 1.8, 1.2])
    with nav_cols[1]:
        nav_left, nav_middle, nav_right = st.columns(3)
        is_kb = st.session_state.get("active_view", "kb") == "kb"
        is_pub = st.session_state.get("active_view") == "kb_list" and st.session_state.get("kb_list_filter") == "published"
        is_chat = st.session_state.get("active_view") == "chat"
        
        st.markdown(
            """
            <style>
            .stButton > button[kind="primary"] {
                background-color: #ffffff !important;
                color: #f97316 !important;
                border: 2px solid #f97316 !important;
                font-weight: 600 !important;
            }
            .stButton > button[kind="primary"]:hover {
                background-color: #fff7ed !important;
                border-color: #ea580c !important;
                color: #ea580c !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        if nav_left.button("Knowledge Builder", use_container_width=True, type="primary" if is_kb else "secondary"):
            st.session_state["active_view"] = "kb"
            st.rerun()
        if nav_middle.button("Published KBs", use_container_width=True, type="primary" if is_pub else "secondary"):
            st.session_state["active_view"] = "kb_list"
            st.session_state["kb_list_filter"] = "published"
            st.rerun()
        if nav_right.button("Insight Chat", use_container_width=True, type="primary" if is_chat else "secondary"):
            st.session_state["active_view"] = "chat"
            st.session_state["chat_messages"] = []
            st.session_state["chat_session_id"] = None
            st.rerun()

    if st.session_state["active_view"] == "kb":
        st.markdown("### Your Knowledge Base Analytics")
        total_kbs = len(kb_list)
        published_kbs = sum(1 for kb in kb_list if kb.get("is_published"))
        unpublished_kbs = total_kbs - published_kbs

        st.markdown(
            """
            <style>
            .metric-card {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            }
            .metric-value {
                font-size: 2.5rem;
                font-weight: 700;
                color: #f97316;
            }
            .metric-label {
                font-size: 0.9rem;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-top: 0.5rem;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{total_kbs}</div><div class="metric-label">Total KBs</div></div>', unsafe_allow_html=True)
            if st.button("View All KBs", key="btn_view_all", use_container_width=True):
                st.session_state["active_view"] = "kb_list"
                st.session_state["kb_list_filter"] = "all"
                st.rerun()
        with mcol2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{published_kbs}</div><div class="metric-label">Published KBs</div></div>', unsafe_allow_html=True)
            if st.button("View Published KBs", key="btn_view_pub", use_container_width=True):
                st.session_state["active_view"] = "kb_list"
                st.session_state["kb_list_filter"] = "published"
                st.rerun()
        with mcol3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{unpublished_kbs}</div><div class="metric-label">Unpublished KBs</div></div>', unsafe_allow_html=True)
            if st.button("View Unpublished KBs", key="btn_view_unpub", use_container_width=True):
                st.session_state["active_view"] = "kb_list"
                st.session_state["kb_list_filter"] = "unpublished"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        st.subheader("1) Upload a file")
        uploaded = st.file_uploader(
            "Upload any supported document",
            type=["txt", "vtt", "docx", "pptx", "pdf", "png", "jpg", "jpeg"],
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
                    
                    stored_name = Path(upload_payload.get("stored_path", "")).name
                    source_url = f"{_asset_base_url(api_base)}/uploads/{stored_name}" if stored_name else None
                    st.session_state["kb_source_url"] = source_url
                    
                    st.session_state["kb_saved_path"] = knowledge_payload.get("saved_path", "")
                    st.session_state["current_kb_id"] = None

                    st.success("Knowledge base draft ready. Scroll down to edit.")
                except requests.RequestException as exc:
                    st.error(f"Generation failed: {exc}")

        st.divider()
        st.subheader("2) Review and edit")

        col_editor, col_tools = st.columns([2.2, 1])

        with col_editor:
            st.text_input("Title", key="kb_title")
            source_doc = st.session_state.get('kb_source', 'Unknown')
            source_url = st.session_state.get('kb_source_url')
            if source_url and st.session_state.get("current_kb_id"):
                st.markdown(f"**Input:** [{source_doc}]({source_url})")
            else:
                st.caption(f"**Source Document:** {source_doc}")
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
                preview = _process_markdown_assets(preview, api_base)
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

            st.markdown("### Save & Publish")
            title = st.session_state.get("kb_title", "").strip()
            content = st.session_state.get("kb_content", "").strip()
            kb_id = st.session_state.get("current_kb_id")

            if st.button("Save KB"):
                if not title or not content:
                    st.warning("Title and content are required.")
                else:
                    try:
                        if kb_id:
                            payload = {"title": title, "content_md": content, "source_document": st.session_state.get("kb_source"), "source_document_url": st.session_state.get("kb_source_url")}
                            result = _api_json("PUT", f"{api_base}/kb/{kb_id}", payload)
                        else:
                            payload = {"title": title, "content_md": content, "source_document": st.session_state.get("kb_source"), "source_document_url": st.session_state.get("kb_source_url")}
                            result = _api_json("POST", f"{api_base}/kb/create", payload)
                            st.session_state["current_kb_id"] = result.get("id")
                        st.success("KB saved.")
                        st.rerun()
                    except requests.RequestException as exc:
                        st.error(f"Save failed: {exc}")

            publish_col, unpublish_col = st.columns(2)
            with publish_col:
                if st.button("Publish"):
                    if not title or not content:
                        st.warning("Title and content are required.")
                    else:
                        success = False
                        try:
                            payload = {"title": title, "content_md": content, "source_document": st.session_state.get("kb_source"), "source_document_url": st.session_state.get("kb_source_url")}
                            if kb_id:
                                _api_json("PUT", f"{api_base}/kb/{kb_id}", payload)
                            else:
                                result = _api_json("POST", f"{api_base}/kb/create", payload)
                                kb_id = result.get("id")
                                st.session_state["current_kb_id"] = kb_id
                            _api_json("POST", f"{api_base}/kb/{kb_id}/publish")
                            success = True
                        except requests.RequestException as exc:
                            st.error(f"Save & Publish failed: {exc}")
                        if success:
                            st.success("KB saved and published.")
                            st.rerun()

            with unpublish_col:
                if st.button("Unpublish"):
                    if not title or not content:
                        st.warning("Title and content are required.")
                    else:
                        success = False
                        try:
                            payload = {"title": title, "content_md": content, "source_document": st.session_state.get("kb_source"), "source_document_url": st.session_state.get("kb_source_url")}
                            if kb_id:
                                _api_json("PUT", f"{api_base}/kb/{kb_id}", payload)
                            else:
                                result = _api_json("POST", f"{api_base}/kb/create", payload)
                                kb_id = result.get("id")
                                st.session_state["current_kb_id"] = kb_id
                            _api_json("POST", f"{api_base}/kb/{kb_id}/unpublish")
                            success = True
                        except requests.RequestException as exc:
                            st.error(f"Save & Unpublish failed: {exc}")
                        if success:
                            st.success("KB saved and unpublished.")
                            st.rerun()

            if st.button("Delete KB"):
                if not kb_id:
                    st.warning("Select a KB to delete.")
                else:
                    success = False
                    with st.spinner("Deleting..."):
                        try:
                            _api_json("DELETE", f"{api_base}/kb/{kb_id}")
                            st.session_state["current_kb_id"] = None
                            st.session_state["kb_title"] = ""
                            st.session_state["kb_content"] = ""
                            st.session_state["kb_source"] = ""
                            st.session_state["kb_source_url"] = ""
                            st.session_state["kb_saved_path"] = ""
                            success = True
                        except requests.RequestException as exc:
                            st.error(f"Delete failed: {exc}")
                    if success:
                        st.rerun()

    elif st.session_state["active_view"] == "kb_list":
        filter_mode = st.session_state.get("kb_list_filter", "all")
        if filter_mode == "published":
            try:
                display_kbs = _api_json("GET", f"{api_base}/kb/published")
            except requests.RequestException:
                display_kbs = []
            st.subheader("Global Published KBs")
        elif filter_mode == "unpublished":
            display_kbs = [kb for kb in kb_list if not kb.get("is_published")]
            st.subheader("Unpublished KBs")
        else:
            display_kbs = kb_list
            st.subheader("All KBs")

        search_query = st.text_input("🔍 Search Knowledge Bases...", key="kb_search")
        if search_query:
            display_kbs = [kb for kb in display_kbs if search_query.lower() in kb["title"].lower() or search_query.lower() in kb.get("source_document", "").lower()]

        if st.button("← Back to Analytics"):
            st.session_state["active_view"] = "kb"
            st.rerun()

        st.divider()

        if display_kbs:
            for kb in display_kbs:
                row = st.columns([2.2, 1.2, 1.2, 1.2])
                with row[0]:
                    st.markdown(f"**{kb['title']}**", unsafe_allow_html=True)
                    if filter_mode == "published":
                        st.caption(f"Created by @{kb.get('owner_username', 'unknown')}")
                    else:
                        st.markdown(_status_badge(kb.get("is_published")), unsafe_allow_html=True)
                with row[1]:
                    st.caption(f"Created: {kb['created_at']}")
                with row[2]:
                    st.caption(f"Updated: {kb['updated_at']}")
                with row[3]:
                    if filter_mode == "published":
                        view_btn = st.button("View", key=f"list_view_{kb['id']}")
                        edit = False
                        toggle_pub = False
                        delete = False
                        if view_btn:
                            st.session_state["view_kb_id"] = kb['id']
                            st.session_state["active_view"] = "kb_view_only"
                            st.rerun()
                    else:
                        edit = st.button("Edit", key=f"list_edit_{kb['id']}")
                        if kb.get("is_published"):
                            toggle_pub = st.button("Unpublish", key=f"list_unpub_{kb['id']}")
                        else:
                            toggle_pub = st.button("Publish", key=f"list_pub_{kb['id']}")
                        delete = st.button("Delete", key=f"list_del_{kb['id']}")
                
                if edit:
                    detail = _api_json("GET", f"{api_base}/kb/{kb['id']}")
                    st.session_state["kb_title"] = detail.get("title", "")
                    st.session_state["kb_content"] = detail.get("content_md", "")
                    st.session_state["kb_source"] = detail.get("source_document", detail.get("title", ""))
                    st.session_state["kb_source_url"] = detail.get("source_document_url", "")
                    st.session_state["kb_saved_path"] = ""
                    st.session_state["current_kb_id"] = detail.get("id")
                    st.session_state["active_view"] = "kb"
                    st.rerun()
                if toggle_pub:
                    action = "unpublish" if kb.get("is_published") else "publish"
                    _api_json("POST", f"{api_base}/kb/{kb['id']}/{action}")
                    st.rerun()
                if delete:
                    success = False
                    with st.spinner("Deleting..."):
                        try:
                            _api_json("DELETE", f"{api_base}/kb/{kb['id']}")
                            if st.session_state.get("current_kb_id") == kb['id']:
                                st.session_state["current_kb_id"] = None
                                st.session_state["kb_title"] = ""
                                st.session_state["kb_content"] = ""
                                st.session_state["kb_source"] = ""
                                st.session_state["kb_source_url"] = ""
                                st.session_state["kb_saved_path"] = ""
                            success = True
                        except requests.RequestException as exc:
                            st.error(f"Failed to delete KB: {exc}")
                    if success:
                        st.rerun()
                st.divider()
        else:
            st.info("No KBs found for this filter.")

    elif st.session_state["active_view"] == "kb_view_only":
        kb_id = st.session_state.get("view_kb_id")
        if not kb_id:
            st.warning("No KB selected.")
            if st.button("← Back"):
                st.session_state["active_view"] = "kb_list"
                st.rerun()
        else:
            try:
                kb_detail = _api_json("GET", f"{api_base}/kb/{kb_id}")
            except requests.RequestException:
                kb_detail = None
            
            if st.button("← Back to Global Published KBs"):
                st.session_state["active_view"] = "kb_list"
                st.rerun()
            
            if kb_detail:
                st.title(kb_detail["title"])
                st.caption(f"Created by @{kb_detail.get('owner_username', 'unknown')} | Updated: {kb_detail['updated_at']}")
                
                st.divider()
                st.subheader("Content Preview")
                st.markdown(_process_markdown_assets(kb_detail["content_md"], api_base))
                
                st.divider()
                st.subheader("Input Source")
                if kb_detail.get("source_document_url"):
                    st.markdown(f"[{kb_detail['source_document']}]({kb_detail['source_document_url']})")
                else:
                    st.markdown(f"`{kb_detail.get('source_document', 'No source document')}`")
            else:
                st.error("Failed to load KB details.")


    else:
        st.subheader("Ask the Knowledge Base")
        st.caption("Answers are grounded only in retrieved knowledge base sections.")

        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = []

        for message in st.session_state["chat_messages"]:
            _render_chat_bubble(message["role"], _process_markdown_assets(message["content"], api_base))
            if message.get("retrieved"):
                with st.expander("Retrieved context"):
                    for item in message["retrieved"]:
                        st.markdown(
                            f"**{item['title']} — {item['section']}** (score {item['score']:.3f})"
                        )
                        st.markdown(_process_markdown_assets(item["content"], api_base))

        user_query = st.chat_input("Ask a question about your knowledge base")
        if user_query:
            st.session_state["chat_messages"].append(
                {"role": "user", "content": user_query}
            )
            _render_chat_bubble("user", user_query)

            try:
                with st.spinner("Retrieving insights from Knowledge Base..."):
                    response = _request(
                        "POST",
                        f"{api_base}/chatbot/query",
                        json={
                            "query": user_query,
                            "session_id": st.session_state.get("chat_session_id"),
                            "top_k": 5,
                            "min_score": 0.2,
                        },
                        headers=_auth_headers()
                    )
                    response.raise_for_status()
                
                answer_payload = response.json()
                st.session_state["chat_session_id"] = answer_payload.get("session_id")
                
                msg_content = answer_payload.get("answer", "No answer found.")
                retrieved = answer_payload.get("retrieved", [])
                
                st.session_state["chat_messages"].append(
                    {
                        "role": "assistant",
                        "content": msg_content,
                        "retrieved": retrieved,
                    }
                )
                
                _render_chat_bubble("assistant", _process_markdown_assets(msg_content, api_base))
                if retrieved:
                    with st.expander("Retrieved context"):
                        for item in retrieved:
                            st.markdown(
                                f"**{item['title']} — {item['section']}** (score {item['score']:.3f})"
                            )
                            st.markdown(_process_markdown_assets(item["content"], api_base))
                if "chat_messages_loaded" in st.session_state:
                    del st.session_state["chat_messages_loaded"]
            except requests.RequestException as exc:
                st.error(f"Chatbot query failed: {exc}")


if __name__ == "__main__":
    main()
