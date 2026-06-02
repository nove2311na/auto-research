# Movable Repo Layout Tips

Pack: `new-claude-repo`

Ghi chú này dành cho lúc vừa vibe code vừa học cách tổ chức repo sao cho sau này có thể đổi layout, move folder/file, hoặc gom code vào `src/` mà không làm vỡ vận hành.

## 1. Tư duy chính: move implementation, giữ public surface

Muốn move file thoải mái thì repo cần phân biệt rõ:

- **Implementation path**: nơi code thật đang sống. Ví dụ: `src/research_pipeline/tools/validator.py`.
- **Public surface**: command/import/path mà người dùng, agent, script, docs đang gọi. Ví dụ: `python scripts/run_pipeline.py`, `python -m tools.validator`, `from gates.output_gates import ...`.

Khi refactor layout, ưu tiên giữ public surface ổn định. Code thật có thể move, nhưng wrapper/shim vẫn giữ lệnh cũ chạy được.

## 2. Đừng rải path logic khắp repo

Tránh pattern này trong nhiều file:

```python
REPO = Path(__file__).resolve().parents[1]
OUTPUTS = REPO / "outputs"
```

Vì khi move file sang folder sâu hơn, `parents[1]` đổi nghĩa ngay.

Nên có một file path resolver duy nhất:

```python
# src/research_pipeline/paths.py
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PACKAGE_ROOT.parent
REPO_ROOT = SRC_ROOT.parent

OUTPUTS = REPO_ROOT / "outputs"
SCHEMAS = REPO_ROOT / "schemas"
HCOM_DIR = REPO_ROOT / ".hcom"
```

Sau đó mọi module import từ đó:

```python
from research_pipeline.paths import OUTPUTS, SCHEMAS, REPO_ROOT
```

## 3. Root scripts nên là wrapper, không phải implementation

Command người dùng hay nhớ nên được giữ cố định:

```cmd
python scripts\run_pipeline.py ...
```

Nhưng file đó chỉ nên làm nhiệm vụ bootstrap:

```python
from _bootstrap import run_module

run_module("research_pipeline.cli.run_pipeline")
```

Code thật nằm trong:

```text
src/research_pipeline/cli/run_pipeline.py
```

Lợi ích: sau này move implementation tiếp vẫn không đổi command.

## 4. Package import cho code mới, shim cho code cũ

Code mới nên dùng import rõ theo package:

```python
from research_pipeline.tools.validator import validate_artifact
```

Không nên tiếp tục viết trong code mới:

```python
from tools.validator import validate_artifact
```

Nhưng để không phá agent prompt hoặc script cũ, có thể giữ root `tools/validator.py` làm shim:

```python
from research_pipeline.tools.validator import *
```

Quy tắc thực dụng:

- Code mới: dùng `research_pipeline.*`.
- Code cũ/agent prompts: cho phép tiếp tục dùng `tools.*` hoặc `gates.*` nhờ shim.

## 5. Move theo hai phase

Đừng vừa move file, vừa đổi behavior, vừa sửa logic business trong cùng một bước lớn.

Flow an toàn:

1. Thêm `paths.py`.
2. Thêm wrapper/shim.
3. Chạy validation.
4. Move implementation vào `src/`.
5. Update imports.
6. Chạy validation lại.
7. Chỉ cleanup shim sau khi chắc chắn không còn ai gọi path cũ.

Nếu làm đúng, mỗi phase đều có thể debug độc lập.

## 6. Luôn audit reference trước và sau khi move

Trước khi move:

```cmd
rg -n "from tools|from gates|tools/|gates/|Path\(__file__\)\.resolve\(\)\.parents"
```

Sau khi move:

```cmd
rg -n "from tools|from gates|tools/|gates/|Path\(__file__\)\.resolve\(\)\.parents" src scripts tools gates
```

Không phải mọi hit đều sai. Ví dụ shim có thể còn `from tools._compat`. Nhưng audit giúp biết chính xác còn dependency cũ ở đâu.

## 7. Đừng move runtime anchors nếu chưa thật sự cần

Một số path nên giữ ổn định ở root vì nhiều tool, agent, hoặc runtime state phụ thuộc vào nó:

- `pipeline.json`
- `schemas/`
- `.claude/`
- `.hcom/`
- `inputs/`
- `outputs/`
- `.docs/`
- `evals/`
- `observability/`

Có thể move sau, nhưng đó là migration riêng. Đừng gom tất cả vào `src/` chỉ vì nhìn repo gọn hơn.

Nguyên tắc: `src/` dành cho code importable. Runtime data và contract files nên ở root nếu hệ sinh thái đang kỳ vọng như vậy.

## 8. Git move và move log

Nếu file đã tracked bởi git, ưu tiên:

```cmd
git mv old_path new_path
```

Nếu dùng tool/patch để move, kiểm tra lại:

```cmd
git status --short
git diff --stat
```

Với reorg lớn, nên có move log đơn giản:

```text
MOVED|old_path|new_path|reason
```

Nó giúp nhớ mình đã move gì, vì sao move, và rollback dễ hơn.

## 9. Validation tối thiểu sau layout refactor

Sau khi đổi layout, nên chạy:

```cmd
python -m py_compile ...
python scripts\validate_specs.py
python scripts\smoke_v2.py
python -m tools.artifact_io list smokev200 03_analyze
python scripts\status.py
```

Ý nghĩa:

- `py_compile`: bắt syntax/import lỗi cơ bản.
- `validate_specs`: kiểm tra agent specs, skill specs, schemas, helper paths.
- `smoke_v2`: kiểm tra pipeline artifact/manifest/validator end-to-end.
- `python -m tools...`: kiểm tra compatibility shim.
- `status.py`: kiểm tra wrapper script + hcom path.

## 10. Vụ Python bị sandbox chặn

Lỗi kiểu này:

```text
windows sandbox: spawn setup refresh
```

thường là lỗi môi trường Codex sandbox, không nhất thiết là lỗi repo.

Cách xử lý thực tế:

- Thử lại bằng script wrapper thật, ví dụ `python scripts\validate_specs.py`.
- Tránh `python -c` nếu không cần, vì dạng này hay bị sandbox chặn.
- Nếu command quan trọng vẫn bị chặn, chạy lại với quyền escalated trong Codex.
- Nếu command cần dùng nhiều lần, xin approve prefix rule cho command đó.
- Phân biệt rõ: user chạy trực tiếp trong terminal local thường không bị sandbox Codex.

Trong lần refactor này:

- Sandbox chặn một số lệnh dạng `python -m ...`, `python -c ...`, và `python scripts\status.py`.
- Khi chạy ngoài sandbox với approval, các lệnh đó pass.
- Vì vậy đây là sandbox/process-spawn issue, không phải lỗi path của repo.

## 11. Checklist nhanh trước khi move folder

```text
[ ] Có path resolver trung tâm chưa?
[ ] Public commands có wrapper chưa?
[ ] Import mới đã dùng package path chưa?
[ ] Path cũ có shim tạm chưa?
[ ] Runtime anchors có được giữ nguyên không?
[ ] Đã rg toàn repo trước khi move chưa?
[ ] Đã chạy smoke/validation sau khi move chưa?
[ ] Đã ghi note/version doc cho lần reorg chưa?
```

## 12. Mental model

Repo dễ move khi có 3 lớp:

```text
User/Agent Contract
  scripts/*.py
  tools/*.py
  gates/*.py
  pipeline.json
  schemas/

Implementation
  src/research_pipeline/...

Runtime State
  inputs/
  outputs/
  .hcom/
  observability/
```

Khi muốn dọn repo, move lớp **Implementation** trước. Đừng động mạnh vào **Contract** và **Runtime State** nếu chưa có migration riêng.
