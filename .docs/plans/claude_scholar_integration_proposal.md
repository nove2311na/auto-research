# Đề xuất Nâng cấp Hệ thống Auto-Research
**Dựa trên các bài học từ dự án `claude-scholar-main`**

**Ngày tạo:** 2026-06-02
**Mục tiêu:** Cải tiến pipeline `auto-research` hiện tại bằng cách áp dụng các design pattern, công cụ và quy trình làm việc tiên tiến từ `claude-scholar-main`, nhằm biến hệ thống thành một trợ lý nghiên cứu học thuật tự động, đáng tin cậy và có khả năng tích hợp cao.

---

## 1. Tích hợp Quản lý Tài liệu với Zotero (MCP)
**Vấn đề:** Hiện tại, bước `01-ingest` và agent `ingestor` có thể đang xử lý tài liệu một cách rời rạc, thiếu metadata chuẩn xác.
**Giải pháp đề xuất:** 
- Tích hợp Zotero Model Context Protocol (MCP) vào agent `ingestor`.
- **Hành động cụ thể:** Cung cấp cho `ingestor` các công cụ để tự động tạo Collection trên Zotero dựa trên topic, tra cứu metadata từ DOI/arXiv, tự động loại bỏ trùng lặp (deduplication) và trích xuất file `.bib` (BibTeX) chuẩn.
- **Lợi ích:** Đảm bảo mọi tài liệu đầu vào đều có trích dẫn chuẩn, dễ dàng quản lý tham khảo trong các bước sau.

## 2. Áp dụng Mô hình "Planning with Files" (Lưu trữ Trạng thái Lên Ổ đĩa)
**Vấn đề:** Agent `orchestrator` hoặc các quy trình dài dễ bị mất ngữ cảnh (context window) hoặc xảy ra ảo giác nếu chỉ lưu kế hoạch trong bộ nhớ của LLM.
**Giải pháp đề xuất:** 
- Áp dụng pattern `planning-with-files` từ `claude-scholar`.
- **Hành động cụ thể:** Bắt buộc hệ thống tạo và cập nhật 3 file cốt lõi cho mỗi task phức tạp:
  1. `task_plan.md`: Chứa danh sách các bước (checkbox) và trạng thái hiện tại.
  2. `notes.md`: Lưu trữ các phát hiện và ngữ cảnh trung gian.
  3. `[deliverable].md`: File kết quả cuối cùng.
- **Lợi ích:** `orchestrator` có thể dễ dàng đọc lại tiến độ từ ổ đĩa, cho phép pipeline tạm dừng và tiếp tục (resume) mà không mất thông tin.

## 3. Thiết lập Cơ chế Cổng Kiểm duyệt Bằng Chứng (Evidence-Gated Workflow)
**Vấn đề:** Tránh tình trạng AI tự suy diễn (hallucinate) kết quả ở bước `04-synthesize` mà không có căn cứ từ dữ liệu trích xuất.
**Giải pháp đề xuất:** 
- Xây dựng "Research Contract" (Hợp đồng nghiên cứu).
- **Hành động cụ thể:** Nâng cấp các file trong thư mục `gates/` (ví dụ: `output_gates.py`, `implementation_gates.py`) để chặn quá trình phân tích/tổng hợp nếu không có đủ "bằng chứng cứng" (ví dụ: trích dẫn rõ ràng từ ít nhất N nguồn hợp lệ đã qua bước `extract`).
- **Lợi ích:** Nâng cao độ tin cậy và tính xác thực học thuật của toàn bộ pipeline.

## 4. Tự động Tạo Bảng & Biểu đồ Chuẩn Xuất Bản
**Vấn đề:** Hiện tại pipeline chủ yếu xử lý văn bản (text/markdown), thiếu các công cụ trực quan hóa dữ liệu.
**Giải pháp đề xuất:** 
- Lấy cảm hứng từ `publication-chart-skill` (dùng `pubfig` và `pubtab`).
- **Hành động cụ thể:** Thêm một module (ví dụ: `07-visualize`) hoặc nâng cấp agent `formatter`. Giao nhiệm vụ cho agent tự động sinh mã Python (dùng matplotlib/seaborn với template học thuật) để xuất ra file PDF biểu đồ hoặc LaTeX tables từ dữ liệu đã phân tích.
- **Lợi ích:** Tạo ra báo cáo toàn diện hơn, sẵn sàng cho việc đưa vào bài báo học thuật.

## 5. Tổ chức Đầu ra Thành Mạng Lưới Kiến Thức Obsidian (Knowledge Base)
**Vấn đề:** Output hiện tại (ví dụ: `learnings.md`) có thể là các văn bản phẳng, khó kết nối và tra cứu về sau.
**Giải pháp đề xuất:** 
- Áp dụng chuẩn Obsidian Project KB.
- **Hành động cụ thể:** Chuẩn hóa đầu ra của `extractor` và `synthesizer` thành định dạng Markdown hỗ trợ Obsidian:
  - Thêm YAML frontmatter (metadata) rõ ràng.
  - Phân loại bằng tags.
  - Sử dụng Wikilinks (`[[Tên Khái Niệm]]`) để liên kết các ý tưởng, bài báo với nhau.
- **Lợi ích:** Tạo ra một "Graph view" tự nhiên, giúp người dùng duyệt và quản lý tri thức theo mạng lưới.

## 6. Nâng Cấp Agent `critic` Thành "Reviewer Phản Biện"
**Vấn đề:** Cần đảm bảo kết quả đầu ra có lập luận chặt chẽ, chống lại các lỗ hổng về phương pháp luận.
**Giải pháp đề xuất:** 
- Xây dựng cơ chế "Self-Rebuttal" tương tự `paper-self-review` và `rebuttal-writer`.
- **Hành động cụ thể:** Trang bị cho agent `critic` một prompt chuyên biệt đóng vai trò như một "Reviewer hội nghị khó tính". `critic` sẽ tấn công vào logic, phương pháp và điểm yếu trong bản nháp của `synthesizer`. Sau đó, `orchestrator` phải yêu cầu `researcher` hoặc `analyzer` bổ sung bằng chứng để giải quyết các lời phê bình này trước khi chốt kết quả.
- **Lợi ích:** Đẩy cao tiêu chuẩn học thuật và tính thuyết phục của tài liệu đầu ra.

## 7. Tinh Chỉnh Phong Cách Viết Chuyên Biệt (Targeted Expression Skills)
**Vấn đề:** Văn bản do AI tạo ra thường có văn phong dễ đoán, sáo rỗng hoặc quá rườm rà.
**Giải pháp đề xuất:** 
- Áp dụng các quy tắc "conclusion-first" (đưa kết luận lên đầu) và "anti-AI writing".
- **Hành động cụ thể:** Cập nhật file `.claude/skills/05-format/SKILL.md` hoặc thêm một skill mới như `expression-skill`. Yêu cầu agent `formatter` dọn dẹp các cụm từ AI thông dụng, sử dụng cấu trúc lập luận súc tích, đi thẳng vào vấn đề giống phong cách báo Nature/Science.
- **Lợi ích:** Tạo ra văn bản tự nhiên, chuyên nghiệp và có giá trị đọc cao hơn, tiết kiệm thời gian chỉnh sửa thủ công.

---
**Các Bước Tiếp Theo (Action Items):**
1. Review đề xuất này và chọn ra 1-2 tính năng ưu tiên (ví dụ: Zotero MCP và Planning with Files) để triển khai trong Sprint tới.
2. Thiết lập Zotero MCP server nếu chưa có.
3. Cập nhật prompt/system message của `orchestrator` để tuân thủ pattern "Planning with Files".
