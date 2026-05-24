# Enterprise Knowledge Studio


## Project Overview

In many enterprises, valuable knowledge is often scattered across meeting discussions, Teams transcripts, documents, PDFs, presentations, and internal files. Employees frequently spend significant time searching for information that has already been discussed in a meeting or documented somewhere within the organization.

Enterprise Knowledge Studio addresses this problem by transforming raw enterprise content into structured, reusable knowledge articles using AI.

By combining AI-assisted knowledge generation with semantic retrieval and chatbot interaction, the platform helps organizations reduce repeated effort, improve knowledge accessibility, and accelerate information discovery across teams.

**Key Features**

- **User accounts:** Signup, login, and a personalized workspace for each user.
- **Document upload & extraction:** Upload common file types (PDF, DOCX, PPTX, transcripts, images); the system extracts text and stores a processed version for review.
 - **Automated knowledge drafting (LLM):** Converts extracted text into a draft knowledge article (with headings and sections) using a large language model so subject-matter experts can review instead of authoring from scratch.
- **Rich editor & assets:** Edit drafts in Markdown, insert images and links, preview content, and save changes.
- **Publish/unpublish workflow:** Save drafts, publish approved articles to a shared library, and unpublish when needed.
 - **Insight Chat (RAG-backed + LLM):** Ask the knowledge base questions and receive generative answers supported by retrieved document sections and a large language model.
- **Chat history & sessions:** Conversations are saved per user and can be viewed or deleted.
- **Vector sync & semantic search:** Published articles are converted into searchable vectors so the Insight Chat can find relevant content quickly.
 - **Edit created KBs:** Users can open and edit any knowledge base they created, update content, and re-save or publish changes.
 - **Search published KBs:** Browse and search the global library of published knowledge bases to find relevant articles.


## Why Enterprise Knowledge Studio is Different

Most enterprise copilots and chatbot solutions primarily focus on answering questions from existing knowledge sources. They typically depend on pre-created documentation and act mainly as conversational retrieval systems.

Enterprise Knowledge Studio goes beyond being just a chatbot or AI assistant.

This platform is designed as an **end-to-end AI-powered knowledge creation and management system** that helps organizations not only consume knowledge, but also generate, structure, refine, publish, and continuously improve it.


### How It Differs from Traditional Knowledge Base Chatbots

Traditional knowledge base chatbots mainly focus on searching and answering questions from existing documentation. Their role is typically limited to retrieving information from already-created knowledge articles.

Enterprise Knowledge Studio extends beyond retrieval by helping organizations generate high-quality knowledge articles using AI.

Key differences:
- Automatically converts raw enterprise documents into structured KB drafts.
- Reduces manual effort required to create knowledge articles.
- Allows users to review, edit, refine, and publish AI-generated KBs.
- Standardizes KB creation workflows using AI-assisted drafting.
- Combines AI-powered knowledge generation with chatbot-based retrieval in a single platform.

### How It Differs from Copilot AI Agents

Copilot AI agents are primarily designed for productivity assistance, workflow automation, and conversational task execution across enterprise applications.

Enterprise Knowledge Studio is specifically focused on accelerating enterprise knowledge creation and enabling AI-powered interaction on top of that generated knowledge.

Key differences:
- Purpose-built for AI-assisted KB article generation from enterprise documents.
- Creates structured and reusable knowledge articles from raw content.
- Enables human validation and refinement before publishing.
- Provides an Insight Chat grounded on approved/generated KB articles.
- Focuses on improving knowledge authoring efficiency rather than general task automation.
- Combines KB generation, editing, publishing, and AI-powered querying within a unified workflow.




**User Workflow (what users do)**

1. Log in or create an account.
2. Upload a document (or select a pre-extracted file).
3. Generate a knowledge draft automatically from the uploaded content.
4. Review, edit, insert images/links, and preview the article.
5. Save the draft; optionally publish it to the global library.
6. Edit or manage your KBs:
   - Edit content of knowledge bases you created and save updates
   - Publish / unpublish or delete knowledge articles
7. Search & discover:
   - Search the global library of published KBs and open items for reading or editing (if you are the owner).
8. Use the Insight Chat to ask questions that are answered from published content.
9. View or remove past chat sessions in the sidebar.

**Current Capabilities (what works today)**

- **End-to-end demo flow:** Upload → extract → draft → edit → save → publish (fully functional via the Streamlit demo).
- **Multi-format extraction:** Handles text extraction from common business formats (PDF, DOCX, PPTX, plain text, and supported images).
 - **Draft generation & approval (LLM):** The system produces an editable draft (generated by an LLM) and supports manual approval/publish.
- **Publishing triggers semantic indexing:** When an article is published it is added to an internal vector index so the chat can retrieve relevant sections.
- **Interactive web UI for business users:** A Streamlit-based interface provides the full user journey with clear controls for upload, editing, publishing, and chat.
 - **Insight Chat (LLM):** Returns answers grounded in retrieved knowledge sections and expanded by an LLM when configured.
- **User-level chat history:** Conversations are persisted per user and can be deleted.
- **Asset handling:** Upload and insert images into articles; stored assets are served from the application.
 - **Edit saved KBs:** Users can open and edit knowledge bases they created; edits can be saved and re-published.
 - **Search published KBs:** The UI supports browsing and searching the global published KB list to discover relevant content.

**Business Value / Benefits**

- **Faster content production:** Converts documents into review-ready drafts, reducing authoring time.
- **Consistent knowledge assets:** Standardizes tone and structure across articles for higher reuse and trust.
- **Improved customer & employee support:** Insight Chat surfaces accurate answers based on approved content, reducing mean time to answer.
- **Audit-friendly:** Human review remains central — drafts are reviewed before publishing, supporting compliance and quality control.
- **Reusable library:** Published knowledge becomes a searchable corporate asset that can be surfaced across teams.

**Future Enhancement Possibilities**

- **Multi-file knowledge generation:** Currently, the platform processes only one file at a time. Future versions will support uploading and processing multiple documents together to generate a unified knowledge article.
- **Image and visual content extraction:** At present, the system extracts only textual content from PDFs and Word documents. Future enhancements will enable extraction and understanding of images, screenshots, diagrams, tables, and embedded visual content inside documents.
- **Enhanced frontend experience:** Improve the UI/UX with a more intuitive dashboard, better navigation, cleaner article viewing, richer previews, drag-and-drop uploads, and a more user-friendly workflow.
- **Role-based access and approvals:** Introduce admin/reviewer workflows with approval stages for publishing enterprise knowledge articles.
- **Enterprise integrations:** Integrate with platforms such as SharePoint, ServiceNow.

**Notes & Requirements (short)**

 - The product is a working prototype intended for demos and hackathons. It includes a business-facing web UI and a REST API for integrations.
 - The Insight Chat and the automated knowledge-drafting feature both call an external LLM (the code uses OpenRouter by default). Set the `OPENROUTER_API_KEY` environment variable in deployment to enable generative responses. The LLM provider and model can be configured in the application settings or environment.

