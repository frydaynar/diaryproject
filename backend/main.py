from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.settings import settings
from src.models import DiaryRequest, DiaryResponse
from src.agent import diary_agent, extract_json
import logging
from src.db import findAll

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_app_state(request: Request):
  return request.app.state

@asynccontextmanager
async def lifespan(app: FastAPI):
  app.state.agent_executor = diary_agent
  logger.info("Swarm Agent Session Loaded Successfully!")
  yield

app = FastAPI(title="Diary Agent API", lifespan=lifespan)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.get("/diaries")
async def get_diaries():
  sql = f"""
    SELECT 
      id, name, title, content, DATE_FORMAT(regDate, '%Y-%m-%d %H:%i') as regDate
    FROM 
      diaries
		WHERE
			useYn = '0'
    ORDER BY 
      regDate DESC
  """
  results = findAll(sql)
  return results

@app.post("/chat", response_model=DiaryResponse)
async def chat(query: DiaryRequest, state=Depends(get_app_state)):
	try:
		agent = state.agent_executor

		# 1. 세션 유지 설정 (thread_id)
		config = {"configurable": {"thread_id": "nara_diary_session"}}

		# 2. 입력 구성 (Swarm 형식)
		inputs = {"messages": [{"role": "user", "content": query.input}]}

		# 3. 에이전트 호출 (config -> 이전 대화 맥락 참조)
		result = await agent.ainvoke(inputs, config)

		# 4. 최종 메시지 추출
		last_message = result["messages"][-1]
		raw_response = last_message.content
		logger.info(f"Raw Agent Response: {raw_response}")

		# 5. 응답이 비어있는 경우 파싱에러 방지
		if not raw_response or not raw_response.strip():
			# 마지막 메시지가 도구 호출(tool_calls)을 포함하고 있는지 확인
			if hasattr(last_message, "tool_calls") and last_message.tool_calls:
				# 도구는 실행되었으나 텍스트 답변만 없는 경우 (정상 저장으로 간주)
				validated_data = {
						"name": "시스템",
						"title": "처리 완료",
						"content": "일기가 성공적으로 처리되었습니다. 타임라인을 확인하세요!"
				}
				return {"status": "success", "data": validated_data}
			else:
				# 도구 호출도 없고 내용도 없는 경우
				raw_response = '{"name": "시스템", "title": "알림", "content": "응답을 생성하지 못했습니다. 다시 시도해주세요."}'

		# 6. JSON 파싱 시도
		try:
			json_data = extract_json(raw_response)
			validated_data = {
				"name" : json_data.get("name", "시스템"),
				"title" : json_data.get("title", "알림"),
				"content" : json_data.get("content", raw_response)
			}
			return {"status": "success", "data": validated_data}
		except Exception as json_err:
			logger.error(f"JSON 파싱 에러: {json_err}")
			return {
				"status": "success",
				"data": {"name": "시스템", "title": "알림", "content": raw_response if raw_response else "작업이 완료되었습니다."}
			}
	except Exception as e:
		logger.error(f"Error: {e}")
		raise HTTPException(status_code=500, detail=str(e))


# @app.post("/chat", response_model=DiaryResponse)
# async def write_diary(query: DiaryRequest, state=Depends(get_app_state)):
# 	try:
# 		agent = state.agent_executor
# 		inputs = {"messages": [{"role": "user", "content": query.input}]}
# 		result = await agent.ainvoke(inputs)

# 		raw_response = result["messages"][-1].content
# 		logger.info(f"Raw Agent Response: {raw_response}")

# 		try:
# 			# JSON 추출
# 			json_data = extract_json(raw_response)

# 			# 필수 필드(name, title, content)가 있는지 검증 및 보정
# 			validated_data = {
# 				"name": json_data.get("name", "시스템"),
# 				"title": json_data.get("title", "알림"),
# 				"content": json_data.get("content", raw_response)
# 			}
# 			return {"status": "success", "data": validated_data}
# 		except Exception as json_err:
# 			# JSON 파싱 실패 시 (에이전트가 일반 텍스트로 대답한 경우)
# 			logger.error(f"JSON 파싱 에러: {json_err}")
# 			return {
# 				"status": "success",
# 				"data": {"name": "시스템", "title": "처리 결과", "content": raw_response}
# 			}
# 	except Exception as e:
# 		logger.error(f"Error: {e}")
# 		raise HTTPException(status_code=500, detail=str(e))