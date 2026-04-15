from pydantic import BaseModel, Field

# ―――――――――――――――――――――――――――― [ 데이터 모델 정의 ] ――――――――――――――――――――――――――――――――――――

class DiaryRequest(BaseModel):
  input: str

class DiaryItem(BaseModel):
  name: str = Field(description="일기 작성자의 이름")
  title: str = Field(description="일기 제목")
  content: str = Field(description="일기 본문 내용")

class DiaryResponse(BaseModel):
  status: str
  data: DiaryItem