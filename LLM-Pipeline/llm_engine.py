import os
import re
import logging
from pathlib import Path
from typing import Dict, Any
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# 🚀 [안정성 강화] llm_engine만 단독으로 임포트되더라도 API Key 에러가 나지 않도록 로컬 .env 로드를 추가합니다.
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types
# pyrefly: ignore [missing-import]
from supabase import create_client, Client as SupabaseClient

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_onboarding_guide(repo_name, categorized_files, simulated_rag_context=""):
    """
    이 함수는 이제 기존 레포지토리 분석 결과를 무시하고, 
    재원님의 프롬프트에 따라 Soft On-boarding Agent의 React 및 Spring Boot 뼈대 코드를 생성합니다.
    """
    
    # 1. 시스템 프롬프트: 프론트엔드와 백엔드 역할을 동시에 부여
    system_prompt = """
    너는 B2B SaaS 전문 프론트엔드 개발자이자, Spring Boot 기반의 데이터 파이프라인을 구축하는 백엔드 아키텍트야.
    현재 'Soft On-boarding Agent'의 프론트엔드(React/Vite)와 백엔드(Spring Boot) 핵심 로직을 구현해야 해.
    """

    # 2. 유저 프롬프트: 재원님이 작성하신 프롬프트 원본 + 약간의 디테일(버전, DB 등) 추가 적용
    user_prompt = """
    [Frontend 구현 요구사항]
    현재 'Soft On-boarding Agent'의 [로그인 및 팀 스페이스 온보딩] 플로우를 React(Vite)와 Tailwind CSS를 사용해 구현하려고 해.
    페이지 이동을 위해 `react-router-dom` v6를 사용하고, 아이콘은 `lucide-react`를 적용해 줘.
    디자인은 Linear, Notion처럼 화이트/그레이 톤에 모던하고 여백이 많은 스타일로 깔끔하게 구성해 줘.

    - 로그인 페이지 (LoginPage.tsx): 화면 중앙에 심플한 로고 텍스트와 함께 [Continue with GitHub] 버튼 하나만 크게 배치해 줘. (GitHub 아이콘 포함)
    - 온보딩 라우팅 페이지 (OnboardingPage.tsx): 로그인 후 팀이 없는 유저가 보는 화면이야. 화면 중앙에 예쁜 카드 UI를 배치해 줘.
      * 기본 상태 (팀 참여): '초대받은 팀 코드를 입력하세요'라는 문구와 함께 텍스트 Input, 그리고 [Join Space] 버튼을 만들어 줘.
      * 하단 토글: 그 아래에 연한 글씨로 "새로운 팀 스페이스를 구축하고 싶으신가요? [팀 생성하기]" 버튼을 만들어 줘.
    - 팀 생성 모달 또는 뷰 전환 (CreateTeamView): 위에서 [팀 생성하기]를 누르면 부드럽게 화면이 전환되며 입력창이 바뀌도록 해 줘. '분석할 GitHub 레포지토리 URL을 입력하세요' 문구와 Input, 그리고 [생성 및 분석 시작] 버튼을 만들어 줘.
    - 분석 로딩 컴포넌트 (AnalyzingLoader.tsx): [생성 및 분석 시작] 버튼을 누르면 AI가 코드를 분석한다는 느낌을 주는 세련된 로딩 화면(스피너 또는 프로그레스 바)을 띄워 줘. "AI가 레포지토리 구조와 최근 커밋 히스토리를 분석하여 4-Way View를 구축하고 있습니다..." 라는 텍스트를 포함해 줘.

    모든 상태 관리(팀 참여, 생성 전환 등)를 포함하여 작동 가능한 코드 뼈대로 작성해 줘.

    ===SPLIT===

    [Backend 구현 요구사항]
    현재 'Soft On-boarding Agent'의 [GitHub OAuth 로그인 및 팀 스페이스 분석 생성] 핵심 비즈니스 로직을 구현해야 해.
    Java 17 환경을 사용하고, 데이터베이스는 PostgreSQL 기준으로 Entity를 매핑해 줘.

    - GitHub OAuth 2.0 로그인: spring-boot-starter-oauth2-client를 활용해 GitHub 로그인을 구현하고, 성공 시 발급받은 Access Token을 DB에 유저 정보와 함께 저장해 줘. (이 토큰으로 프라이빗 레포지토리 API를 호출해야 함).
    - 팀 스페이스 참여 API (Join): 프론트에서 전달받은 teamCode를 검증하여 해당 팀에 유저를 매핑하는 엔드포인트를 만들어 줘.
    - 팀 스페이스 생성 API (Create) - ⭐️ 핵심 ⭐️: 프론트에서 GitHub Repo URL을 받으면 다음 2가지 로직을 비동기(또는 효율적으로) 처리하는 서비스 레이어를 짜 줘.
      * [로직 A: 뼈대 구축]: GitHub Git Trees API(recursive)를 호출해 파일 경로 목록을 가져온 뒤, LLM API(Google Gemini API 사용 기준)를 통해 이 파일들을 4가지 'Functional', 'Data', 'Interface', 'Process'로 분류해서 각각 테이블에 repo_name, file_path, space_id, created_at에 저장해 줘. 특히 space_id는 team code 문자열이 아닌 space id를 넣어줘야 해. LLM API 호출 부분은 서비스 레이어 뼈대만 작성해.
      * [로직 B: 히스토리 매핑]: GitHub Commits API를 호출해 해당 레포의 '최근 100개' 커밋 내역과 Diff를 가져와. 그리고 이 커밋들이 수정/생성한 파일 경로를 바탕으로, [로직 A]에서 만든 컴포넌트 노드들과 매핑하여 CommitHistory 테이블에 저장해 줘. (프론트에서 특정 노드 클릭 시 이 히스토리가 조회되어야 함).

    코드 구조는 Controller, Service, Repository(JPA) 패턴으로 깔끔하게 나누고, 외부 API(GitHub) 통신 부분은 WebClient 또는 RestTemplate을 사용하는 뼈대 코드로 작성해 줘.
    
    [중요 규칙]
    반드시 Frontend 가이드 작성이 끝난 직후, Backend 가이드를 시작하기 전에 정확히 '===SPLIT===' 이라는 텍스트를 출력해서 두 파트를 완벽하게 구분해 줘. (이 기호를 기준으로 파이썬 시스템이 파일을 쪼갤 예정이야)
    """

    print("[LLM] 재원님의 커스텀 프롬프트를 바탕으로 React 및 Spring Boot 코드를 생성 중입니다...")
    
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
        )
    )
    
    return response.text

import json

def categorize_files_with_gemini(file_paths):
    """
    파일 경로 리스트를 받아 4-Way View 카테고리로 분류합니다.
    """
    categorized = {
        "Interface": [],
        "Functional": [],
        "Data": [],
        "Process": []
    }
    
    for path in file_paths:
        lower_path = path.lower()
        if any(ignore in lower_path for ignore in ['.git/', 'node_modules/', 'venv/', '__pycache__', '.jpg', '.png', '.ico', '.svg', 'package-lock.json', 'yarn.lock']):
            continue
            
        if any(kw in lower_path for kw in ['components', 'pages', 'views', 'ui', 'styles', 'css', 'tailwind', '.jsx', '.tsx', 'router']):
            categorized["Interface"].append(path)
        elif any(kw in lower_path for kw in ['entity', 'schema', 'prisma', 'sql', 'ddl', 'models', 'migrations']):
            categorized["Data"].append(path)
        elif any(kw in lower_path for kw in ['.github', 'workflows', 'docker', 'build.gradle', 'pom.xml', 'package.json', 'Makefile', 'ci', 'cd']):
            categorized["Process"].append(path)
        elif any(kw in lower_path for kw in ['service', 'utils', 'handler', 'controller', 'api', 'logic', '.py', '.java', '.go', '.ts', '.js']):
            categorized["Functional"].append(path)
            
    return categorized

def analyze_functional_view(repo_name, files_content_str):
    system_prompt = """
    너는 시니어 백엔드 아키텍트야. 제공된 소스코드 파일들을 분석해서 비즈니스 로직과 서비스 계층이 어떻게 구성되어 있는지 분석해줘.
    FOREST (도메인 분류), TREE (클래스/파일 단위), RING (핵심 메서드/API) 계층 구조로 나누어 JSON으로 응답해.
    반드시 다음 JSON 배열 형태로만 응답해.
    [
      {
        "name": "User Domain (Forest 예시)",
        "element_type": "FOREST",
        "description": "유저 관련 비즈니스 도메인",
        "children": [
          {
            "name": "UserService.java",
            "element_type": "TREE",
            "description": "유저 비즈니스 로직 클래스",
            "file_path": "src/main/java/.../UserService.java",
            "children": [
              {
                "name": "login()",
                "element_type": "RING",
                "description": "유저 로그인 처리 메서드",
                "api_method": "POST",
                "api_url": "/api/v1/login"
              }
            ]
          }
        ]
      }
    ]
    """
    
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=f"레포지토리: {repo_name}\n\n파일 내용들:\n{files_content_str}",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2,
            response_mime_type="application/json"
        )
    )
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return []

def analyze_interface_view(repo_name, files_content_str):
    """
    LLM을 활용해 프론트엔드/UI 파일들을 분석하여 라우팅 트리, 디자인 토큰, UI 컴포넌트 목록을 반환합니다.
    """
    system_prompt = """
    너는 시니어 프론트엔드 개발자야. 제공된 프론트엔드/UI 파일들을 분석하여 라우팅 트리, 디자인 토큰, UI 컴포넌트 목록을 분석해줘.
    반드시 다음 JSON 객체 형태로만 응답해.
    {
      "routing": [ {"path": "/", "component": "Home"} ],
      "design_tokens": { "colors": ["#fff"], "fonts": ["Inter"] },
      "components": [ {"name": "Button", "description": "공통 버튼 컴포넌트"} ]
    }
    """
    
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=f"레포지토리: {repo_name}\n\n파일 내용들:\n{files_content_str}",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2,
            response_mime_type="application/json"
        )
    )
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {}

# ============================================================
# Interface Analysis Pipeline (interface_analyzer.py 통합)
# ============================================================

def _get_supabase_client() -> SupabaseClient:
    """
    환경 변수에서 Supabase URL과 KEY를 가져와 클라이언트를 초기화합니다.
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("치명적 오류: Supabase 환경 변수(SUPABASE_URL, SUPABASE_KEY)가 설정되지 않았습니다.")
        
    return create_client(supabase_url, supabase_key)

def extract_component_metadata(project_path: str) -> list:
    """
    프로젝트 경로 내의 .tsx, .jsx, .vue 파일들을 스캔하여
    @figma 및 @storybook 주석을 추출합니다.
    """
    component_metadata = []
    
    # 정규식 패턴: // @figma: url 또는 /* @figma: url */
    figma_pattern = re.compile(r'@figma:\s*(https?://[^\s]+)')
    storybook_pattern = re.compile(r'@storybook:\s*(https?://[^\s]+)')
    
    for root, dirs, files in os.walk(project_path):
        # node_modules 등 제외
        if 'node_modules' in root or '.git' in root or 'dist' in root:
            continue
            
        for file in files:
            if file.endswith(('.tsx', '.jsx', '.vue')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        figma_match = figma_pattern.search(content)
                        storybook_match = storybook_pattern.search(content)
                        
                        if figma_match or storybook_match:
                            # 파일명에서 확장자를 제외한 이름을 기본 컴포넌트 이름으로 사용
                            component_name = os.path.splitext(file)[0]
                            if component_name == 'index':
                                component_name = os.path.basename(root)
                                
                            metadata = {
                                "component_name": component_name,
                                "file_path": os.path.relpath(file_path, project_path).replace("\\", "/"),
                                "figma_url": figma_match.group(1) if figma_match else None,
                                "storybook_url": storybook_match.group(1) if storybook_match else None
                            }
                            component_metadata.append(metadata)
                except Exception as e:
                    logger.warning(f"파일 읽기 실패 {file_path}: {e}")
                    
    return component_metadata

def analyze_project_ui(project_path: str) -> Dict[str, Any]:
    """
    주어진 프로젝트 폴더를 탐색하여 라우팅 구조와 디자인 토큰을 추출합니다.
    (실제 복잡한 AI 분석 로직, 정규식, AST 파싱 등은 이 부분에 구현되며, 현재는 모킹 처리됨)
    """
    logger.info(f"프로젝트 분석 시작 (경로: {project_path})")
    
    # [가상 로직 1] 라우팅 구조 분석
    routing_data = {
        "name": "root",
        "path": "/",
        "children": [
            {
                "name": "Dashboard",
                "path": "/dashboard",
                "children": [
                    {
                        "name": "Settings",
                        "path": "/dashboard/settings",
                        "children": []
                    }
                ]
            },
            {
                "name": "Login",
                "path": "/login",
                "children": []
            }
        ]
    }
    
    # [가상 로직 2] 디자인 토큰 추출
    design_data = {
        "colors": {
            "primary": "#3B82F6",
            "secondary": "#6B7280",
            "background": "#FAFAFA"
        },
        "typography": {
            "base_font": "Inter, sans-serif"
        }
    }
    
    # 실제 주석 파싱 로직 실행
    component_metadata = extract_component_metadata(project_path)
    
    return {
        "raw_routing": routing_data,
        "raw_design": design_data,
        "component_metadata": component_metadata
    }

def format_interface_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    추출된 로우 데이터를 프론트엔드가 렌더링하기 좋은 [지정된 출력 JSON 포맷]으로 변환(정형화)합니다.
    """
    logger.info("추출된 데이터를 출력 JSON 포맷 스펙에 맞게 가공합니다.")
    
    try:
        routing_tree = raw_data.get("raw_routing", {})
        design_tokens = raw_data.get("raw_design", {})
        
        formatted_data = {
            "routing_tree": {
                "name": routing_tree.get("name", "Root"),
                "path": routing_tree.get("path", "/"),
                "children": routing_tree.get("children", [])
            },
            "design_tokens": {
                "colors": {
                    "primary": design_tokens.get("colors", {}).get("primary", "#000000"),
                    "secondary": design_tokens.get("colors", {}).get("secondary", "#FFFFFF"),
                    "background": design_tokens.get("colors", {}).get("background", "#FFFFFF")
                },
                "typography": {
                    "base_font": design_tokens.get("typography", {}).get("base_font", "sans-serif")
                }
            },
            "components": raw_data.get("component_metadata", [])
        }
        return formatted_data
    except Exception as e:
        logger.error(f"데이터 포맷팅 중 오류 발생: {str(e)}")
        raise

def save_interface_to_supabase(space_id: int, interface_data: Dict[str, Any]):
    """
    가공 완료된 JSON 데이터를 Supabase 'analysis_results' 테이블에 저장(Upsert)합니다.
    """
    logger.info(f"Supabase DB 저장 시작 (space_id: {space_id})")
    
    try:
        supabase = _get_supabase_client()
        
        data = {
            "space_id": space_id,
            "interface_view_data": interface_data
        }
        
        response = supabase.table("analysis_results").upsert(data).execute()
        
        if hasattr(response, 'error') and response.error:
             raise Exception(response.error)
             
        logger.info(f"Supabase 저장 성공. 완료된 데이터 수: {len(response.data) if response.data else 0}")
        return response
    except Exception as e:
        logger.error(f"Supabase 저장 중 예외 발생: {str(e)}")
        raise

def run_interface_analysis_pipeline(space_id: int, project_path: str):
    """
    전체 Interface 분석 파이프라인을 실행하는 오케스트레이션(메인) 함수.
    1. 프로젝트 파일 분석 및 추출
    2. 추출된 데이터 정형화
    3. 데이터베이스 저장
    """
    try:
        logger.info(f"--- Interface 분석 파이프라인 시작 (Space ID: {space_id}) ---")
        
        # 1. 프로젝트 파일 분석 및 추출
        raw_data = analyze_project_ui(project_path)
        
        # 2. 추출된 데이터 정형화
        formatted_json = format_interface_data(raw_data)
        
        # 3. 데이터베이스 저장
        save_interface_to_supabase(space_id, formatted_json)
        
        logger.info("--- Interface 분석 파이프라인 완료 ---")
        return formatted_json
        
    except Exception as e:
        logger.error(f"파이프라인 실행 중 치명적 오류 발생: {str(e)}")
        raise

def analyze_data_view(repo_name, files_content_str):
    """
    Data View용 파일 목록을 텍스트 형태로 반환합니다.
    LLM JSON 분석 없이, 파일 내용 문자열에서 파일명을 추출하여 줄바꿈으로 나열합니다.
    호출 측(SOA_LLM_Model.py)에서 repo_name, space_id와 함께 DB에 적재합니다.
    """
    file_names = []
    for line in files_content_str.split("\n"):
        line = line.strip()
        if line.startswith("--- FILE:") and line.endswith("---"):
            # "--- FILE: path/to/file.java ---" 형식에서 파일 경로 추출
            file_path = line.replace("--- FILE:", "").replace("---", "").strip()
            file_names.append(file_path)
    
    return "\n".join(file_names)

def analyze_process_view(repo_name, files_content_str):
    system_prompt = """
    너는 DevOps 엔지려야. CI/CD 파이프라인, Docker, 인프라 설정 파일들을 분석하여 파이프라인 흐름도를 그려줘.
    빌드/테스트/배포 단계, 사용 기술 스택, 환경 변수를 추출해서 JSON으로 응답해.
    반드시 다음 JSON 배열 형태로 응답해.
    [
      {
        "step": "Build",
        "description": "Gradle을 사용한 애플리케이션 빌드",
        "tech_stack": ["Gradle", "Java 17"],
        "env_vars": []
      },
      {
        "step": "Deploy",
        "description": "AWS EC2 배포",
        "tech_stack": ["AWS", "Docker"],
        "env_vars": ["AWS_ACCESS_KEY"]
      }
    ]
    """
    
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=f"레포지토리: {repo_name}\n\n파일 내용들:\n{files_content_str}",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2,
            response_mime_type="application/json"
        )
    )
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return []