from pathlib import Path

# MCP 서버 설정 — 로컬 파일시스템 접근용 설정 블록
# MCP server configuration for filesystem access
mcp_config = {
    'filesystem': {
        # npx 명령어를 통해 MCP 파일시스템 서버를 실행 (run the MCP filesystem server via npx)
        'command': 'npx',
        'args': [
            '-y',  # 필요한 경우 자동 설치 (auto-install if needed)
            '@modelcontextprotocol/server-filesystem',  # MCP 파일시스템 서버 패키지
            str(Path(__file__).parent / 'mcp-sample-files')  # 연구 문서가 위치한 로컬 경로 (path to research documents)
        ],
        # 표준 입출력(stdio)을 통해 LangChain ↔ MCP 서버 간 통신 수행
        # communication between LangChain and MCP server via stdin/stdout
        'transport': 'stdio'  # communication via stdin/stdout
    }
}
