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
            
        if lower_path.endswith('.json'):
            if 'package.json' in lower_path:
                categorized["Process"].append(path)
            else:
                categorized["Data"].append(path)
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
    중요: 하나의 레포지토리에 있는 모든 데이터를 생략되는 것 없이 최대한 많이 추출해서 응답해야 해.
    
    비즈니스 레이어 구조는 다음 세 단계 계층 구조로 이루어져 있어:
    1. FOREST (도메인 또는 패키지 단위)
    2. TREE (클래스 또는 파일 단위) - 상위 FOREST 요소를 부모로 가짐
    3. RING (메서드 또는 API 엔드포인트 단위) - 상위 TREE 요소를 부모로 가짐

    반드시 다음 JSON 배열 형태로만 응답해. 각 객체는 다음 키로만 구성되어야 해:
    temp_id, parent_temp_id, name, element_type, description, file_path, api_method, api_url

    - temp_id: 해당 요소의 임시 고유 ID (예: "1", "2", "3" 등 문자열)
    - parent_temp_id: 부모 요소의 임시 고유 ID (상위 FOREST가 없는 FOREST 요소는 null, TREE 요소는 부모 FOREST의 temp_id, RING 요소는 부모 TREE의 temp_id)

    [
      {
        "temp_id": "1",
        "parent_temp_id": null,
        "name": "User Domain",
        "element_type": "FOREST",
        "description": "유저 관련 비즈니스 도메인",
        "file_path": null,
        "api_method": null,
        "api_url": null
      },
      {
        "temp_id": "2",
        "parent_temp_id": "1",
        "name": "UserService",
        "element_type": "TREE",
        "description": "유저 관련 핵심 비즈니스 로직 처리 클래스",
        "file_path": "src/main/java/com/vector/onboarding/domain/user/UserService.java",
        "api_method": null,
        "api_url": null
      },
      {
        "temp_id": "3",
        "parent_temp_id": "2",
        "name": "createUser",
        "element_type": "RING",
        "description": "새로운 유저 정보 생성 및 저장 메서드",
        "file_path": "src/main/java/com/vector/onboarding/domain/user/UserService.java",
        "api_method": "POST",
        "api_url": "/api/v1/users"
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
    중요: 하나의 레포지토리에 있는 모든 데이터를 생략되는 것 없이 최대한 많이 추출해서 응답해야 해.
    반드시 다음 JSON 배열 형태로만 응답해. 각 객체는 다음 열로만 구성되어야 해:
    repo_name, file_path, space_id, created_at, element_type, name, description, extra_info

    - element_type: "ROUTING", "DESIGN_TOKEN", "COMPONENT" 중 하나로 분류
    - extra_info: 해당 요소와 관련된 추가 정보 (라우팅 경로, 컴포넌트 Props, 색상 코드 등)

    [
      {
        "repo_name": "레포지토리 이름",
        "file_path": "해당 파일 경로",
        "space_id": null,
        "created_at": "현재 시간(ISO 8601)",
        "element_type": "ROUTING",
        "name": "Login",
        "description": "사용자 로그인 페이지 컴포넌트",
        "extra_info": "경로: /login"
      },
      {
        "repo_name": "레포지토리 이름",
        "file_path": "해당 파일 경로",
        "space_id": null,
        "created_at": "현재 시간(ISO 8601)",
        "element_type": "COMPONENT",
        "name": "Button",
        "description": "재사용 가능한 UI 버튼",
        "extra_info": "Props: size, color, onClick"
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

def analyze_data_view(repo_name: str, file_paths: list) -> list:
    """
    Data View용 파일 경로 리스트를 받아, Data의 열 구조에 맞게 반환합니다.
    LLM 분석 없이 파일 경로를 기반으로 목록을 생성합니다.
    """
    import datetime
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    results = []
    for path in file_paths:
        results.append({
            "repo_name": repo_name,
            "file_path": path,
            "file_name": os.path.basename(path),
            "space_id": None,
            "created_at": now_str
        })

    logger.info(f"[Data View] '{repo_name}' 파일 변환 완료: 총 {len(results)}건")
    return results

def analyze_process_view(repo_name, files_content_str):
    system_prompt = """
    너는 DevOps 엔지니어야. CI/CD 파이프라인, Docker, 인프라 설정 파일들을 분석하여 파이프라인 흐름도를 그려줘.
    중요: 하나의 레포지토리에 있는 모든 데이터를 생략되는 것 없이 최대한 많이 추출해서 응답해야 해.
    반드시 다음 JSON 배열 형태로 응답해. 각 객체는 다음 열로만 구성되어야 해:
    repo_name, file_path, space_id, created_at, element_type, name, description, tech_stack, env_vars

    - element_type: "STEP" 으로 고정 (각 파이프라인 단계를 의미함)

    [
      {
        "repo_name": "레포지토리 이름",
        "file_path": "해당 파일 경로",
        "space_id": null,
        "created_at": "현재 시간(ISO 8601)",
        "element_type": "STEP",
        "name": "Build Project",
        "description": "프로젝트 빌드 단계",
        "tech_stack": "Gradle, Java 17",
        "env_vars": "None"
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