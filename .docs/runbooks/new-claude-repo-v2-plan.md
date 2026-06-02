                                                                          
  # New Claude Repo Idea Seed V2                                          
                                                                          
  ## Summary                                                              

  Tạo bản cải tiến tại .docs/runbooks/new-claude-repo-seed-v2/. Không     
  sửa, không ghi đè, không merge vào .docs/runbooks/new-claude-repo/;     
  nếu folder đích đã tồn tại thì dừng hoặc dùng suffix timestamp.         
                                                                          
  Seed mới sẽ biến prompt kiểu “tôi muốn làm việc A, việc B” thành spec   
  agentic hoàn chỉnh: agent roles, skills, tool/MCP map, workflow,        
  memory, gates, scaffold templates, và rubric tự chấm.                   
                                                                          
  ## Key Changes                                                          
                                                                          
  - Thêm “idea germination” flow: intake ý tưởng → harvest repo mẫu →     
    phân rã công việc → thiết kế agent/skill/tool matrix → scaffold plan  
    → validation report.                                                  
                                                                          
  - Tạo contract chuẩn cho seed input/output:                             
      - Input: idea, jobs_to_be_done, domain, target_runtime, stack,      
        risk_level, reference_repos, required_tools, constraints,
        success_criteria.                                                 
                                                                          
      - Output: agent_system_spec gồm agents[], skills[], tools[],        
        mcp_servers[], workflows[], memory[], gates[], scaffold_files[].  
                                                                          
  - Tạo template inventory cho agent/skill/tool:                          
      - Agent spec bắt buộc có role, trigger, allowed tools, forbidden    
        actions, input/output, stop conditions, escalation.               
                                                                          
      - Skill spec theo chuẩn SKILL.md + references/, scripts/, assets/.  
      - Tool/MCP spec có risk class, approval policy, auth requirements,  
        allowed agents.                                                   
                                                                          
  - Thêm reference index, không vendor toàn bộ repo ngoài vào bản seed.   
    Ghi distilled takeaways + links từ:                                   
      - Claude Code settings, subagents, MCP docs                         
      - Agent Skills spec và anthropics/skills                            
      - ShakaCode shared commands/agents/skills                           
      - claude-agent-starter, claude-memory-kit, claude-agents, OneWave-  
        AI/claude-skills
                                                                          
  - Thêm rubric riêng cho seed: chấm khả năng “gieo ý tưởng → ra hệ       
    agentic”, không chỉ chấm cấu trúc folder.                             
                                                                          
  ## Implementation Steps                                                 
                                                                          
  - Copy concepts từ bản gốc sang folder mới theo hướng “seed system”,    
    không sửa bản gốc.                                                    
                                                                          
  - Tạo các tài liệu chính: README, seed prompt, growth protocol, agent/  
    skill/tool matrix, MCP catalog, reference repo index, scaffold        
    output contract, quality rubric.                                      

  - Tạo template pack tối thiểu: CLAUDE.md, AGENTS.md, .claude/agents/    
    *, .claude/skills/*/SKILL.md, .mcp.json.example, agentic/knowledge,   
    agentic/memory, agentic/policies.                                     
                                                                          
  - Thêm validator nhẹ cho seed pack để kiểm tra: đủ file lõi, không      
    placeholder rỗng, có source index, có input/output contract, có       
    agent/skill/tool matrix.                                              
                                                                          
  - Trước khi viết skill/template chuyên biệt, chạy reference-learning    
    step theo rule repo: dùng npx skills add <owner/repo> cho các repo    
    phù hợp nếu network cho phép; nếu bị chặn, ghi rõ blocked và dùng     
    nguồn web đã kiểm tra.                                                
                                                                          
  ## Test Plan
                                                                          
  - Verify no original changes: git diff -- .docs/runbooks/new-claude-    
    repo.                                                                 
                                                                          
  - Verify target isolated: Test-Path .docs\runbooks\new-claude-repo-     
    seed-v2.                                                              
                                                                          
  - Run seed validator: python .docs\runbooks\new-claude-repo-seed-       
    v2\scripts\validate_seed_pack.py --target .docs\runbooks\new-claude-  
    repo-seed-v2.                                                         
                                                                          
  - Run content sanity checks with rg for unresolved placeholders like    
    TODO, TBD, fake URLs, or empty agent/skill/tool sections.             

  - Produce final comparison note: what V2 adds over original blueprint/  
    rubric/validator pack.                                                
                                                                          
  ## Assumptions                                                          
                                                                          
  - Folder đích mặc định: .docs/runbooks/new-claude-repo-seed-v2.         
  - Seed là docs + templates + validator, không phải full CLI generator.  
  - Không clone hoặc copy nguyên repo ngoài vào workspace; chỉ ghi        
    curated references và minimal derived templates.                      
                                                                          
  - Windows-first vì repo đang chạy trên PowerShell, nhưng template vẫn   
    ghi fallback macOS/Linux/WSL khi cần.                                 
                                                                          
  ## Source Links Used                                                    
                                                                          
  - Claude Code settings: https://code.claude.com/docs/ja/settings        
  - Anthropic skills repo: https://github.com/anthropics/skills
  - ShakaCode commands/skills/agents:
    https://github.com/shakacode/claude-code-commands-skills-agents       

  - Claude Memory Kit: https://github.com/awrshift/claude-memory-kit      
  - Claude Agent Starter:
    https://github.com/enc0ding/claude-agent-starter



Cách dùng
› cái v2 này dùng như nào trên ai agent cli app nào nhỉ


• V2 dùng tốt nhất trên Claude Code CLI. Lý do: output của nó là repo     
  Claude-native: CLAUDE.md, AGENTS.md, .claude/agents/, .claude/          
  skills/, .mcp.json.example, agentic/, scripts/gates/.                   
                                                                          
  Dùng kiểu này trong Claude Code:                                        
                                                                          
  Use .docs/runbooks/new-claude-repo-seed-v2 as the seed system.          
  My idea is: <ý tưởng của tôi>.                                          
  Generate an agent_system_spec first, then scaffold a new Claude-native  
  agentic repo that matches or exceeds .docs/runbooks/new-claude-repo.    
  Do not overwrite existing files. Run the seed validator and report V1   
  benchmark alignment.                                                    
                                                                          
  Nếu dùng ngay trong repo này thì chạy validate pack:                    
                                                                          
  python .docs\runbooks\new-claude-repo-seed-
  v2\scripts\validate_seed_pack.py --target .docs\runbooks\new-claude-    
  repo-seed-v2                                                            
                                                                          
  Thứ tự dùng chuẩn:                                                      
                                                                          
     v1_benchmark_contract.md, scaffold_output_contract.md.

  3. Nó tạo agent_system_spec.
  4. Nó tạo scaffold folder/repo mới bằng templates/.

  Có thể dùng trên Codex CLI hoặc Gemini CLI nữa, nhưng không native bằng 
  Claude Code. Với Codex/Gemini, V2 chỉ là docs + templates + validator để
  agent đọc và làm theo. Với Claude Code thì .claude/agents và .claude/   
  skills có thể trở thành runtime-native luôn.