import re
import json
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm
from src.db import save, findOne
from src.settings import settings
from src.models import DiaryItem
from save_image import save_graph_image

# ―――――――――――――――――――――――――― [ tool 및 유틸리티 정의 ] ――――――――――――――――――――――――――――――――――

@tool
async def save_diary(name: str, title: str, content: str) -> str:
  """
  새로운 일기를 DB에 저장합니다. (Writer 에이전트용)
  - name: 작성자 이름
  - title: 일기 제목
  - content: 일기 내용
  """
  sql = "INSERT INTO diaries (name, title, content, regDate) VALUES (?, ?, ?, NOW())"
  params = (name, title, content)
  result = save(sql, params)
  if result:
    return "일기가 성공적으로 저장되었습니다."
  else:
    return "일기 저장에 실패했습니다."

@tool
async def manage_diary(action: str, target: str, title: str = None, content: str = None) -> str:
  """
  일기를 수정하거나 삭제(숨김)합니다. (Manager 에이전트용)
  - action: 'update' 또는 'delete'
  - target : 게시물 번호(ID) 또는 제목(Title)
  """
  if target.isdigit():
    condition = "id = ?"
    target_val = int(target)
  else:
    condition = "title = ?"
    target_val = target
  
  if action == 'delete':
    sql = f"UPDATE diaries SET useYn = '1' WHERE {condition}"
    params = (target_val,)
    result = save(sql, params)
    if result:
      return f"'{target}' 일기가 성공적으로 삭제되었습니다."
    else:
      return "삭제에 실패했습니다."

  elif action == 'update':
    if not title or not content:
      return "수정을 위해서는 새로운 제목과 내용이 필요합니다."
    sql = f"UPDATE diaries SET title = ?, content = ? WHERE {condition}"
    params = (title, content, target_val)
    result = save(sql, params)
    if result:
      return f"'{target}' 일기가 성공적으로 수정되었습니다."
    else:
      return "수정에 실패했습니다."

# @tool
# async def update_diary(id: int, title: str, content: str) -> str:
#   """"
#   특정 ID의 일기 제목과 내용을 수정합니다.
#   - id : 수정할 일기의 번호(ID)
#   - title : 새 제목
#   - content : 새 내용
#   """
#   sql = "UPDATE diaries SET title = ?, content = ? WHERE id = ?"
#   params = (title, content, id)
#   result = save(sql, params)
#   if result:
#     return "일기가 성공적으로 수정되었습니다."
#   else:
#     return "일기 수정에 실패했습니다."

# @tool
# async def delete_diary(id: int) -> str:
#   """
#   특정 ID의 일기를 삭제(숨김) 처리합니다.
#   - id : 삭제(숨김)할 일기의 번호 (ID)
#   """
#   sql = "UPDATE diaries SET useYn = '1' WHERE id = ?"
#   params = (id,)
#   result = save(sql, params)
#   if result:
#     return f"{id}번 일기가 성공적으로 삭제되었습니다."
#   else:
#     return f"{id}번 일기 삭제에 실패했습니다."

def extract_json(text: str) -> dict:
  match = re.search(r"(\{.*\})", text, re.DOTALL)
  if match:
    return json.loads(match.group(1))
  return json.loads(text)

def get_id_by_title(title: str) -> int:
  """
  제목으로 일기의 ID를 조회합니다.
  - title : 일기 제목
  """
  sql = "SELECT id FROM diaries WHERE title = ? AND useYn = '0' LIMIT 1"
  params = (title,)
  result = findOne(sql, params)
  if result:
    return result["id"]
  else:
    return None

# ―――――――――――――――――――――――――――――― [ 에이전트 생성 ] ―――――――――――――――――――――――――――――――――――――

def diary_swarm():
  llm = ChatOllama(
    model=settings.ollama_model_name,
    base_url=settings.ollama_base_url,
    temperature=0
  )

  # -------------------------- [ 저장 에이전트 (Writer)] -------------------------------
  writer_agent = create_react_agent(
    llm,
    [save_diary, create_handoff_tool(agent_name="Manager", description="일기를 수정하거나 삭제해야 하는 경우")],
    prompt="""
      당신은 일기 저장 로봇입니다. 인사말이나 부연 설명은 절대로 하지 마십시오.
            
      [수행 규칙]
      1. 사용자가 일기 내용을 말하면, 내용에 어울리는 '제목'을 당신이 스스로 요약하여 추출하십시오.
      2. 추출된 제목과 내용을 바탕으로 즉시 'save_diary' 도구를 호출하여 저장하십시오.
      3. 저장이 완료되면 오직 결과 JSON만 출력하십시오. 다른 텍스트는 금지입니다.
      4. 사용자가 구체적인 정보를 주지 않아도, 입력된 문장을 기반으로 최선의 제목을 만드십시오.
      5. 사용자가 수정/삭제를 요구하면 지체없이 'manager_agent'에게 전달하세요. 

      JSON 형식: {"name": "작성자", "title": "추출된 제목", "content": "내용"} 
    """,
    name="Writer"
  )

  # -------------------------- [ 수정/삭제 에이전트 (Manager)] -------------------------------
  manager_agent = create_react_agent(
    llm,
    [manage_diary, create_handoff_tool(agent_name="Writer", description="새로운 일기를 작성하거나 저장해야 하는 경우")],
    prompt="""
      당신은 일기 관리 로봇입니다. 인사말이나 부연 설명은 절대로 하지 마십시오.
      
      [수행 규칙]
      1. 사용자가 수정 혹은 삭제를 원하면 'manage_diary'를 즉시 호출하십시오.
      2. 작업 완료 후에는 오직 다음 JSON만 출력하십시오.
      JSON 형식: {"name": "시스템", "title": "알림", "content": "처리 결과 메시지"}
      3. 사용자가 새로운 일기를 작성하면 지체없이 'writer_agent'에게 전달하세요. 
    """,
    name="Manager"
  )

  workflow = create_swarm([writer_agent, manager_agent], default_active_agent="Writer")
  # return workflow.compile()

  compiled_graph = workflow.compile()
  save_graph_image(compiled_graph)
  return compiled_graph

diary_agent = diary_swarm()