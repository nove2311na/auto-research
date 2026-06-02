 Claude vừa kích hoạt 3 chế độ Agent hoàn toàn khác nhau.
Và đa số người dùng mới chỉ đang dùng chế độ đầu tiên.
1. Sub-Agent
Gõ: "use subagents"
Claude tự tạo một agent phụ, giao việc và nhận kết quả trả về.
✓ Xử lý tác vụ đơn lẻ nhanh chóng
✓ Giữ cuộc trò chuyện chính gọn gàng
✓ Phù hợp với kiểu: "Làm việc này rồi báo lại cho tôi"
2. Agent Team
Gõ: "create agent team"
Bạn tự thiết kế đội ngũ agent bằng các file role riêng biệt.
Ví dụ:
Strategist → Executor → QA
✓ Chuỗi quy trình cố định
✓ Tự động hóa công việc lặp lại mỗi ngày
✓ Rất phù hợp cho sản xuất nội dung, marketing và vận hành
3. Dynamic Workflow
Gõ: "run a workflow"
Đây là cấp độ hoàn toàn khác.
Một workflow có thể:
✓ Chạy hàng chục đến hàng trăm agent song song
✓ Kiểm tra chéo kết quả giữa các agent
✓ Lặp lại nhiều vòng cho đến khi đạt yêu cầu
Phù hợp với các tác vụ nghiên cứu, phân tích và xác minh quy mô lớn.
Quy tắc chọn nhanh:
• Sub-Agent = "Làm giúp tôi một việc."
• Agent Team = "Đi theo quy trình chuyên gia tôi đã thiết kế."
• Workflow = "Vận hành cả một hệ thống ở quy mô lớn."
Phần lớn mọi người dừng lại ở Sub-Agent.
Trong khi Agent Team và Workflow mới là nơi tạo ra lợi thế thực sự.
Nếu bạn đang dùng Claude hằng ngày, việc hiểu đúng 3 chế độ này sẽ tạo ra khác biệt rất lớn giữa "dùng AI để hỗ trợ" và "xây hệ thống AI tự vận hành".

5 Phút Học Ai Cho người Mới
01. SUB-AGENT
Claude khởi tạo một nhân viên phụ, giao một nhiệm vụ rồi nhận kết quả trả về.
Cách dùng
use subagents
Nhập vào trong prompt.
AI kiểm soát
Claude quyết định khi nào tạo, khi nào gọi và gọi theo thứ tự nào.
Khi nào thắng
Phân quyền nhanh, chạy song song khi muốn giữ luồng chat chính sạch sẽ.
Claude tạo các nhân viên trợ giúp bay (sub-agents)
Mỗi nhân viên tự trả kết quả về.
Research
Code
Docs
➡️ Main Agent quyết định trên fly.
19h
Reply

Author
5 Phút Học Ai Cho người Mới
02. ĐỘI NGŨ AGENT
Một chuỗi cố định các chuyên gia, chạy tuần tự đúng theo thứ tự bạn đặt.
Cách dùng
create agent team
Một team, một file cho mỗi vai trò.
AI kiểm soát
Bạn đặt đội hình. Claude đi theo thứ tự và chuyển tay cho mỗi chuyên gia.
Khi nào thắng
Pipeline lặp lại, vai trò chuyên gia chạy đúng mỗi lần.
Một chuỗi cố định, mỗi chuyên gia nhận việc tiếp theo
IN →
Bước 1
Chiến lược gia
⬇
Bước 2
Nhà thiết kế
⬇
Cổng – Bước 3
QA Review
⬇
Bước 4
Nhà xuất bản
→ OUT
19h
Reply

Author
5 Phút Học Ai Cho người Mới
03. LUỒNG LÀM VIỆC ĐỘNG
Một script chạy nền, phân tán công việc, lặp lại và fan-out cho đến khi xong.
Cách dùng
run a workflow
Yêu cầu Claude, nó chạy script.
AI kiểm soát
Code của bạn. Script giữ vòng lặp, điều kiện và fan-out.
Khi nào thắng
Mở rộng tới hàng chục agent, kèm các kiểm tra độc lập đáng tin cậy.
Script mã hóa vận hành, merge và lặp ở quy mô lớn
Tối đa 100 agent
Worker
Worker
Worker
Worker
Worker
➡️ Kết quả được gộp
🔄 Lặp cho đến khi xong