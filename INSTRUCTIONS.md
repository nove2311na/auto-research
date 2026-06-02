# Hướng dẫn Setup & Khởi chạy Swarm cho người mới (Non-tech)

Tài liệu này hướng dẫn bạn từng bước cực kỳ đơn giản để cài đặt và chạy hệ thống nghiên cứu tự động trên bất kỳ máy tính mới nào (Windows, macOS hoặc Linux).

---

## Bước 1: Cài đặt Python & uv (Quản lý môi trường)

Hệ thống này chạy hoàn toàn bằng ngôn ngữ Python. Để quản lý các gói thư viện nhanh và ổn định, chúng ta sử dụng một công cụ tên là `uv`.

### Trên Windows (PowerShell):
Mở PowerShell và chạy lệnh sau để cài đặt `uv`:
```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Trên macOS / Linux:
Mở Terminal và chạy lệnh sau để cài đặt `uv`:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Bước 2: Cài đặt công cụ điều phối `hcom`

`hcom` là ứng dụng giúp các Agent liên lạc và làm việc cùng nhau.

### Trên Windows:
Bạn tải tệp tin chạy được (`hcom.exe`) trực tiếp từ trang chính thức:
1. Vào đường link: [hcom Releases](https://github.com/aannoo/hcom/releases)
2. Tải phiên bản dành cho Windows (ví dụ: `hcom-x86_64-pc-windows-msvc.zip`).
3. Giải nén và copy tệp `hcom.exe` vào thư mục của dự án (hoặc thêm vào PATH hệ thống nếu bạn biết cách).

### Trên macOS (sử dụng Homebrew):
Chạy lệnh sau trong Terminal:
```bash
brew install aannoo/hcom/hcom
```

### Trên Linux hoặc macOS (cài qua Script):
Chạy lệnh sau trong Terminal:
```bash
curl --proto '=https' --sv1.2 -LsSf https://github.com/aannoo/hcom/releases/download/v0.7.12/hcom-installer.sh | sh
```

---

## Bước 3: Thiết lập khóa môi trường (API Key)

Hệ thống cần API Key để giao tiếp với AI.

1. Bạn tìm tệp tin tên là `.env.example` ở thư mục dự án.
2. Tạo một bản sao của nó và đổi tên thành `.env` (hoặc tạo file mới đặt tên là `.env`).
3. Mở file `.env` bằng Notepad hoặc Text Editor bất kỳ và điền key của bạn:
   ```env
   ANTHROPIC_AUTH_TOKEN=your-api-key-here
   ```
   *(Thay thế `your-api-key-here` bằng mã khóa Claude của bạn)*

---

## Bước 4: Tự động cài đặt thư viện cho dự án

Sau khi hoàn thành các bước trên, bạn mở Terminal/PowerShell tại thư mục dự án và chạy lệnh duy nhất sau:
```bash
uv sync
```
*Lệnh này sẽ tự động tạo một môi trường Python cô lập trong dự án và tải toàn bộ các gói phần mềm cần thiết mà không làm ảnh hưởng đến máy tính của bạn.*

---

## Bước 5: Cách chạy Swarm 8 Agent

Thay vì sử dụng các lệnh shell phức tạp, bây giờ bạn chỉ cần chạy trực tiếp qua Python.

### 1. Khởi động Swarm (Mở các Agent làm việc)
Chạy lệnh sau:
```bash
python scripts/launch.py
```
*(Nếu bạn dùng macOS/Linux hoặc Git Bash, bạn vẫn có thể chạy `./scripts/launch.sh` nếu muốn).*

### 2. Gửi lệnh kích hoạt (Chỉ cần chạy 1 lần sau khi mở launch)
Mở một cửa sổ Terminal/PowerShell mới tại thư mục dự án và chạy:
```bash
python scripts/kickoff.py
```

### 3. Gửi tài liệu nghiên cứu (Bắt đầu chạy pipeline)
Để gửi một tài liệu hoặc chủ đề nghiên cứu, chạy lệnh sau:
```bash
python scripts/run_pipeline.py "Chủ đề bạn muốn nghiên cứu hoặc đường dẫn tới file"
```
*Ví dụ:*
```bash
python scripts/run_pipeline.py "Quantum error correction 2026"
```

### 4. Xem bảng trạng thái công việc (TUI Dashboard)
Để xem các Agent đang thảo luận và xử lý đến bước nào, chạy lệnh:
```bash
python scripts/attach_tui.py
```

### 5. Kiểm tra kết quả
Kết quả nghiên cứu hoàn chỉnh (dưới dạng file văn bản Markdown đẹp mắt và tệp tin JSON cấu trúc) sẽ được xuất ra tại thư mục:
`outputs/<mã_kết_quả>/05_format/v1.md`
